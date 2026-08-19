"""Deterministic founder-control and dilution calculations.

This module is intentionally dependency-free. It is a workpaper calculator, not
legal advice. Inputs describe the fully diluted economic denominator and the
voting universe separately so preferred and other special voting rights cannot
silently invalidate the 5.01% control objective.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

getcontext().prec = 50


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        return Fraction(int(value))
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(str(value or 0))


def _decimal(value: Fraction) -> str:
    return format(Decimal(value.numerator) / Decimal(value.denominator), ".12f").rstrip("0").rstrip(".") or "0"


@dataclass(frozen=True)
class ControlResult:
    founder_economic: Fraction
    founder_votes: Fraction
    total_votes: Fraction
    founder_voting_power: Fraction
    threshold: Fraction
    vote_floor: Fraction
    threshold_pass: bool
    voting_pass: bool
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "founder_economic_percent": _decimal(self.founder_economic * 100),
            "founder_votes": _decimal(self.founder_votes),
            "total_votes": _decimal(self.total_votes),
            "founder_voting_power_percent": _decimal(self.founder_voting_power * 100),
            "threshold_percent": _decimal(self.threshold * 100),
            "vote_floor_percent": _decimal(self.vote_floor * 100),
            "threshold_pass": self.threshold_pass,
            "voting_pass": self.voting_pass,
            "status": "pass" if self.threshold_pass and self.voting_pass and not self.failures else "fail",
            "failures": list(self.failures),
        }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]
    if payload.get("schema") not in {"glaw-founder-control/v1", "glaw-founder-control/v2"}:
        failures.append("payload schema must be glaw-founder-control/v1 or v2")
    if payload.get("denominator_basis") not in {
        "fully_diluted_economic_ownership",
        "as_converted_economic_ownership",
        "outstanding_economic_ownership",
    }:
        failures.append("denominator_basis must explicitly identify the ownership denominator")
    if not str(payload.get("founder_holder", "")).strip() and not payload.get("founder_holders"):
        failures.append("founder_holder or founder_holders is required")
    for field in ("economic", "voting"):
        rows = payload.get(field)
        if not isinstance(rows, list) or not rows:
            failures.append(f"{field} must be a non-empty explicit row list")
            continue
        seen_ids: set[str] = set()
        for idx, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                failures.append(f"{field}[{idx}] must be an object")
                continue
            if not str(row.get("holder", "")).strip():
                failures.append(f"{field}[{idx}] holder is required")
            if "shares" not in row:
                failures.append(f"{field}[{idx}] shares is required")
            else:
                try:
                    shares = _fraction(row.get("shares"))
                    if shares < 0:
                        failures.append(f"{field}[{idx}] shares cannot be negative")
                except (ValueError, ZeroDivisionError):
                    failures.append(f"{field}[{idx}] shares is not numeric")
            row_id = str(row.get("id", "")).strip()
            if row_id and row_id in seen_ids:
                failures.append(f"{field}[{idx}] duplicate row id: {row_id}")
            if row_id:
                seen_ids.add(row_id)
            if field == "voting":
                if "votes_per_share" not in row:
                    failures.append(f"voting[{idx}] votes_per_share is required; no implicit one-vote default")
                else:
                    try:
                        if _fraction(row.get("votes_per_share")) < 0:
                            failures.append(f"voting[{idx}] votes_per_share cannot be negative")
                    except (ValueError, ZeroDivisionError):
                        failures.append(f"voting[{idx}] votes_per_share is not numeric")
    return failures


def _founder_holders(payload: dict[str, Any]) -> set[str]:
    rows = payload.get("founder_holders")
    if isinstance(rows, list) and rows:
        return {str(value) for value in rows}
    return {str(payload.get("founder_holder", "Founder"))}


def calculate(payload: dict[str, Any]) -> ControlResult:
    """Calculate ownership and vote control from a normalized workpaper payload.

    ``economic`` rows contribute to the fully diluted denominator. ``voting``
    rows contribute to the voting universe. A row may contribute to both. Each
    row is ``{"holder": ..., "shares": ..., "votes_per_share": ...}``.
    """
    validation_failures = validate_payload(payload)
    economic_rows = payload.get("economic", []) if isinstance(payload.get("economic"), list) else []
    voting_rows = payload.get("voting", []) if isinstance(payload.get("voting"), list) else []
    founder_holders = _founder_holders(payload)
    threshold = _fraction(payload.get("threshold_percent", "5.01")) / 100
    vote_floor = _fraction(payload.get("vote_floor_percent", "50.1")) / 100

    economic_total = sum((_fraction(row.get("shares")) for row in economic_rows), Fraction(0))
    founder_economic_shares = sum(
        (_fraction(row.get("shares")) for row in economic_rows if str(row.get("holder")) in founder_holders),
        Fraction(0),
    )
    voting_total = Fraction(0)
    founder_votes = Fraction(0)
    for row in voting_rows:
        votes = _fraction(row.get("shares")) * _fraction(row.get("votes_per_share"))
        voting_total += votes
        if str(row.get("holder")) in founder_holders:
            founder_votes += votes

    economic_pct = founder_economic_shares / economic_total if economic_total else Fraction(0)
    voting_pct = founder_votes / voting_total if voting_total else Fraction(0)
    failures: list[str] = list(validation_failures)
    if economic_total == 0:
        failures.append("economic denominator is zero")
    if voting_total == 0:
        failures.append("voting universe is zero")
    if economic_pct < threshold:
        failures.append("founder economic ownership is below the Founder Threshold")
    if voting_pct <= vote_floor:
        failures.append("founder voting power is not greater than the required voting floor")
    return ControlResult(
        founder_economic=economic_pct,
        founder_votes=founder_votes,
        total_votes=voting_total,
        founder_voting_power=voting_pct,
        threshold=threshold,
        vote_floor=vote_floor,
        threshold_pass=economic_pct >= threshold,
        voting_pass=voting_pct > vote_floor,
        failures=tuple(failures),
    )


def minimum_multiplier(founder_percent: Any = "5.01", vote_floor_percent: Any = "50.1") -> Fraction:
    """Return the strict lower bound for M in the simple A/B model."""
    p = _fraction(founder_percent) / 100
    floor = _fraction(vote_floor_percent) / 100
    # pM/(pM + 1-p) > floor => M > floor(1-p)/(p(1-floor))
    return floor * (1 - p) / (p * (1 - floor))


def sensitivity(payload: dict[str, Any], multipliers: list[Any] | None = None) -> list[dict[str, Any]]:
    multipliers = multipliers or ["10", "20", "25", "50", "100"]
    rows = payload.get("voting", [])
    founder_holders = _founder_holders(payload)
    result: list[dict[str, Any]] = []
    for multiplier in multipliers:
        voting = []
        for row in rows:
            copy = dict(row)
            if str(copy.get("holder")) in founder_holders:
                copy["votes_per_share"] = multiplier
            voting.append(copy)
        row_payload = dict(payload)
        row_payload["voting"] = voting
        row_payload["class_b_votes_per_share"] = str(multiplier)
        result.append({"multiplier": str(multiplier), **calculate(row_payload).as_dict()})
    return result


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def ledger_digest(matter: Path) -> tuple[str, int, list[str]]:
    path = matter / "workpapers" / "founder-control-ledger.jsonl"
    if not path.exists():
        return _sha256(path) if path.exists() else hashlib.sha256(b"").hexdigest(), 0, []
    failures: list[str] = []
    rows: list[str] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            failures.append(f"ledger line {idx} is invalid JSON")
            continue
        expected = row.get("row_hash")
        copy = dict(row)
        copy.pop("row_hash", None)
        actual = _canonical_sha256(copy)
        if expected != actual:
            failures.append(f"ledger line {idx} row_hash mismatch")
        rows.append(line)
    return _sha256(path), len(rows), failures


def verify_assurance_certificate(matter: Path, root: Path | None = None) -> dict[str, Any]:
    """Verify the current founder-control certificate and all referenced hashes."""
    matter = Path(matter).resolve()
    root = Path(root or matter.parents[2]).resolve()
    certificate_path = matter / "workpapers" / "founder-control-assurance.json"
    failures: list[str] = []
    if not certificate_path.is_file():
        return {"status": "fail", "certificate": str(certificate_path), "failures": ["founder-control-assurance certificate is missing"]}
    try:
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "fail", "certificate": str(certificate_path), "failures": [f"certificate is invalid JSON: {exc}"]}
    if certificate.get("schema") != "glaw-founder-control-certificate/v1":
        failures.append("certificate schema is unsupported")
    if certificate.get("status") != "pass":
        failures.append("certificate status is not pass")
    result = certificate.get("control_result", {})
    if result.get("status") != "pass":
        failures.append("certificate control result is not pass")
    if not certificate.get("reviewer") or not certificate.get("human_seal", {}).get("seal_id"):
        failures.append("named reviewer and human seal are required")
    input_rel = str(certificate.get("input_path", ""))
    input_path = (matter / input_rel).resolve() if input_rel else None
    if not input_path or matter not in input_path.parents or not input_path.is_file():
        failures.append("certificate input_path must reference an existing matter file")
    elif certificate.get("input_sha256") != _sha256(input_path):
        failures.append("certificate input digest is stale")
    policy_path = root / "lib" / "client-lanes" / "founder-control-assurance.json"
    if not policy_path.is_file() or certificate.get("policy_sha256") != _sha256(policy_path):
        failures.append("assurance policy digest is stale or missing")
    digest, count, ledger_failures = ledger_digest(matter)
    if certificate.get("ledger_sha256") != digest or certificate.get("ledger_count") != count:
        failures.append("transfer/conversion ledger digest is stale")
    failures.extend(ledger_failures)
    controls = certificate.get("controls", {})
    for control in (
        "cap_table_reconciled",
        "voting_universe_reconciled",
        "control_math_passed",
        "document_precedence_clear",
        "case_law_index_reviewed",
        "jurisdiction_and_forum_reviewed",
        "human_seal_recorded",
    ):
        if controls.get(control) is not True:
            failures.append(f"required assurance control is not complete: {control}")
    return {
        "status": "pass" if not failures else "fail",
        "certificate": str(certificate_path),
        "certificate_sha256": _sha256(certificate_path),
        "event": certificate.get("event"),
        "reviewer": certificate.get("reviewer"),
        "ledger_sha256": digest,
        "ledger_count": count,
        "failures": failures,
    }

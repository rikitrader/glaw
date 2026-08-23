"""Deterministic, fail-closed court routing and supervised filing handoffs.

This module does not file, sign, serve, transmit, or pay. It validates source-backed
forum facts, assembles checksum manifests, and records human-generated receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COURT_PACKS = ROOT / "jurisdiction" / "packs" / "courts"
SOURCE_ID_RE = re.compile(r"^SRC-[0-9]{4}(?:\b|\s)")
VERIFIED_FEDERAL_DISTRICTS = {"mdfl": "mdfl-2025.json"}
SUPPORTED_CASE_KINDS = {"ordinary_civil", "civil"}
REQUIRED_JURISDICTION_CHECKS = (
    "personal_jurisdiction",
    "venue",
    "standing",
    "limitations",
    "pre_suit",
)
GATE_EVIDENCE = (
    "citations_verified",
    "adversarial_clear",
    "writing_clear",
    "final_packet_ready",
    "chief_approved",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_ok(value: Any) -> bool:
    return bool(SOURCE_ID_RE.match(str(value or "").strip()))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_pack(name: str) -> dict[str, Any]:
    return load_json(COURT_PACKS / name)


def authority_freshness(
    pack_names: list[str] | None = None,
    *,
    as_of: date | None = None,
    max_age_days: int = 45,
) -> dict[str, Any]:
    """Validate local source-backed freshness metadata for court packs.

    This is deliberately an offline gate. It validates review dates, status,
    and source metadata; it does not claim that a URL is reachable or that a
    court has accepted a filing.
    """
    if max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")
    names = pack_names or sorted(path.name for path in COURT_PACKS.glob("*.json"))
    checked_at = as_of or date.today()
    packs: list[dict[str, Any]] = []
    failures: list[str] = []
    for name in names:
        try:
            pack = load_pack(name)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append(f"{name}: unable to load authority pack: {exc}")
            continue
        pack_failures: list[str] = []
        status = str(pack.get("status") or "").strip().lower()
        checked_raw = str(pack.get("checked_on") or "").strip()
        if status not in {"verified", "verified-baseline"}:
            pack_failures.append("status must be verified or verified-baseline")
        try:
            checked_on = date.fromisoformat(checked_raw)
        except ValueError:
            checked_on = None
            pack_failures.append("checked_on must be an ISO date")
        age_days = None
        if checked_on is not None:
            if checked_on > checked_at:
                pack_failures.append("checked_on cannot be in the future")
            else:
                age_days = (checked_at - checked_on).days
                if age_days > max_age_days:
                    pack_failures.append(f"authority pack is {age_days} days old; maximum is {max_age_days}")
        sources = pack.get("sources")
        if not isinstance(sources, list) or not sources:
            pack_failures.append("sources must be a non-empty list")
            sources = []
        for index, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                pack_failures.append(f"sources[{index}] must be an object")
                continue
            for field in ("id", "url", "description"):
                if not str(source.get(field) or "").strip():
                    pack_failures.append(f"sources[{index}].{field} is required")
            if source.get("url") and not str(source["url"]).startswith(("https://", "http://")):
                pack_failures.append(f"sources[{index}].url must be http(s)")
        row = {
            "pack": name,
            "id": str(pack.get("id") or name),
            "status": "pass" if not pack_failures else "block",
            "checked_on": checked_raw,
            "age_days": age_days,
            "max_age_days": max_age_days,
            "source_count": len(sources),
            "failures": pack_failures,
        }
        packs.append(row)
        failures.extend(f"{name}: {item}" for item in pack_failures)
    return {
        "status": "pass" if not failures and packs else "block",
        "as_of": checked_at.isoformat(),
        "max_age_days": max_age_days,
        "packs": packs,
        "failures": failures,
        "authority_boundary": "Offline metadata freshness only; source reachability, filing-day rule changes, portal notices, and human filing approval remain required.",
    }


def _normalize_county(value: str) -> str:
    raw = " ".join(str(value or "").replace("County", "").strip().split())
    aliases = {
        "st johns": "St. Johns",
        "st. johns": "St. Johns",
        "st lucie": "St. Lucie",
        "st. lucie": "St. Lucie",
        "miami dade": "Miami-Dade",
        "miami-dade": "Miami-Dade",
        "desoto": "DeSoto",
    }
    return aliases.get(raw.lower(), raw.title())


def florida_circuit_for_county(county: str) -> int | None:
    normalized = _normalize_county(county)
    pack = load_pack("florida-trial-courts-2026.json")
    for circuit, counties in pack.get("circuits", {}).items():
        if normalized in counties:
            return int(circuit)
    return None


def _party_citizenship(party: dict[str, Any], label: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    states: set[str] = set()
    entity_type = str(party.get("entity_type") or party.get("type") or "individual").strip().lower()
    name = str(party.get("name") or label)
    if not source_ok(party.get("source_id")):
        errors.append(f"{label} {name}: citizenship facts require current SRC-#### provenance")

    if entity_type in {"individual", "person"}:
        domicile = str(party.get("domicile") or "").strip()
        if not domicile:
            errors.append(f"{label} {name}: individual domicile is required; residence or mailing address is insufficient")
        else:
            states.add(domicile.casefold())
    elif entity_type in {"corporation", "corporate"}:
        formed = str(party.get("state_of_incorporation") or "").strip()
        ppb = str(party.get("principal_place_of_business") or "").strip()
        if not formed or not ppb:
            errors.append(f"{label} {name}: corporation needs both state of incorporation and principal place of business")
        states.update(item.casefold() for item in (formed, ppb) if item)
    elif entity_type in {"llc", "limited_liability_company"}:
        members = party.get("members")
        if not isinstance(members, list) or not members:
            errors.append(f"{label} {name}: LLC citizenship requires every member and nested member")
        else:
            for index, member in enumerate(members, start=1):
                if not isinstance(member, dict):
                    errors.append(f"{label} {name}: member {index} must be an object")
                    continue
                nested, nested_errors = _party_citizenship(member, f"{label} {name} member {index}")
                states.update(nested)
                errors.extend(nested_errors)
    elif entity_type in {"partnership", "limited_partnership"}:
        partners = party.get("partners")
        if not isinstance(partners, list) or not partners:
            errors.append(f"{label} {name}: partnership citizenship requires every partner and nested partner")
        else:
            for index, partner in enumerate(partners, start=1):
                if not isinstance(partner, dict):
                    errors.append(f"{label} {name}: partner {index} must be an object")
                    continue
                nested, nested_errors = _party_citizenship(partner, f"{label} {name} partner {index}")
                states.update(nested)
                errors.extend(nested_errors)
    else:
        errors.append(f"{label} {name}: unsupported entity_type {entity_type!r} for diversity analysis")
    return states, errors


def _amount(case_data: dict[str, Any]) -> tuple[float | None, list[str]]:
    errors: list[str] = []
    amount = case_data.get("amount_in_controversy")
    if not isinstance(amount, dict):
        return None, ["amount_in_controversy must be an object with value, exclusions, and SRC-#### provenance"]
    try:
        value = float(amount.get("value"))
    except (TypeError, ValueError):
        value = None
        errors.append("amount_in_controversy.value must be numeric")
    if amount.get("exclusive_of_interest_costs_fees") is not True:
        errors.append("amount must expressly exclude interest, costs, and fees for routing")
    if not source_ok(amount.get("source_id")):
        errors.append("amount in controversy requires current SRC-#### provenance")
    return value, errors


def _jurisdiction_checks(case_data: dict[str, Any]) -> list[str]:
    checks = case_data.get("jurisdiction_checks")
    if not isinstance(checks, dict):
        return ["jurisdiction_checks object is required"]
    errors: list[str] = []
    for key in REQUIRED_JURISDICTION_CHECKS:
        row = checks.get(key)
        if not isinstance(row, dict):
            errors.append(f"jurisdiction_checks.{key} is required")
            continue
        if row.get("status") != "pass":
            errors.append(f"jurisdiction_checks.{key} must be pass, not {row.get('status', 'missing')}")
        if not source_ok(row.get("source_id")):
            errors.append(f"jurisdiction_checks.{key} requires current SRC-#### provenance")
    return errors


def federal_basis(case_data: dict[str, Any]) -> dict[str, Any]:
    parties = case_data.get("parties") if isinstance(case_data.get("parties"), dict) else {}
    plaintiffs = parties.get("plaintiffs") if isinstance(parties.get("plaintiffs"), list) else []
    defendants = parties.get("defendants") if isinstance(parties.get("defendants"), list) else []
    claims = case_data.get("claims") if isinstance(case_data.get("claims"), list) else []

    federal_claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("federal_question") is not True:
            continue
        if claim.get("statutory_basis") and source_ok(claim.get("source_id")):
            federal_claims.append(str(claim.get("statutory_basis")))

    p_states: set[str] = set()
    d_states: set[str] = set()
    diversity_errors: list[str] = []
    if not plaintiffs or not defendants:
        diversity_errors.append("at least one plaintiff and defendant are required")
    for index, party in enumerate(plaintiffs, start=1):
        if isinstance(party, dict):
            states, errors = _party_citizenship(party, f"plaintiff {index}")
            p_states.update(states)
            diversity_errors.extend(errors)
        else:
            diversity_errors.append(f"plaintiff {index} must be an object")
    for index, party in enumerate(defendants, start=1):
        if isinstance(party, dict):
            states, errors = _party_citizenship(party, f"defendant {index}")
            d_states.update(states)
            diversity_errors.extend(errors)
        else:
            diversity_errors.append(f"defendant {index} must be an object")
    amount, amount_errors = _amount(case_data)
    diversity_errors.extend(amount_errors)
    overlap = sorted(p_states & d_states)
    if overlap:
        diversity_errors.append("complete diversity fails; opposing citizenship overlaps: " + ", ".join(overlap))
    if amount is None or amount <= 75000:
        diversity_errors.append("diversity amount must exceed $75,000")

    federal_question = bool(federal_claims)
    diversity = not diversity_errors
    bases = []
    if federal_question:
        bases.append("28 U.S.C. § 1331")
    if diversity:
        bases.append("28 U.S.C. § 1332")
    return {
        "status": "pass" if bases else "fail",
        "bases": bases,
        "federal_claims": federal_claims,
        "federal_question": federal_question,
        "diversity": diversity,
        "plaintiff_citizenship": sorted(p_states),
        "defendant_citizenship": sorted(d_states),
        "diversity_failures": diversity_errors,
    }


def route_case(case_data: dict[str, Any]) -> dict[str, Any]:
    requested = str(case_data.get("forum_request") or "auto").strip().lower()
    court = case_data.get("court") if isinstance(case_data.get("court"), dict) else {}
    checks = _jurisdiction_checks(case_data)
    federal = federal_basis(case_data)
    candidates: list[dict[str, Any]] = []

    district = str(court.get("federal_district") or "").strip().lower()
    federal_failures = list(checks)
    federal_pack_name = VERIFIED_FEDERAL_DISTRICTS.get(district, "federal-core-2025.json")
    federal_authority = authority_freshness([federal_pack_name])
    if federal_authority["status"] != "pass":
        federal_failures.extend(federal_authority["failures"])
    federal_status = "pass"
    if federal.get("status") != "pass":
        federal_failures.append("no verified federal-question or diversity basis")
    if not district:
        federal_failures.append("court.federal_district is required for federal routing")
    elif district not in VERIFIED_FEDERAL_DISTRICTS:
        federal_status = "review"
        federal_failures.append(f"district {district} lacks a current verified local-rule pack")
    if any(item for item in federal_failures if "lacks a current" not in item):
        federal_status = "block"
    candidates.append({
        "forum": "federal_district",
        "court_code": district,
        "status": federal_status,
        "basis": federal.get("bases", []),
        "basis_analysis": federal,
        "failures": federal_failures,
        "authority_pack": federal_pack_name,
        "authority_freshness": federal_authority,
    })

    florida_pack = load_pack("florida-trial-courts-2026.json")
    state_failures = list(checks)
    florida_authority = authority_freshness(["florida-trial-courts-2026.json"])
    if florida_authority["status"] != "pass":
        state_failures.extend(florida_authority["failures"])
    state = str(court.get("state") or "").strip()
    county = _normalize_county(str(court.get("county") or ""))
    circuit = florida_circuit_for_county(county)
    amount, amount_errors = _amount(case_data)
    state_failures.extend(amount_errors)
    case_kind = str(case_data.get("case_kind") or "ordinary_civil").strip().lower()
    if state.casefold() != "florida":
        state_failures.append("only Florida state trial-court routing is currently verified")
    if not circuit:
        state_failures.append("court.county must identify one of Florida's 67 counties")
    if case_kind not in SUPPORTED_CASE_KINDS:
        state_failures.append(f"case_kind {case_kind!r} requires specialist/local-counsel routing")

    division = ""
    if amount is not None:
        thresholds = florida_pack["ordinary_civil_thresholds"]
        if amount <= float(thresholds["small_claims_max"]):
            division = "small_claims"
        elif amount <= float(thresholds["county_civil_max"]):
            division = "county_civil"
        else:
            division = "circuit_civil"
    candidates.append({
        "forum": "florida_trial_court",
        "state": "Florida",
        "county": county,
        "judicial_circuit": circuit,
        "division": division,
        "status": "block" if state_failures else "pass",
        "basis": ["Florida ordinary civil monetary jurisdiction"],
        "failures": state_failures,
        "authority_pack": "florida-trial-courts-2026.json",
        "authority_freshness": florida_authority,
    })

    allowed = {
        "federal": [candidates[0]],
        "federal_district": [candidates[0]],
        "florida": [candidates[1]],
        "state": [candidates[1]],
        "auto": candidates,
    }
    considered = allowed.get(requested)
    if considered is None:
        return {
            "status": "block",
            "selected": None,
            "candidates": candidates,
            "failures": ["forum_request must be auto, federal, or florida"],
            "generated_at": utc_now(),
        }
    selected = next((row for row in considered if row["status"] == "pass"), None)
    if selected is None:
        selected = next((row for row in considered if row["status"] == "review"), None)
    status = selected["status"] if selected else "block"
    return {
        "status": status,
        "selected": selected,
        "candidates": candidates,
        "failures": [] if selected else ["no requested forum passed all source-backed routing gates"],
        "generated_at": utc_now(),
        "authority_boundary": "Forum screening only; licensed counsel must approve subject-matter jurisdiction, personal jurisdiction, venue, standing, limitations, pre-suit conditions, removal/remand, abstention, immunity, and local rules.",
    }


def _verified_artifact(row: Any, base: Path, label: str) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(row, dict) or row.get("status") != "pass":
        return None, f"{label} gate status must be pass"
    rel = str(row.get("artifact") or "").strip()
    if not rel:
        return None, f"{label} gate requires artifact path"
    path = (base / rel).resolve() if not Path(rel).is_absolute() else Path(rel).resolve()
    if not path.is_file():
        return None, f"{label} artifact missing: {rel}"
    digest = sha256_file(path)
    if row.get("sha256") != digest:
        return None, f"{label} artifact hash mismatch: {rel}"
    return {"artifact": str(path), "sha256": digest, "size_bytes": path.stat().st_size}, None


def _document_manifest(case_data: dict[str, Any], base: Path, route: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    docs = case_data.get("documents") if isinstance(case_data.get("documents"), list) else []
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for index, doc in enumerate(docs, start=1):
        if not isinstance(doc, dict):
            failures.append(f"documents[{index}] must be an object")
            continue
        role = str(doc.get("role") or "").strip().lower()
        rel = str(doc.get("path") or "").strip()
        path = (base / rel).resolve() if rel and not Path(rel).is_absolute() else Path(rel).resolve()
        if not role or not rel or not path.is_file():
            failures.append(f"documents[{index}] requires role and existing path")
            continue
        rows.append({"role": role, "path": str(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    roles = [row["role"] for row in rows]
    selected = route.get("selected") or {}
    required = ["complaint", "summons"]
    if selected.get("forum") == "federal_district":
        required.append("civil_cover_sheet")
        parties = case_data.get("parties") if isinstance(case_data.get("parties"), dict) else {}
        corporate = any(
            str(p.get("entity_type") or "").lower() in {"corporation", "corporate", "llc", "limited_liability_company", "partnership", "limited_partnership"}
            for group in ("plaintiffs", "defendants")
            for p in parties.get(group, [])
            if isinstance(p, dict)
        )
        if corporate:
            required.append("corporate_disclosure")
    elif selected.get("division") == "small_claims":
        required.append("civil_cover_sheet")
        if "statement_of_claim" not in roles and "complaint" not in roles:
            failures.append("small claims requires a statement_of_claim or complaint artifact")
    else:
        required.append("civil_cover_sheet")
    for role in required:
        if role not in roles:
            failures.append(f"required filing document missing: {role}")
    defendants = ((case_data.get("parties") or {}).get("defendants") or []) if isinstance(case_data.get("parties"), dict) else []
    if roles.count("summons") < len(defendants):
        failures.append("one summons artifact is required per defendant, subject to clerk-specific workflow")
    return rows, failures


def prepare_packet(case_path: Path, output_dir: Path) -> dict[str, Any]:
    case_path = case_path.resolve()
    case_data = load_json(case_path)
    route = route_case(case_data)
    failures: list[str] = []
    if route.get("status") != "pass":
        failures.append("forum routing must pass before packet preparation")
    selected = route.get("selected") or {}
    selected_authority = (
        authority_freshness([str(selected.get("authority_pack"))])
        if selected.get("authority_pack")
        else {"status": "block", "failures": ["selected route has no authority pack"]}
    )
    if selected_authority.get("status") != "pass":
        failures.extend(selected_authority.get("failures", []))
    gates: dict[str, Any] = {}
    gate_data = case_data.get("gate_evidence") if isinstance(case_data.get("gate_evidence"), dict) else {}
    for name in GATE_EVIDENCE:
        verified, error = _verified_artifact(gate_data.get(name), case_path.parent, name)
        if error:
            failures.append(error)
        elif verified:
            gates[name] = verified
    documents, doc_failures = _document_manifest(case_data, case_path.parent, route)
    failures.extend(doc_failures)
    platform = "CM/ECF" if selected.get("forum") == "federal_district" else "Florida Courts E-Filing Portal"
    packet_id = f"court-packet-{uuid.uuid4()}"
    manifest = {
        "schema_version": 1,
        "packet_id": packet_id,
        "status": "blocked" if failures else "ready_for_human_filing",
        "generated_at": utc_now(),
        "case_source": str(case_path),
        "case_source_sha256": sha256_file(case_path),
        "route": route,
        "authority_freshness": selected_authority,
        "gate_evidence": gates,
        "documents": documents,
        "filing": {
            "platform": platform,
            "mode": "manual_supervised_handoff",
            "live_connector_configured": False,
            "fee": "VERIFY WITH COURT/PORTAL AT FILING",
            "signer": "licensed or otherwise court-authorized human filer",
        },
        "failures": sorted(set(failures)),
        "authority_boundary": "Signature-ready/checksum packet only. GLAW does not file, sign, serve, transmit, select a live filing event, or pay a fee. A licensed/authorized human must reverify the court, division, case type/subtype, local rules, judge orders, fees, PDF limits, confidentiality/redaction, and each document immediately before filing.",
    }
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "court-filing-manifest.json"
    write_json(json_path, manifest)
    lines = [
        "# Court Filing Handoff",
        "",
        f"Status: {manifest['status']}",
        f"Packet: {packet_id}",
        f"Platform: {platform}",
        "",
        "## Route",
        "",
        f"- {json.dumps(selected, sort_keys=True)}",
        "",
        "## Documents",
        "",
    ]
    lines.extend(f"- [ ] {row['role']} — {row['path']} — sha256 {row['sha256']}" for row in documents)
    lines.extend(["", "## Blocking Items", ""])
    lines.extend(f"- {item}" for item in manifest["failures"]) if manifest["failures"] else lines.append("- none")
    lines.extend(["", "## Human Authority Boundary", "", manifest["authority_boundary"], ""])
    (output_dir / "court-filing-checklist.md").write_text("\n".join(lines), encoding="utf-8")
    manifest["manifest_path"] = str(json_path)
    return manifest


def create_handoff(packet_path: Path, output_path: Path) -> dict[str, Any]:
    packet_path = packet_path.resolve()
    packet = load_json(packet_path)
    failures = _packet_integrity_failures(packet)
    if packet.get("status") != "ready_for_human_filing":
        failures.append("packet status must be ready_for_human_filing")
    handoff = {
        "schema_version": 1,
        "handoff_id": f"court-handoff-{uuid.uuid4()}",
        "status": "blocked" if failures else "ready_for_human_operator",
        "generated_at": utc_now(),
        "packet_path": str(packet_path),
        "packet_sha256": sha256_file(packet_path),
        "platform": (packet.get("filing") or {}).get("platform"),
        "documents": packet.get("documents", []),
        "failures": failures,
        "operator_steps": [
            "Reverify filing-day local rules, judge orders, division, case type/subtype, fees, and PDF limits.",
            "Confirm the authorized filer account, signer authority, redactions, and sealed-filing procedure.",
            "Upload each checksum-matched document manually and review the portal summary before submission.",
            "A human submits and pays only after final confirmation.",
            "Export the court receipt and use record-receipt; do not infer a case number or filing time.",
        ],
        "authority_boundary": "This artifact is a manual handoff, not a filing or transmission.",
    }
    write_json(output_path.resolve(), handoff)
    return handoff


def _packet_integrity_failures(packet: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    case_source = Path(str(packet.get("case_source") or ""))
    if not case_source.is_file() or sha256_file(case_source) != packet.get("case_source_sha256"):
        failures.append("case source changed or is missing after packet generation")
    for collection, label in ((packet.get("gate_evidence", {}).values(), "gate evidence"), (packet.get("documents", []), "document")):
        for row in collection:
            if not isinstance(row, dict):
                failures.append(f"invalid {label} manifest row")
                continue
            path = Path(str(row.get("artifact") or row.get("path") or ""))
            if not path.is_file() or sha256_file(path) != row.get("sha256"):
                failures.append(f"{label} changed or missing: {path}")
    return failures


def _filing_receipt_exists(packet_path: Path, packet_id: str) -> bool:
    ledger = packet_path.resolve().parent / "docket" / "filing-receipts.jsonl"
    if not ledger.is_file():
        return False
    for line in ledger.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("packet_id") == packet_id and row.get("status") == "recorded" and row.get("receipt_sha256"):
            return True
    return False


def live_submit(packet_path: Path, actor: str, role: str) -> dict[str, Any]:
    from glaw_authority import require_human_authority

    ok, result = require_human_authority("submit-live", actor=actor, role=role, context=str(packet_path))
    if not ok:
        return {"status": "blocked", "reason": result, "submitted": False}
    return {
        "status": "blocked",
        "reason": "No court-approved live connector is configured. Use handoff for supervised manual filing and record the official receipt afterward.",
        "human_authority": result,
        "submitted": False,
        "authority_boundary": "Human authority is necessary but does not create a connector or prove court acceptance.",
    }


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def record_receipt(packet_path: Path, receipt_path: Path, actor: str) -> dict[str, Any]:
    packet_path = packet_path.resolve()
    receipt_path = receipt_path.resolve()
    packet = load_json(packet_path)
    receipt = load_json(receipt_path)
    missing = [key for key in ("case_number", "filed_at", "filed_by", "court", "receipt_artifact") if not receipt.get(key)]
    artifact = Path(str(receipt.get("receipt_artifact") or ""))
    if not artifact.is_absolute():
        artifact = (receipt_path.parent / artifact).resolve()
    if not artifact.is_file():
        missing.append("existing receipt_artifact")
    if not actor.strip():
        missing.append("named recording actor")
    row = {
        "event": "court_filing_receipt_recorded",
        "recorded_at": utc_now(),
        "recorded_by": actor.strip(),
        "packet_id": packet.get("packet_id"),
        "packet_sha256": sha256_file(packet_path),
        "case_number": receipt.get("case_number"),
        "court": receipt.get("court"),
        "filed_at": receipt.get("filed_at"),
        "filed_by": receipt.get("filed_by"),
        "receipt_artifact": str(artifact),
        "receipt_sha256": sha256_file(artifact) if artifact.is_file() else "",
        "status": "blocked" if missing else "recorded",
        "missing": missing,
    }
    if not missing:
        _append_jsonl(packet_path.parent / "docket" / "filing-receipts.jsonl", row)
    return row


def service_handoff(packet_path: Path, output_path: Path) -> dict[str, Any]:
    packet_path = packet_path.resolve()
    packet = load_json(packet_path)
    route = packet.get("route", {}).get("selected") or {}
    failures = _packet_integrity_failures(packet)
    if packet.get("status") != "ready_for_human_filing":
        failures.append("packet status must be ready_for_human_filing")
    if not _filing_receipt_exists(packet_path, str(packet.get("packet_id") or "")):
        failures.append("recorded official filing receipt is required before service handoff")
    result = {
        "schema_version": 1,
        "service_handoff_id": f"service-handoff-{uuid.uuid4()}",
        "status": "blocked" if failures else "ready_for_human_operator",
        "generated_at": utc_now(),
        "packet_id": packet.get("packet_id"),
        "forum": route.get("forum"),
        "failures": failures,
        "instructions": [
            "Do not serve until the court has accepted the initiating filing and issued/approved each summons.",
            "A human chooses a legally authorized server and method for each defendant.",
            "Record the actual service event and proof; do not docket an answer deadline from an assumed service date.",
        ],
        "authority_boundary": "Preparation only. GLAW does not serve process.",
    }
    write_json(output_path.resolve(), result)
    return result


def record_service(packet_path: Path, proof_path: Path, actor: str) -> dict[str, Any]:
    packet_path = packet_path.resolve()
    packet = load_json(packet_path)
    proof = load_json(proof_path.resolve())
    missing = [key for key in ("defendant", "served_at", "method", "server", "proof_artifact") if not proof.get(key)]
    if _packet_integrity_failures(packet):
        missing.append("unchanged ready filing packet")
    if not _filing_receipt_exists(packet_path, str(packet.get("packet_id") or "")):
        missing.append("recorded official filing receipt")
    artifact = Path(str(proof.get("proof_artifact") or ""))
    if not artifact.is_absolute():
        artifact = (proof_path.parent / artifact).resolve()
    if not artifact.is_file():
        missing.append("existing proof_artifact")
    if not actor.strip():
        missing.append("named recording actor")
    answer_date = ""
    selected = packet.get("route", {}).get("selected") or {}
    if not missing and selected.get("forum") == "federal_district":
        try:
            served = date.fromisoformat(str(proof["served_at"])[:10])
            days = 60 if proof.get("defendant_type") == "federal" else 21
            answer_date = (served + timedelta(days=days)).isoformat()
        except ValueError:
            missing.append("served_at ISO date")
    row = {
        "event": "service_proof_recorded",
        "recorded_at": utc_now(),
        "recorded_by": actor.strip(),
        "packet_id": packet.get("packet_id"),
        "defendant": proof.get("defendant"),
        "served_at": proof.get("served_at"),
        "method": proof.get("method"),
        "server": proof.get("server"),
        "proof_artifact": str(artifact),
        "proof_sha256": sha256_file(artifact) if artifact.is_file() else "",
        "candidate_answer_date": answer_date,
        "deadline_status": "review_required" if answer_date else "unresolved",
        "deadline_note": "Candidate only. Recompute under applicable Rule 6, Rule 12, waiver, government-party, service-method, court-order, weekend, holiday, and extension rules before docket reliance.",
        "status": "blocked" if missing else "recorded",
        "missing": missing,
    }
    if not missing:
        _append_jsonl(packet_path.parent / "docket" / "service-receipts.jsonl", row)
    return row

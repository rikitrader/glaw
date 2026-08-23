"""Hash-bound adversarial cross-review protocol.

The protocol is an evidence workflow, not a substitute for counsel.  It keeps
the first-pass opinions immutable, exposes only an explicit target to the
opposing pass, and requires an independent adjudicator before a disagreement
can be closed.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PHASES = ("RED_CROSS_REVIEW", "BLUE_REBUTTAL", "RED_SUR_REBUTTAL", "ADJUDICATION")
ACTORS = {
    "RED_CROSS_REVIEW": "victor_sterling",
    "BLUE_REBUTTAL": "alexandra_vale",
    "RED_SUR_REBUTTAL": "victor_sterling",
    "ADJUDICATION": "independent_adjudicator",
}
DECISIONS = {"OPEN", "CONCEDED", "MAINTAINED", "RESOLVED", "REVIEW_REQUIRED", "BLOCK"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def opinion_hash(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return digest(payload)


def _required_text(value: Any, name: str) -> str:
    value = str(value or "").strip()
    if not value or value.lower() in {"tbd", "unknown", "reviewer", "attorney", "operator"}:
        raise ValueError(f"{name} must be a named, non-placeholder value")
    return value


def validate_entry(entry: dict[str, Any], expected_phase: str, *, expected_target: str | None = None) -> list[str]:
    errors: list[str] = []
    if entry.get("phase") != expected_phase:
        errors.append(f"phase must be {expected_phase}")
    if entry.get("actor") != ACTORS.get(expected_phase):
        errors.append(f"actor must be {ACTORS.get(expected_phase)}")
    try:
        _required_text(entry.get("reviewer_id"), "reviewer_id")
    except ValueError as exc:
        errors.append(str(exc))
    if expected_phase != "ADJUDICATION" and entry.get("target_hash") != expected_target:
        errors.append("target_hash does not match the immutable prior opinion")
    if not isinstance(entry.get("claims"), list) or not entry.get("claims"):
        errors.append("claims must be a non-empty array")
    if not isinstance(entry.get("evidence_refs"), list):
        errors.append("evidence_refs must be an array")
    if not isinstance(entry.get("unresolved_questions"), list):
        errors.append("unresolved_questions must be an array")
    if entry.get("decision") not in DECISIONS:
        errors.append(f"decision must be one of {sorted(DECISIONS)}")
    return errors


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def start(run_dir: Path) -> dict[str, Any]:
    blue_path, red_path = run_dir / "blue-first-pass.json", run_dir / "red-first-pass.json"
    snapshot_path = run_dir / "snapshot.json"
    missing = [str(path.name) for path in (blue_path, red_path, snapshot_path) if not path.is_file()]
    if missing:
        raise ValueError("cross-review requires: " + ", ".join(missing))
    state = {
        "protocol": "glaw-cross-review/v1",
        "run_dir": str(run_dir),
        "created_at": now(),
        "snapshot_hash": digest(_load_json(snapshot_path)),
        "blue_first_pass_hash": opinion_hash(blue_path),
        "red_first_pass_hash": opinion_hash(red_path),
        "phases": [],
        "status": "REVIEW_REQUIRED",
        "governor_decision": "REVIEW_REQUIRED",
        "resolution": None,
    }
    (run_dir / "cross-review.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def record(run_dir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    state_path = run_dir / "cross-review.json"
    if not state_path.is_file():
        raise ValueError("cross-review has not been started")
    state = _load_json(state_path)
    phase_index = len(state.get("phases", []))
    if phase_index >= len(PHASES):
        raise ValueError("all cross-review phases are already recorded")
    expected_phase = PHASES[phase_index]
    prior_target = None
    if expected_phase == "RED_CROSS_REVIEW":
        prior_target = state.get("blue_first_pass_hash")
    elif expected_phase == "BLUE_REBUTTAL":
        prior_target = digest(state["phases"][-1])
    elif expected_phase == "RED_SUR_REBUTTAL":
        prior_target = digest(state["phases"][-1])
    errors = validate_entry(entry, expected_phase, expected_target=prior_target)
    if errors:
        raise ValueError("invalid cross-review entry: " + "; ".join(errors))
    stamped = dict(entry)
    stamped["recorded_at"] = now()
    stamped["entry_hash"] = digest(stamped)
    state.setdefault("phases", []).append(stamped)
    if expected_phase == "ADJUDICATION":
        if stamped.get("decision") != "RESOLVED":
            state["governor_decision"] = "BLOCK"
            state["status"] = "BLOCK"
            state["resolution"] = "adjudicator did not resolve the disputed issue"
        else:
            state["governor_decision"] = "REVIEW_REQUIRED"
            state["status"] = "REVIEW_REQUIRED"
            state["resolution"] = "resolved by independent adjudicator; human legal approval remains required"
    state["updated_at"] = now()
    state["state_hash"] = digest(state)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def check(run_dir: Path) -> dict[str, Any]:
    state = _load_json(run_dir / "cross-review.json")
    phases = state.get("phases") or []
    failures = []
    if len(phases) != len(PHASES):
        failures.append(f"requires all {len(PHASES)} phases; found {len(phases)}")
    for index, entry in enumerate(phases):
        expected = PHASES[index]
        target = None
        if expected == "RED_CROSS_REVIEW": target = state.get("blue_first_pass_hash")
        elif index: target = digest(phases[index - 1])
        failures.extend(validate_entry(entry, expected, expected_target=target))
    if phases and phases[-1].get("decision") != "RESOLVED":
        failures.append("independent adjudication did not resolve the dispute")
    result = {
        "status": "PASS" if not failures else "BLOCK",
        "governor_decision": state.get("governor_decision", "REVIEW_REQUIRED"),
        "phases_recorded": len(phases),
        "required_phases": list(PHASES),
        "failures": sorted(set(failures)),
    }
    return result

"""Oversight Board policy-pack validation for GLAW."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "oversight-board" / "policies" / "core.json"

REQUIRED_DECISIONS = {"approve", "fix", "deny", "halt", "resume"}
REQUIRED_TRIGGER_IDS = {
    "human-only-act-requested",
    "non-convergence",
    "accounting-control-failure",
    "government-adversary-failure",
    "citation-grounding-failure",
    "high-impact-filing",
}
REQUIRED_PROHIBITED_ACTS = {
    "file",
    "serve",
    "sign",
    "transmit",
    "charge",
    "pay",
    "submit-live",
}


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(_nonempty_string(item) for item in value)


def validate_policy(data: object, *, path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return {
            "status": "fail",
            "path": str(path),
            "failures": [{"id": "root", "detail": "policy pack must be a JSON object"}],
            "warnings": [],
        }

    if data.get("schema_version") != 1:
        failures.append({"id": "schema_version", "detail": "schema_version must be 1"})
    if not _nonempty_string(data.get("name")):
        failures.append({"id": "name", "detail": "name is required"})
    if not _nonempty_string(data.get("authority_boundary")):
        failures.append({"id": "authority_boundary", "detail": "authority_boundary is required"})
    if "human seal" not in str(data.get("authority_boundary", "")).lower():
        failures.append({"id": "human_seal", "detail": "authority_boundary must preserve the human seal"})
    prohibited = set(data.get("prohibited_autonomous_acts") or [])
    missing_acts = sorted(REQUIRED_PROHIBITED_ACTS - prohibited)
    if missing_acts:
        failures.append({"id": "prohibited_autonomous_acts", "detail": "missing: " + ", ".join(missing_acts)})

    triggers = data.get("escalation_triggers")
    trigger_ids: set[str] = set()
    if not isinstance(triggers, list) or not triggers:
        failures.append({"id": "escalation_triggers", "detail": "at least one escalation trigger is required"})
    else:
        for idx, item in enumerate(triggers, start=1):
            if not isinstance(item, dict):
                failures.append({"id": f"escalation_trigger_{idx}", "detail": "trigger must be an object"})
                continue
            trigger_id = str(item.get("id", "")).strip()
            trigger_ids.add(trigger_id)
            for key in ("id", "description", "owner", "next_command", "source_requirement"):
                if not _nonempty_string(item.get(key)):
                    failures.append({"id": f"trigger_{idx}_{key}", "detail": f"escalation trigger {idx} missing {key}"})
            if "SRC-####" not in str(item.get("source_requirement", "")):
                failures.append({"id": f"trigger_{idx}_source", "detail": "source_requirement must mention SRC-####"})
    missing_triggers = sorted(REQUIRED_TRIGGER_IDS - trigger_ids)
    if missing_triggers:
        failures.append({"id": "required_escalation_triggers", "detail": "missing: " + ", ".join(missing_triggers)})

    rules = data.get("decision_rules")
    rule_ids: set[str] = set()
    if not isinstance(rules, list) or not rules:
        failures.append({"id": "decision_rules", "detail": "decision rules are required"})
    else:
        for idx, rule in enumerate(rules, start=1):
            if not isinstance(rule, dict):
                failures.append({"id": f"decision_rule_{idx}", "detail": "decision rule must be an object"})
                continue
            decision = str(rule.get("decision", "")).strip()
            rule_ids.add(decision)
            for key in ("decision", "minimum_evidence", "conditions", "audit_entry"):
                if key == "conditions":
                    if not _string_list(rule.get(key)):
                        failures.append({"id": f"decision_{idx}_{key}", "detail": f"decision rule {idx} must list conditions"})
                elif not _nonempty_string(rule.get(key)):
                    failures.append({"id": f"decision_{idx}_{key}", "detail": f"decision rule {idx} missing {key}"})
            if "SRC-####" not in str(rule.get("minimum_evidence", "")):
                failures.append({"id": f"decision_{idx}_evidence", "detail": "minimum_evidence must mention SRC-####"})
            if decision in {"approve", "resume"} and "ADMIN" not in str(rule.get("conditions", "")):
                failures.append({"id": f"decision_{idx}_admin", "detail": f"{decision} must require RBAC ADMIN"})
    missing_rules = sorted(REQUIRED_DECISIONS - rule_ids)
    if missing_rules:
        failures.append({"id": "required_decision_rules", "detail": "missing: " + ", ".join(missing_rules)})

    required_evidence = data.get("required_evidence")
    if not _string_list(required_evidence):
        failures.append({"id": "required_evidence", "detail": "required_evidence must be a nonempty string list"})
    else:
        joined = " ".join(required_evidence)
        for token in ("SRC-####", "owner", "required_fix", "next_command"):
            if token not in joined:
                failures.append({"id": f"required_evidence_{token}", "detail": f"required_evidence must mention {token}"})

    if failures:
        status = "fail"
    else:
        status = "pass"
    return {
        "status": status,
        "path": str(path),
        "name": data.get("name", ""),
        "failures": failures,
        "warnings": warnings,
        "required_trigger_count": len(REQUIRED_TRIGGER_IDS),
        "decision_rule_count": len(REQUIRED_DECISIONS),
    }


def validate_policy_file(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    try:
        data = load_policy(path)
    except FileNotFoundError:
        return {
            "status": "fail",
            "path": str(path),
            "failures": [{"id": "missing_policy", "detail": "policy file is missing"}],
            "warnings": [],
        }
    except json.JSONDecodeError as exc:
        return {
            "status": "fail",
            "path": str(path),
            "failures": [{"id": "invalid_json", "detail": str(exc)}],
            "warnings": [],
        }
    return validate_policy(data, path=path)

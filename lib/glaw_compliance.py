"""Shared compliance-manifest helpers for GLAW orchestrator surfaces."""
from __future__ import annotations


def compliance_failures(rows: object) -> list[dict]:
    if not isinstance(rows, list):
        return []
    return [
        row for row in rows
        if isinstance(row, dict) and row.get("status") != "pass"
    ]


def compliance_action_plan(rows: object) -> list[dict]:
    plan = []
    for row in compliance_failures(rows):
        plan.append({
            "id": str(row.get("id", "")).strip(),
            "owner": str(row.get("owner", "")).strip(),
            "next_command": str(row.get("next_command", "")).strip(),
            "required_fix": str(row.get("required_fix", "")).strip(),
            "missing": list(row.get("missing") or []),
        })
    return plan

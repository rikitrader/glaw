"""Automatic lane/department/reviewer dependency matrix."""
from __future__ import annotations

import json
from pathlib import Path

from glaw_premium_scope import premium_lane_requirement


DEPARTMENTS = {
    "corp-build": ["Corporate", "Securities/Funds", "Tax/IRS", "Accounting/Finance", "Regulatory", "Private Client"],
    "litigation": ["Litigation", "Legal Research", "Evidence", "Regulatory"],
    "investigation": ["Investigations", "Intelligence", "FinCEN/AML", "SEC", "Litigation"],
    "contract-review": ["Corporate", "Commercial Contracts", "Legal Research"],
}


def resolve(root: Path, intake: dict) -> dict:
    requirement = premium_lane_requirement(intake)
    lanes = list(requirement.get("required_lanes") or [])
    track = intake.get("universal", {}).get("workflow_track") or intake.get("workflow_track") or "litigation"
    manifest = json.loads((root / "lib/client-lanes/premium-lanes.json").read_text(encoding="utf-8"))
    lane_rows = manifest.get("lanes", manifest)
    reviewers = []
    artifacts = []
    for lane in lanes:
        row = lane_rows.get(lane, {}) if isinstance(lane_rows, dict) else {}
        reviewers.extend(row.get("lead_seats", []))
        reviewers.extend(row.get("adversarial_reviewers", []))
        artifacts.extend(row.get("required_lane_packet", []))
    departments = list(DEPARTMENTS.get(track, ["Legal Research", "Corporate", "Accounting/Finance"]))
    return {
        "schema": "glaw-dependency-matrix/v1",
        "track": track,
        "lanes": sorted(set(lanes)),
        "departments": sorted(set(departments)),
        "reviewers": sorted(set(str(item) for item in reviewers)),
        "required_artifacts": sorted(set(str(item) for item in artifacts)),
        "required_gates": ["intake", "jurisdiction", "primary_authority", "rag_context", "claude_codex_parity", "citation_verifier", "adverse_authority", "red_team", "legal_governor", "human_counsel"],
    }

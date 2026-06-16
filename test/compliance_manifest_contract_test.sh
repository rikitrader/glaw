#!/usr/bin/env bash
# compliance_manifest_contract_test.sh - final-packet compliance rows must be self-routing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GLAW_ROOT="$ROOT"

python3 - <<'PY'
import importlib.machinery
import importlib.util
import json
from pathlib import Path

root = Path(__import__("os").environ["GLAW_ROOT"])
packet_path = root / "bin" / "glaw-final-packet"
gate_path = root / "bin" / "glaw-gate"

loader = importlib.machinery.SourceFileLoader("glaw_final_packet", str(packet_path))
spec = importlib.util.spec_from_loader("glaw_final_packet", loader)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

passed = 0


def ok(condition, message):
    global passed
    if not condition:
        raise AssertionError(message)
    passed += 1


def rows_by_id(rows):
    return {row["id"]: row for row in rows}


routes = module.COMPLIANCE_ROW_ROUTES
expected_route_ids = {
    "ethics-upl",
    "citation-grounding",
    "government-adversary",
    "senior-review-source-support",
    "red-flag-accountability",
    "source-evidence-chain",
    "professional-report-quality",
    "reviewer-identity",
    "accounting-control",
    "accounting-control-not-required",
}
ok(set(routes) == expected_route_ids, "final-packet route table ids drifted")

gate_text = gate_path.read_text(encoding="utf-8")
for row_id, (next_command, required_fix) in routes.items():
    ok(json.dumps(row_id) in gate_text, f"glaw-gate missing compliance row id {row_id}")
    ok(json.dumps(next_command) in gate_text, f"glaw-gate missing next_command for {row_id}")
    ok(json.dumps(required_fix) in gate_text, f"glaw-gate missing required_fix for {row_id}")

failing_rows = rows_by_id(module.compliance_manifest(
    "accounting-tax",
    {
        "conflicts_cleared": False,
        "ethics_gate_complete": False,
        "upl_footer_clear": False,
        "citations_verified": False,
        "citation_gate_complete": False,
        "red_flags_clear": False,
        "red_flag_resolution_evidence_clear": False,
        "nonblocking_red_flags_accounted_clear": False,
        "source_evidence_manifest_clear": False,
    },
    accounting_control={
        "required": True,
        "status": "fail",
        "missing": ["bank_reconciliation.status=pass"],
    },
    government_adversary_rows=[
        {"lens": "irs-examiner", "status": "fail", "missing": ["attack SRC-0001"]}
    ],
    source_manifest=[],
    senior_review_evidence_manifest=[
        {"kind": "council", "name": "tax partner", "status": "fail", "missing": ["notes"]}
    ],
    red_flag_resolution_evidence_manifest=[
        {"id": "RF-1", "status": "fail", "missing": ["owner"]}
    ],
    nonblocking_red_flags=[
        {"id": "RF-2", "status": "fail", "missing": ["source"]}
    ],
    reviewer_identity=[
        {"kind": "adversarial", "name": "irs-examiner", "status": "fail", "missing": ["Soul:"]}
    ],
    report_quality_manifest=[
        {"path": "deliverable.md", "status": "fail", "missing_markers": ["Evidence:"]}
    ],
))
expected_failing_ids = expected_route_ids - {"accounting-control-not-required"}
ok(set(failing_rows) == expected_failing_ids, "accounting profile compliance rows are incomplete")
for row_id, row in failing_rows.items():
    ok(row["status"] == "fail", f"{row_id} should fail in failing fixture")
    ok(row["owner"], f"{row_id} missing owner")
    ok(row["next_command"], f"{row_id} missing next_command")
    ok(row["required_fix"], f"{row_id} missing required_fix")
    ok(row["missing"], f"{row_id} missing failure reason")

ok(
    failing_rows["government-adversary"]["owner"] == "glaw-adversarial"
    and failing_rows["government-adversary"]["next_command"] == "bin/glaw-adversarial status --profile auto",
    "government-adversary failure must route to glaw-adversarial",
)
ok(
    failing_rows["accounting-control"]["owner"] == "glaw-accounting"
    and failing_rows["accounting-control"]["next_command"] == "bin/glaw-accounting-control",
    "accounting failure must route to glaw-accounting-control",
)
ok(
    failing_rows["citation-grounding"]["owner"] == "glaw-legal-research"
    and failing_rows["citation-grounding"]["next_command"] == "bin/glaw-citation-gate status",
    "citation failure must route to glaw-citation-gate",
)

passing_gates = {
    "conflicts_cleared": True,
    "ethics_gate_complete": True,
    "upl_footer_clear": True,
    "citations_verified": True,
    "citation_gate_complete": True,
    "red_flags_clear": True,
    "red_flag_resolution_evidence_clear": True,
    "nonblocking_red_flags_accounted_clear": True,
    "source_evidence_manifest_clear": True,
}
not_required_rows = rows_by_id(module.compliance_manifest(
    "litigation",
    passing_gates,
    accounting_control={"required": False, "status": "not_required", "missing": []},
    government_adversary_rows=[{"lens": "opposing-counsel", "status": "pass", "missing": []}],
    source_manifest=[{"path": "evidence/source.txt", "size_bytes": 100}],
    senior_review_evidence_manifest=[{"kind": "council", "name": "litigator", "status": "pass", "missing": []}],
    red_flag_resolution_evidence_manifest=[],
    nonblocking_red_flags=[],
    reviewer_identity=[{"kind": "citation", "name": "legal-research", "status": "pass", "missing": []}],
    report_quality_manifest=[{"path": "brief.md", "status": "pass", "missing_markers": []}],
))
ok("accounting-control-not-required" in not_required_rows, "non-accounting profile missing not-required row")
ok("accounting-control" not in not_required_rows, "non-accounting profile incorrectly requires accounting control")
nr = not_required_rows["accounting-control-not-required"]
ok(nr["status"] == "pass", "not-required accounting row should pass")
ok(nr["owner"] == "glaw-accounting", "not-required accounting row still needs accountable owner")
ok(nr["required_fix"], "not-required accounting row should explain why no accounting control is required")
ok(nr["next_command"] == "", "not-required accounting row should not route a remediation command")

print(f"{passed} passed")
PY

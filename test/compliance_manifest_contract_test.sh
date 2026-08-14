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
    "premium-lane-packet",
    "premium-objective-audit",
    "materialized-source-ingest",
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
    premium_lane_rows=[
        {"path": "workpapers/premium-lane-founder-unicorn.json", "status": "fail", "failures": [{"detail": "reviewer_status"}]}
    ],
    premium_objective_audit={
        "status": "fail",
        "failures": [{"id": "trust_asset_shelter", "detail": "missing Schwab trust benchmark"}],
    },
    materialized_source_ingest={
        "required": True,
        "status": "fail",
        "missing": ["sources/local-source-ingest-ledger.json"],
    },
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
ok(
    failing_rows["premium-lane-packet"]["owner"] == "glaw-premium-lanes"
    and failing_rows["premium-lane-packet"]["next_command"] == "bin/glaw-premium-lanes status --json",
    "premium lane packet failure must route to glaw-premium-lanes",
)
ok(
    failing_rows["premium-objective-audit"]["owner"] == "glaw-premium-lanes"
    and failing_rows["premium-objective-audit"]["next_command"] == "bin/glaw-premium-lanes audit-objective --json",
    "premium objective audit failure must route to glaw-premium-lanes audit-objective",
)
ok(
    failing_rows["materialized-source-ingest"]["owner"] == "glaw-premium-lanes"
    and failing_rows["materialized-source-ingest"]["next_command"] == "bin/glaw-premium-lanes materialize-source-ingest --json",
    "materialized source-ingest failure must route to glaw-premium-lanes materialize-source-ingest",
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
    "premium_objective_audit_clear": True,
    "materialized_source_ingest_clear": True,
}
lane_specific_rows = rows_by_id(module.compliance_manifest(
    "corp-build",
    {**passing_gates, "premium_lane_packet_clear": False},
    accounting_control={"required": False, "status": "not_required", "missing": []},
    government_adversary_rows=[{"lens": "sec-offering-reviewer", "status": "pass", "missing": []}],
    source_manifest=[{"path": "evidence/source.txt", "size_bytes": 100}],
    senior_review_evidence_manifest=[{"kind": "council", "name": "corporate partner", "status": "pass", "missing": []}],
    red_flag_resolution_evidence_manifest=[],
    nonblocking_red_flags=[],
    reviewer_identity=[{"kind": "citation", "name": "legal-research", "status": "pass", "missing": []}],
    report_quality_manifest=[{"path": "packet.md", "status": "pass", "missing_markers": []}],
    premium_lane_rows=[
        {
            "path": "workpapers/premium-lane-founder-unicorn.json",
            "lane_id": "founder-unicorn",
            "status": "fail",
            "failures": [{"id": "rendered_template_missing", "detail": "missing rendered packet template"}],
            "next_command": "bin/glaw-premium-lanes render-packet --lane founder-unicorn --matter-slug founder-fixture --owner \"named lead\" --source \"SRC-0001 basis\"",
            "required_fix": "render premium lane client packet templates with report headers, findings, evidence, red flags, sign-off conditions, and UPL/human-authority footer",
        }
    ],
    premium_objective_audit={"status": "pass", "failures": []},
    materialized_source_ingest={"required": True, "status": "pass", "missing": []},
))
lane_route = lane_specific_rows["premium-lane-packet"]
ok(lane_route["status"] == "fail", "lane-specific premium row should fail in fixture")
ok(
    lane_route["next_command"] == "bin/glaw-premium-lanes render-packet --lane founder-unicorn --matter-slug founder-fixture --owner \"named lead\" --source \"SRC-0001 basis\"",
    "premium lane compliance row should use lane-specific active-matter repair command",
)
ok("workpapers/premium-lane-founder-unicorn.json" not in lane_route["next_command"], "premium lane repair command should not require direct workpaper path")
ok("<basis>" not in lane_route["next_command"] and "<lead>" not in lane_route["next_command"], "premium lane repair command should be copy-safe")

docket_route_rows = rows_by_id(module.compliance_manifest(
    "corp-build",
    {**passing_gates, "premium_lane_packet_clear": False},
    accounting_control={"required": False, "status": "not_required", "missing": []},
    government_adversary_rows=[{"lens": "sec-offering-reviewer", "status": "pass", "missing": []}],
    source_manifest=[{"path": "evidence/source.txt", "size_bytes": 100}],
    senior_review_evidence_manifest=[{"kind": "council", "name": "corporate partner", "status": "pass", "missing": []}],
    red_flag_resolution_evidence_manifest=[],
    nonblocking_red_flags=[],
    reviewer_identity=[{"kind": "citation", "name": "legal-research", "status": "pass", "missing": []}],
    report_quality_manifest=[{"path": "packet.md", "status": "pass", "missing_markers": []}],
    premium_lane_rows=[
        {
            "path": "workpapers/premium-lane-founder-unicorn.json",
            "lane_id": "founder-unicorn",
            "status": "fail",
            "check_packet_status": "pass",
            "docketed": False,
            "failures": [{"id": "docket_materialized", "detail": "docket_materialized: recurring obligations are not materialized in docket.jsonl"}],
            "next_command": "bin/glaw-premium-lanes docket --lane founder-unicorn --matter-slug founder-fixture",
            "required_fix": "materialize the premium lane recurring obligations into docket.jsonl before final-packet or file-gate reliance",
        }
    ],
    premium_objective_audit={"status": "pass", "failures": []},
    materialized_source_ingest={"required": True, "status": "pass", "missing": []},
))
docket_route = docket_route_rows["premium-lane-packet"]
ok(
    docket_route["next_command"] == "bin/glaw-premium-lanes docket --lane founder-unicorn --matter-slug founder-fixture",
    "premium lane compliance row should route packet-ready lanes to docket materialization",
)
ok("docket_materialized" in docket_route["missing"][0], "premium lane docket route should expose docket materialization blocker")

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
    premium_lane_rows=[],
    premium_objective_audit={"status": "pass", "failures": []},
    materialized_source_ingest={"required": False, "status": "not_required", "missing": []},
))
ok("accounting-control-not-required" in not_required_rows, "non-accounting profile missing not-required row")
ok("accounting-control" not in not_required_rows, "non-accounting profile incorrectly requires accounting control")
nr = not_required_rows["accounting-control-not-required"]
ok(nr["status"] == "pass", "not-required accounting row should pass")
ok(nr["owner"] == "glaw-accounting", "not-required accounting row still needs accountable owner")
ok(nr["required_fix"], "not-required accounting row should explain why no accounting control is required")
ok(nr["next_command"] == "", "not-required accounting row should not route a remediation command")
ok("premium-lane-packet" not in not_required_rows, "premium lane row should be absent when no premium packet exists")

packet_md = module.render_md({
    "matter_slug": "premium-fixture",
    "generated_at": "2026-01-01T00:00:00Z",
    "workflow_profile": "corp-build",
    "status": "ready",
    "gates": {"premium_lane_packet_clear": True},
    "blocking_red_flags": [],
    "red_flag_resolution_evidence_manifest": [],
    "nonblocking_red_flag_manifest": [],
    "council_reviews": [],
    "government_adversary_manifest": [],
    "reviewer_identity_manifest": [],
    "deliverables": [],
    "report_quality_manifest": [],
    "accounting_control_manifest": {"required": False, "status": "not_required", "missing": []},
    "premium_lane_manifest": [
        {
            "lane_id": "founder-unicorn",
            "path": "workpapers/premium-lane-founder-unicorn.json",
            "sha256": "a" * 64,
            "status": "pass",
            "failures": [],
            "rendered_templates": [
                {
                    "item": "investor tax disclosure and no-guarantee QSBS statement",
                    "path": "drafts/premium-lane-founder-unicorn/01-investor-tax-disclosure.md",
                    "bytes": 2048,
                    "sha256": "b" * 64,
                }
            ],
        }
    ],
    "premium_objective_audit_manifest": {
        "status": "pass",
        "objective": "Fortune 500 lawyer, tax system, entrepreneur/founder, investor/capital raise, QSBS, trust, and premium-lane GLAW buildout",
        "manifest_sha256": "c" * 64,
        "requirements": [
            {"id": "trust_asset_shelter", "lane_id": "uhnw-family-office", "status": "pass"}
        ],
        "firm_blueprint_status": "pass",
        "firm_blueprint_summary": {
            "phase_count": 10,
            "lanes": [
                "fortune500-enterprise",
                "tax-system",
                "founder-unicorn",
                "uhnw-family-office",
            ],
            "source_count": 6,
            "trust_type_count": 38,
            "phase_names": [
                "1. One front door: intake, conflicts, source ingest, and jurisdiction",
                "2. Fortune 500 enterprise bench",
                "3. Tax system and IRS engine",
                "4. Entrepreneur, founder, QSBS, and capital raise",
            ],
        },
        "returncode": 0,
        "failures": [],
    },
    "compliance_manifest": [],
})
ok("## Premium Lane Manifest" in packet_md, "final packet markdown missing premium lane section")
ok("workpapers/premium-lane-founder-unicorn.json" in packet_md, "final packet markdown missing premium lane workpaper")
ok("drafts/premium-lane-founder-unicorn/01-investor-tax-disclosure.md" in packet_md, "final packet markdown missing rendered template path")
ok("sha256=" + ("b" * 12) in packet_md, "final packet markdown missing rendered template hash preview")
ok("## Premium Objective Audit" in packet_md, "final packet markdown missing premium objective audit section")
ok("integrated firm blueprint: status=pass phases=10 lanes=4 sources=6 trust_types=38" in packet_md, "final packet markdown missing integrated firm blueprint summary")
ok("2. Fortune 500 enterprise bench" in packet_md, "final packet markdown missing integrated Fortune 500 phase")
ok("3. Tax system and IRS engine" in packet_md, "final packet markdown missing integrated tax-system phase")
ok("4. Entrepreneur, founder, QSBS, and capital raise" in packet_md, "final packet markdown missing integrated founder/QSBS phase")
ok("trust_asset_shelter" in packet_md, "final packet markdown missing trust objective audit row")

print(f"{passed} passed")
PY

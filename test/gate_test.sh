#!/usr/bin/env bash
# gate_test.sh — regression test for bin/glaw-gate (the code-enforced hard gates).
# Zero spend. Isolates via a temp GLAW_HOME so it never touches real matters.
# Asserts: a guarded stage is BLOCKED (exit 1) until its prerequisite gate events are
# logged, then CLEAR (exit 0); unguarded stages are always clear.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${GLAW_ROOT:-}" ]; then
  ROOT="$(cd "$GLAW_ROOT" && pwd)"
else
  ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "FATAL: cannot resolve repo root; set GLAW_ROOT explicitly" >&2
    exit 99
  }
fi
GATE="$ROOT/bin/glaw-gate"
CORPUS="$ROOT/bin/glaw-citation-corpus"
pass=0; fail=0
ok(){
  if [ "$1" = 1 ]; then
    pass=$((pass+1)); echo "  ✓ $2"
  else
    fail=$((fail+1)); echo "  ✗ FAIL: $2"
    [ -s "${TMP:-}/last-gate.err" ] && sed 's/^/      gate: /' "$TMP/last-gate.err"
  fi
}
fixture_py(){
  python3 - "$@" || {
    rc=$?
    echo "FATAL: gate_test fixture setup failed near line ${BASH_LINENO[0]} (python exit $rc)" >&2
    exit "$rc"
  }
}

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
M="$TMP/matters/m"; mkdir -p "$M"; : > "$M/timeline.jsonl"; echo m > "$TMP/.active"
log(){ printf '{"ts":"t","event":"%s"}\n' "$1" >> "$M/timeline.jsonl"; }
chk(){ "$GATE" check "$1" m >"$TMP/last-gate.err" 2>&1; echo $?; }   # echoes exit code
append_hashed_jsonl(){
  fixture_py "$1" "$2" <<'PY'
import hashlib
import json
import sys

path = sys.argv[1]
row = json.loads(sys.argv[2])
payload = dict(row)
payload.pop("row_hash", None)
row["row_hash"] = hashlib.sha256(
    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
with open(path, "a", encoding="utf-8") as f:
    f.write(json.dumps(row) + "\n")
PY
}

# unguarded transitions are always clear
ok "$([ "$(chk structure)" = 0 ] && echo 1 || echo 0)" "unguarded stage 'structure' is CLEAR"
ok "$([ "$(chk draft)" = 0 ] && echo 1 || echo 0)"     "unguarded stage 'draft' is CLEAR"

# intake + gate 1: strategy needs intake_complete and conflicts_cleared
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy BLOCKED before intake_complete + conflicts_cleared"
log intake_complete
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED with only intake_complete"
log conflicts_cleared
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED before intake/ethics artifacts"
cat > "$M/intake.json" <<'JSON'
{"status":"complete"}
JSON
cat > "$M/ethics.json" <<'JSON'
{"status":"complete","conflicts_status":"cleared","engagement":{"status":"drafted"}}
JSON
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED by incomplete structured intake artifact"
cat > "$M/intake.json" <<'JSON'
{
  "status": "complete",
  "workflow_track": "accounting-tax",
  "universal": {
    "matter_name": "Manual Gate Fixture",
    "workflow_track": "accounting-tax",
    "client_names": ["Acme Inc."],
    "parties": ["Acme Inc.", "Bank"],
    "jurisdiction": "Florida",
    "goal": "reconstruct books and tax package",
    "source_documents": ["bank.csv"],
    "deadlines": ["2026-09-15 tax filing"],
    "facts_timeline": ["2026-01-01 opening balance"],
    "open_questions": ["none"],
    "conflicts_parties": ["Acme Inc.", "Bank"],
    "authorized_scope": "review and draft only"
  },
  "track_specific": {
    "bank_statement_sources": "bank.csv",
    "tax_years": "2026",
    "entity_tax_type": "C-corp",
    "books_status": "raw statements",
    "irs_forms_needed": "1120"
  },
  "review": {
    "completed_by": "intake reviewer"
  }
}
JSON
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED by generic intake reviewer"
fixture_py "$M/intake.json" <<'PY'
import json, sys
p = sys.argv[1]
data = json.load(open(p, encoding="utf-8"))
data["review"]["completed_by"] = "Jordan Lee, intake counsel"
open(p, "w", encoding="utf-8").write(json.dumps(data) + "\n")
PY
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED by unsourced ethics artifact"
cat > "$M/ethics.json" <<'JSON'
{
  "status": "complete",
  "conflicts_status": "cleared",
  "conflicts_notes": "no conflict in fixture",
  "conflicts_source": "SRC-0001 party list reviewed",
  "engagement": {
    "status": "drafted",
    "scope": "review and draft only",
    "responsible_professional": "Alex Rivera, licensed attorney",
    "source": "SRC-0001 authorized scope reviewed"
  },
  "upl_footer": "Attorney work-product - not legal advice."
}
JSON
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED before current source evidence file"
mkdir -p "$M/evidence"
printf 'date,description,amount\n2026-01-01,capital deposit,100.00\n' > "$M/evidence/bank.csv"
cat > "$M/ethics.json" <<'JSON'
{
  "status": "complete",
  "conflicts_status": "cleared",
  "conflicts_notes": "no conflict in fixture",
  "conflicts_source": "SRC-9999 stale party list reviewed",
  "engagement": {
    "status": "drafted",
    "scope": "review and draft only",
    "responsible_professional": "Alex Rivera, licensed attorney",
    "source": "SRC-9999 stale authorized scope reviewed"
  },
  "upl_footer": "Attorney work-product - not legal advice."
}
JSON
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED by stale ethics source id"
cat > "$M/ethics.json" <<'JSON'
{
  "status": "complete",
  "conflicts_status": "cleared",
  "conflicts_notes": "no conflict in fixture",
  "conflicts_source": "SRC-0001 party list reviewed",
  "engagement": {
    "status": "drafted",
    "scope": "review and draft only",
    "responsible_professional": "licensed reviewer",
    "source": "SRC-0001 authorized scope reviewed"
  },
  "upl_footer": "Attorney work-product - not legal advice."
}
JSON
ok "$([ "$(chk strategy)" = 1 ] && echo 1 || echo 0)" "strategy STILL BLOCKED by generic ethics responsible professional"
cat > "$M/ethics.json" <<'JSON'
{
  "status": "complete",
  "conflicts_status": "cleared",
  "conflicts_notes": "no conflict in fixture",
  "conflicts_source": "SRC-0001 party list reviewed",
  "engagement": {
    "status": "drafted",
    "scope": "review and draft only",
    "responsible_professional": "Alex Rivera, licensed attorney",
    "source": "SRC-0001 authorized scope reviewed"
  },
  "upl_footer": "Attorney work-product - not legal advice."
}
JSON
ok "$([ "$(chk strategy)" = 0 ] && echo 1 || echo 0)" "strategy CLEAR after current-source intake/ethics artifacts"

# file gate: citations, adversarial, red flags, final packet, and chief approval
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED with no file gates"
log citations_verified
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED with only citations_verified"
log adversarial_done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before red_flags_clear"
log red_flags_clear
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before final_packet_ready"
log final_packet_ready
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before chief_approved"
log chief_approved
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED before verified final packet artifacts"
cat > "$M/final_packet.json" <<'JSON'
{
  "status": "ready",
  "generated_at": "2026-01-01T00:00:00Z",
  "workflow_profile": "accounting-tax",
  "gates": {
    "intake_complete": true,
    "intake_artifact_clear": true,
    "conflicts_cleared": true,
    "ethics_gate_complete": true,
    "citations_verified": true,
    "citation_gate_complete": true,
    "adversarial_done": true,
    "accounting_adversarial_complete": true,
    "accounting_council_complete": true,
    "red_flags_clear": true,
    "red_flag_resolution_evidence_clear": true,
    "nonblocking_red_flags_accounted_clear": true,
    "external_deliverable_present": true,
    "source_evidence_manifest_clear": true,
    "senior_review_evidence_source_clear": true,
    "government_adversary_manifest_clear": true,
    "compliance_manifest_clear": true,
    "professional_report_manifest_clear": true,
    "upl_footer_clear": true
  }
}
JSON
fixture_py "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
import hashlib, json, sys
packet = sys.argv[2]
row = {
    "final_gate": "approved",
    "decision": "PROCEED",
    "approved_packet_generated_at": "2025-12-31T00:00:00Z",
    "approved_packet_sha256": hashlib.sha256(open(packet, "rb").read()).hexdigest(),
    "score": "95",
    "grade": "A",
    "top_risks": ["none"],
    "conditions": ["licensed signer final review"],
    "rationale": "SRC-0001 all gates clear and source manifests tie out",
}
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED when Chief approval references stale packet"
fixture_py "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
import hashlib, json, sys
packet = sys.argv[2]
row = {
    "final_gate": "approved",
    "decision": "PROCEED",
    "approved_packet_generated_at": "2026-01-01T00:00:00Z",
    "approved_packet_sha256": "stale-packet-hash",
    "score": "95",
    "grade": "A",
    "top_risks": ["none"],
    "conditions": ["licensed signer final review"],
    "rationale": "SRC-0001 all gates clear and source manifests tie out",
}
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED when Chief approval references stale packet hash"
fixture_py "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
import hashlib, json, sys
packet = sys.argv[2]
row = {
    "final_gate": "approved",
    "decision": "PROCEED",
    "approved_packet_generated_at": "2026-01-01T00:00:00Z",
    "approved_packet_sha256": hashlib.sha256(open(packet, "rb").read()).hexdigest(),
    "score": "95",
    "grade": "A",
    "top_risks": ["none"],
    "conditions": ["licensed signer final review"],
    "rationale": "SRC-0001 all gates clear and source manifests tie out",
}
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before verified citation ledger artifact"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by incomplete verified citation row"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/","reviewer":"legal-research"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by verified citation without support summary"
printf '%s\n' "26 U.S.C. 6001 requires tax return records to tie to books and establish tax liability." > "$TMP/usc-6001.txt"
"$CORPUS" capture --id CORP-1 --source-url "https://uscode.house.gov/" --file "$TMP/usc-6001.txt" --authenticated-copy --segment "tax return records to tie to books and establish tax liability" >/dev/null
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/","reviewer":"legal-research","support_summary":"The source segment says tax return records tie to books and establish tax liability.","corpus_id":"CORP-1"}'
"$ROOT/bin/glaw-groundedness" audit >/dev/null
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before current council ledger artifact"
for role in cfo tax-strategist irs-audit-agent legal-counsel forensic-audit accounting-reviewer outside-critic external-reviewer; do
  append_hashed_jsonl "$M/council.jsonl" "{\"profile\":\"accounting-tax\",\"role\":\"$role\",\"decision\":\"approve\",\"evidence\":\"SRC-0001 fixture\",\"notes\":\"$role source-backed approval conclusion\"}"
done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before current adversarial ledger artifact"
for lens in irs-examiner state-tax-auditor tax-court-counsel penalty-reviewer forensic-accountant cfo-controller outside-critic; do
  append_hashed_jsonl "$M/adversarial.jsonl" "{\"profile\":\"accounting-tax\",\"lens\":\"$lens\",\"decision\":\"survive\",\"attack\":\"SRC-0001 $lens no fatal challenge after source review\",\"evidence\":\"SRC-0001 fixture\"}"
done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before current external deliverable artifact"
printf '# Draft Report\n\nNumbers tie.\n' > "$M/draft-report.md"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current deliverable missing UPL footer"
printf '\nAttorney work-product - not legal advice. Prepared for licensed review.\n' >> "$M/draft-report.md"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before professional report quality manifest"
cat > "$M/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source; [CLIENT] placeholder remains.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by unresolved current report placeholder"
cat > "$M/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source. REVIEW: asset register not provided.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by unresolved current REVIEW marker"
cat > "$M/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
fixture_py "$M" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
markers = ["Owner:", "Report voice:", "Findings:", "Evidence:", "Red flags:", "Sign-off conditions:"]
packet["report_quality_required_markers"] = markers
packet["report_quality_manifest"] = [{
    "path": "draft-report.md",
    "status": "fail",
    "missing_markers": ["source evidence manifest"],
    "cited_source_ids": [],
    "unresolved_placeholders": [],
    "unresolved_review_markers": [],
}]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before source evidence manifest"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
source = d / "evidence/bank.csv"
packet["source_evidence_manifest"] = [{
    "id": "SRC-0001",
    "path": "evidence/bank.csv",
    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "size_bytes": source.stat().st_size,
}]
packet["senior_review_evidence_manifest"] = [
    {
        "kind": "council",
        "name": name,
        "status": "pass",
        "missing": [],
        "cited_source_ids": ["SRC-0001"],
    }
    for name in [
        "cfo",
        "tax-strategist",
        "irs-audit-agent",
        "legal-counsel",
        "forensic-audit",
        "accounting-reviewer",
        "outside-critic",
        "external-reviewer",
    ]
] + [
    {
        "kind": "adversarial",
        "name": name,
        "status": "pass",
        "missing": [],
        "cited_source_ids": ["SRC-0001"],
        "attack_cited_source_ids": ["SRC-0001"],
    }
    for name in [
        "irs-examiner",
        "state-tax-auditor",
        "tax-court-counsel",
        "penalty-reviewer",
        "forensic-accountant",
        "cfo-controller",
        "outside-critic",
    ]
]
packet["government_adversary_manifest"] = [
    {
        "lens": name,
        "status": "pass",
        "missing": [],
        "evidence_cited_source_ids": ["SRC-0001"],
        "attack_cited_source_ids": ["SRC-0001"],
    }
    for name in [
        "irs-examiner",
        "state-tax-auditor",
        "tax-court-counsel",
        "penalty-reviewer",
    ]
]
packet["red_flag_resolution_evidence_manifest"] = []
packet["nonblocking_red_flag_manifest"] = []
packet["report_quality_manifest"] = [{
    "path": "draft-report.md",
    "status": "pass",
    "missing_markers": [],
    "cited_source_ids": ["SRC-0001"],
    "unresolved_placeholders": [],
    "unresolved_review_markers": [],
}]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
printf '{"id":"RF-MED","severity":"medium","status":"open","finding":"watch item","source":"SRC-0001 bank statement"}\n' > "$M/red_flags.jsonl"
fixture_py "$M" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["nonblocking_red_flag_manifest"] = [{
    "id": "RF-MED",
    "severity": "medium",
    "status": "fail",
    "missing": ["owner", "required_fix"],
    "owner": "",
    "required_fix": "",
    "finding": "watch item",
    "cited_source_ids": ["SRC-0001"],
    "referenced_source_ids": ["SRC-0001"],
}]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by unowned nonblocking medium red flag"
printf '{"id":"RF-MED","severity":"medium","status":"open","finding":"watch item","owner":"controller","required_fix":"carry in Chief conditions until closed","source":"SRC-0001 bank statement"}\n' > "$M/red_flags.jsonl"
fixture_py "$M" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["nonblocking_red_flag_manifest"] = [{
    "id": "RF-MED",
    "severity": "medium",
    "status": "pass",
    "missing": [],
    "owner": "controller",
    "required_fix": "carry in Chief conditions until closed",
    "finding": "watch item",
    "cited_source_ids": ["SRC-0001"],
    "referenced_source_ids": ["SRC-0001"],
}]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "source-backed nonblocking medium red flag proceeds to next gate"
fixture_py "$M" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["government_adversary_manifest"] = [
    row for row in packet["government_adversary_manifest"] if row["lens"] != "irs-examiner"
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by stale government adversary manifest"
fixture_py "$M" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["government_adversary_manifest"] = [
    {
        "lens": name,
        "status": "pass",
        "missing": [],
        "evidence_cited_source_ids": ["SRC-0001"],
        "attack_cited_source_ids": ["SRC-0001"],
    }
    for name in [
        "irs-examiner",
        "state-tax-auditor",
        "tax-court-counsel",
        "penalty-reviewer",
    ]
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before accounting control manifest"
mkdir -p "$M/workpapers"
printf '{"rows":[],"audit":[]}\n' > "$M/workpapers/ledger.json"
printf 'books doctor pass\n' > "$M/workpapers/books-doctor.txt"
printf '{"reconciled":true,"unreconciled_difference":"0","book_only":[],"bank_only":[]}\n' > "$M/workpapers/bank-rec.json"
cat > "$M/workpapers/tax-tieout.json" <<'JSON'
{
  "schema_version": 1,
  "source_tool": "glaw-tax-tieout",
  "mode": "recompute",
  "recomputed_total_provision": "21.00",
  "posted_income_tax_expense": "21.00",
  "provision_ties": true,
  "internal": {
    "schema_version": 1,
    "source_tool": "glaw-tax-tieout",
    "mode": "internal-consistency",
    "income_tax_expense": "21.00",
    "income_tax_payable": "21.00",
    "deferred_tax_liability": "0.00",
    "deferred_tax_asset": "0.00",
    "expense_should_equal": "21.00",
    "consistent": true,
    "has_tax": true
  }
}
JSON
cat > "$M/accounting_control.json" <<'JSON'
{
  "schema_version": 1,
  "status": "pass",
  "source": "SRC-0001 bank statement, ledger, bank reconciliation, and tax tie-out source package",
  "ledger": {
    "status": "pass",
    "artifact": "workpapers/ledger.json"
  },
  "books_doctor": {
    "status": "pass",
    "artifact": "workpapers/books-doctor.txt",
    "require_rec": true
  },
  "bank_reconciliation": {
    "status": "pass",
    "artifact": "workpapers/bank-rec.json",
    "reconciled": true,
    "unreconciled_difference": "0",
    "book_only_count": 0,
    "bank_only_count": 0
  }
}
JSON
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
control = d / "accounting_control.json"
packet["accounting_control_manifest"] = {
    "required": True,
    "path": "accounting_control.json",
    "status": "pass",
    "missing": [],
    "sha256": hashlib.sha256(control.read_bytes()).hexdigest(),
    "artifact_hashes": [
        {
            "label": "ledger",
            "path": "workpapers/ledger.json",
            "sha256": hashlib.sha256((d / "workpapers/ledger.json").read_bytes()).hexdigest(),
            "size_bytes": (d / "workpapers/ledger.json").stat().st_size,
        },
        {
            "label": "books_doctor",
            "path": "workpapers/books-doctor.txt",
            "sha256": hashlib.sha256((d / "workpapers/books-doctor.txt").read_bytes()).hexdigest(),
            "size_bytes": (d / "workpapers/books-doctor.txt").stat().st_size,
        },
        {
            "label": "bank_reconciliation",
            "path": "workpapers/bank-rec.json",
            "sha256": hashlib.sha256((d / "workpapers/bank-rec.json").read_bytes()).hexdigest(),
            "size_bytes": (d / "workpapers/bank-rec.json").stat().st_size,
        },
    ],
}
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before accounting-tax tax tie-out"
fixture_py "$M/accounting_control.json" <<'PY'
import json, sys
p = sys.argv[1]
control = json.loads(open(p, encoding="utf-8").read())
control["tax_tieout"] = {
    "status": "pass",
    "artifact": "workpapers/tax-tieout.json",
    "provision_ties": True,
    "internal_consistency": True,
}
open(p, "w", encoding="utf-8").write(json.dumps(control) + "\n")
PY
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
control = d / "accounting_control.json"
packet["accounting_control_manifest"]["sha256"] = hashlib.sha256(control.read_bytes()).hexdigest()
packet["accounting_control_manifest"]["artifact_hashes"].append(
    {
        "label": "tax_tieout",
        "path": "workpapers/tax-tieout.json",
        "sha256": hashlib.sha256((d / "workpapers/tax-tieout.json").read_bytes()).hexdigest(),
        "size_bytes": (d / "workpapers/tax-tieout.json").stat().st_size,
    }
)
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before reviewer identity manifest"
fixture_py "$M" "$ROOT" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root / "lib"))
from glaw_profiles import ADVERSARIAL_PROFILES, COUNCIL_PROFILES, REVIEWER_SKILL_MAP

def skill_name(path):
    in_frontmatter = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter and line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""

def skill_path_for(command):
    matches = [p for p in root.rglob("SKILL.md") if ".git" not in p.parts and skill_name(p) == command]
    return sorted(matches, key=lambda p: ("seats" in p.relative_to(root).parts, str(p.relative_to(root))))[0]

def row(kind, name):
    command = REVIEWER_SKILL_MAP[name]
    path = skill_path_for(command)
    return {
        "kind": kind,
        "name": name,
        "skill": command,
        "path": str(path.relative_to(root)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "status": "pass",
        "missing": [],
    }

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
profile = packet["workflow_profile"]
packet["reviewer_identity_manifest"] = (
    [row("citation", "legal-research")]
    + [row("council", name) for name in COUNCIL_PROFILES[profile]]
    + [row("adversarial", name) for name in ADVERSARIAL_PROFILES[profile]]
)
routes = {
    "ethics-upl": ("bin/glaw-ethics status", "clear conflicts, engagement, and UPL footer evidence"),
    "citation-grounding": ("bin/glaw-citation-gate status", "verify citations against the captured source corpus"),
    "government-adversary": ("bin/glaw-adversarial status --profile auto", "record surviving government/regulatory/litigation adversary attacks"),
    "senior-review-source-support": ("bin/glaw-council status --profile auto", "obtain source-backed senior reviewer approval notes"),
    "red-flag-accountability": ("bin/glaw-red-flags status", "resolve blocking red flags and account for nonblocking flags"),
    "source-evidence-chain": ("bin/glaw-final-packet build --profile auto", "refresh the source evidence manifest from current matter files"),
    "professional-report-quality": ("bin/glaw-upl-check", "fix external reports so they carry owner, voice, findings, evidence, red flags, sign-off conditions, sources, and no placeholders"),
    "reviewer-identity": ("bin/glaw-doctor", "repair reviewer skill mapping or identity markers"),
    "accounting-control": ("bin/glaw-accounting-control", "run books-doctor, bank reconciliation, ledger, tax tie-out, and SEC audit tie-out controls"),
}
def compliance(row_id, owner):
    next_command, required_fix = routes[row_id]
    return {
        "id": row_id,
        "owner": owner,
        "status": "pass",
        "missing": [],
        "next_command": next_command,
        "required_fix": required_fix,
    }
packet["compliance_manifest"] = [
    compliance("ethics-upl", "glaw-ethics-conflicts"),
    compliance("citation-grounding", "glaw-legal-research"),
    compliance("government-adversary", "glaw-adversarial"),
    compliance("senior-review-source-support", "glaw-council"),
    compliance("red-flag-accountability", "glaw-red-flags"),
    compliance("source-evidence-chain", "glaw-final-packet"),
    compliance("professional-report-quality", "glaw-legal-writing"),
    compliance("reviewer-identity", "glaw-final-packet"),
    compliance("accounting-control", "glaw-accounting"),
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before deliverable hash manifest"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
p = d / "draft-report.md"
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["external_text_deliverables"] = ["draft-report.md"]
packet["external_text_deliverable_hashes"] = {"draft-report.md": hashlib.sha256(p.read_bytes()).hexdigest()}
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before gate artifact hash manifest"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
names = ["intake.json", "ethics.json", "citation_corpus.jsonl", "citations.jsonl", "groundedness.json", "council.jsonl", "adversarial.jsonl", "accounting_control.json"]
if (d / "red_flags.jsonl").exists():
    names.append("red_flags.jsonl")
packet["gate_artifact_hashes"] = {
    name: hashlib.sha256((d / name).read_bytes()).hexdigest()
    for name in names
}
md = "# GLAW Final Packet\n\nManual gate fixture.\n"
(d / "final_packet.md").write_text(md, encoding="utf-8")
packet["final_packet_md_sha256"] = hashlib.sha256(md.encode("utf-8")).hexdigest()
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
fixture_py "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
import hashlib, json, sys
packet = sys.argv[2]
row = {
    "final_gate": "approved",
    "decision": "PROCEED",
    "approved_packet_generated_at": "2026-01-01T00:00:00Z",
    "approved_packet_sha256": hashlib.sha256(open(packet, "rb").read()).hexdigest(),
    "score": "95",
    "grade": "A",
    "top_risks": ["none"],
    "conditions": ["licensed signer final review"],
    "rationale": "SRC-0001 all gates clear and source manifests tie out",
}
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED when Chief approval omits open nonblocking red flag"
fixture_py "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
import hashlib, json, sys
packet = sys.argv[2]
row = {
    "final_gate": "approved",
    "decision": "PROCEED",
    "approved_packet_generated_at": "2026-01-01T00:00:00Z",
    "approved_packet_sha256": hashlib.sha256(open(packet, "rb").read()).hexdigest(),
    "score": "95",
    "grade": "A",
    "top_risks": ["RF-MED remains open as a nonblocking watch item"],
    "conditions": ["licensed signer final review; RF-MED carried until closed"],
    "rationale": "SRC-0001 all gates clear and source manifests tie out",
}
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after all file gates"
cp "$M/final_packet.json" "$M/final_packet.compliance-baseline.json"
cp "$M/groundedness.json" "$M/groundedness.baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.baseline.jsonl"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
ground_path = d / "groundedness.json"
ground = json.loads(ground_path.read_text(encoding="utf-8"))
ground["rows"][0]["entity_grounding"] = 1.0
ground["rows"][0]["missing_proposition_tokens"] = ["manually-corrupted"]
ground_path.write_text(json.dumps(ground) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
packet["gate_artifact_hashes"]["groundedness.json"] = hashlib.sha256(ground_path.read_bytes()).hexdigest()
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
row = json.loads(decision_path.read_text(encoding="utf-8").splitlines()[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
decision_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by stale groundedness artifact despite matching packet hashes"
cp "$M/final_packet.compliance-baseline.json" "$M/final_packet.json"
cp "$M/groundedness.baseline.json" "$M/groundedness.json"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
fixture_py "$M/final_packet.json" <<'PY'
import json, sys
p = sys.argv[1]
packet = json.load(open(p, encoding="utf-8"))
packet["compliance_manifest"] = [
    row for row in packet["compliance_manifest"] if row["id"] != "government-adversary"
]
open(p, "w", encoding="utf-8").write(json.dumps(packet) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by stale compliance manifest"
cp "$M/final_packet.compliance-baseline.json" "$M/final_packet.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact compliance manifest restored"
cp "$M/final_packet.json" "$M/final_packet.profile-baseline.json"
fixture_py "$M/final_packet.json" <<'PY'
import json, sys
p = sys.argv[1]
packet = json.load(open(p, encoding="utf-8"))
packet["workflow_profile"] = "tax"
open(p, "w", encoding="utf-8").write(json.dumps(packet) + "\n")
PY
"$GATE" check file m >"$TMP/profile-mismatch.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'does not match intake workflow profile accounting' "$TMP/profile-mismatch.out" && echo 1 || echo 0)" "file BLOCKED by final packet profile mismatch with intake"
cp "$M/final_packet.profile-baseline.json" "$M/final_packet.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact final packet profile restored"
cp "$M/workpapers/ledger.json" "$M/workpapers/ledger.baseline.json"
printf '{"rows":[{"tampered":true}]}\n' > "$M/workpapers/ledger.json"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet accounting ledger tamper"
cp "$M/workpapers/ledger.baseline.json" "$M/workpapers/ledger.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact accounting ledger restored"
cp "$M/workpapers/books-doctor.txt" "$M/workpapers/books-doctor.baseline.txt"
printf 'tampered workpaper\n' >> "$M/workpapers/books-doctor.txt"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet accounting workpaper tamper"
cp "$M/workpapers/books-doctor.baseline.txt" "$M/workpapers/books-doctor.txt"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact accounting workpaper restored"
cp "$M/final_packet.json" "$M/final_packet.accounting-baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.accounting-baseline.jsonl"
cp "$M/workpapers/bank-rec.json" "$M/workpapers/bank-rec.baseline.json"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
rec_path = d / "workpapers/bank-rec.json"
rec_path.write_text(json.dumps({
    "reconciled": False,
    "unreconciled_difference": "1.00",
    "book_only": [{"id": "B1"}],
    "bank_only": [],
}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
for item in manifest["artifact_hashes"]:
    if item["label"] == "bank_reconciliation":
        item["sha256"] = hashlib.sha256(rec_path.read_bytes()).hexdigest()
        item["size_bytes"] = rec_path.stat().st_size
manifest["status"] = "fail"
manifest["missing"] = [
    "bank_reconciliation.artifact.reconciled=true",
    "bank_reconciliation.artifact.unreconciled_difference=0",
    "bank_reconciliation.artifact.book_only empty",
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
row = json.loads(decision_path.read_text(encoding="utf-8").splitlines()[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
decision_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
PY
"$GATE" check file m >"$TMP/bank-rec-content.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'current accounting control is incomplete' "$TMP/bank-rec-content.out" && echo 1 || echo 0)" "file BLOCKED by bank-rec workpaper content even with matching packet hashes"
cp "$M/final_packet.accounting-baseline.json" "$M/final_packet.json"
cp "$M/decisions.accounting-baseline.jsonl" "$M/decisions.jsonl"
cp "$M/workpapers/bank-rec.baseline.json" "$M/workpapers/bank-rec.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact bank-rec workpaper restored"
cp "$M/final_packet.json" "$M/final_packet.accounting-baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.accounting-baseline.jsonl"
cp "$M/workpapers/bank-rec.json" "$M/workpapers/bank-rec.baseline.json"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
rec_path = d / "workpapers/bank-rec.json"
rec_path.write_text(json.dumps({
    "reconciled": True,
    "unreconciled_difference": "0.00",
}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
for item in manifest["artifact_hashes"]:
    if item["label"] == "bank_reconciliation":
        item["sha256"] = hashlib.sha256(rec_path.read_bytes()).hexdigest()
        item["size_bytes"] = rec_path.stat().st_size
manifest["status"] = "fail"
manifest["missing"] = [
    "bank_reconciliation.artifact.book_only array",
    "bank_reconciliation.artifact.bank_only array",
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
row = json.loads(decision_path.read_text(encoding="utf-8").splitlines()[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
decision_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
PY
"$GATE" check file m >"$TMP/bank-rec-schema.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'current accounting control is incomplete' "$TMP/bank-rec-schema.out" && echo 1 || echo 0)" "file BLOCKED by bank-rec workpaper missing explicit exception arrays"
cp "$M/final_packet.accounting-baseline.json" "$M/final_packet.json"
cp "$M/decisions.accounting-baseline.jsonl" "$M/decisions.jsonl"
cp "$M/workpapers/bank-rec.baseline.json" "$M/workpapers/bank-rec.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact bank-rec schema restored"
cp "$M/final_packet.json" "$M/final_packet.accounting-baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.accounting-baseline.jsonl"
cp "$M/workpapers/tax-tieout.json" "$M/workpapers/tax-tieout.baseline.json"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
tax_path = d / "workpapers/tax-tieout.json"
tax_path.write_text(json.dumps({
    "provision_ties": False,
    "internal": {"consistent": False},
}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
found = False
for item in manifest["artifact_hashes"]:
    if item["label"] == "tax_tieout":
        found = True
        item["sha256"] = hashlib.sha256(tax_path.read_bytes()).hexdigest()
        item["size_bytes"] = tax_path.stat().st_size
if not found:
    manifest["artifact_hashes"].append({
        "label": "tax_tieout",
        "path": "workpapers/tax-tieout.json",
        "sha256": hashlib.sha256(tax_path.read_bytes()).hexdigest(),
        "size_bytes": tax_path.stat().st_size,
    })
manifest["status"] = "fail"
manifest["missing"] = [
    "tax_tieout.artifact.schema_version=1",
    "tax_tieout.artifact.source_tool=glaw-tax-tieout",
    "tax_tieout.artifact.mode=recompute",
    "tax_tieout.artifact.recomputed_total_provision decimal",
    "tax_tieout.artifact.posted_income_tax_expense decimal",
    "tax_tieout.artifact.provision_ties=true",
    "tax_tieout.artifact.internal.source_tool=glaw-tax-tieout",
    "tax_tieout.internal.artifact.income_tax_expense decimal",
    "tax_tieout.internal.artifact.expense_should_equal decimal",
    "tax_tieout.artifact.internal.consistent=true",
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
row = json.loads(decision_path.read_text(encoding="utf-8").splitlines()[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
decision_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
PY
"$GATE" check file m >"$TMP/tax-tieout-content.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -Eq 'current accounting control (is incomplete|manifest does not match)' "$TMP/tax-tieout-content.out" && echo 1 || echo 0)" "file BLOCKED by tax tie-out workpaper content even with matching packet hashes"
cp "$M/final_packet.accounting-baseline.json" "$M/final_packet.json"
cp "$M/decisions.accounting-baseline.jsonl" "$M/decisions.jsonl"
cp "$M/workpapers/tax-tieout.baseline.json" "$M/workpapers/tax-tieout.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact tax tie-out workpaper restored"
cp "$M/final_packet.json" "$M/final_packet.accounting-baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.accounting-baseline.jsonl"
cp "$M/workpapers/tax-tieout.json" "$M/workpapers/tax-tieout.baseline.json"
fixture_py "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
tax_path = d / "workpapers/tax-tieout.json"
tax_path.write_text(json.dumps({"consistent": True}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
found = False
for item in manifest["artifact_hashes"]:
    if item["label"] == "tax_tieout":
        found = True
        item["sha256"] = hashlib.sha256(tax_path.read_bytes()).hexdigest()
        item["size_bytes"] = tax_path.stat().st_size
if not found:
    manifest["artifact_hashes"].append({
        "label": "tax_tieout",
        "path": "workpapers/tax-tieout.json",
        "sha256": hashlib.sha256(tax_path.read_bytes()).hexdigest(),
        "size_bytes": tax_path.stat().st_size,
    })
manifest["status"] = "fail"
manifest["missing"] = [
    "tax_tieout.artifact.schema_version=1",
    "tax_tieout.artifact.source_tool=glaw-tax-tieout",
    "tax_tieout.artifact.mode=recompute",
    "tax_tieout.artifact.recomputed_total_provision decimal",
    "tax_tieout.artifact.posted_income_tax_expense decimal",
    "tax_tieout.artifact.provision_ties=true",
    "tax_tieout.artifact.internal object",
]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
row = json.loads(decision_path.read_text(encoding="utf-8").splitlines()[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
decision_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
PY
"$GATE" check file m >"$TMP/tax-tieout-schema.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -Eq 'current accounting control (is incomplete|manifest does not match)' "$TMP/tax-tieout-schema.out" && echo 1 || echo 0)" "file BLOCKED by tax tie-out workpaper schema shortcut even with matching packet hashes"
cp "$M/final_packet.accounting-baseline.json" "$M/final_packet.json"
cp "$M/decisions.accounting-baseline.jsonl" "$M/decisions.jsonl"
cp "$M/workpapers/tax-tieout.baseline.json" "$M/workpapers/tax-tieout.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact tax tie-out schema restored"
cp "$M/accounting_control.json" "$M/accounting_control.baseline.json"
fixture_py "$M/accounting_control.json" <<'PY'
import json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["bank_reconciliation"]["unreconciled_difference"] = "1.00"
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet accounting control tamper"
cp "$M/accounting_control.baseline.json" "$M/accounting_control.json"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact accounting control restored"
cp "$M/decisions.jsonl" "$M/decisions.baseline.jsonl"
fixture_py "$M/decisions.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["decision"] = "tampered after approval"
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-approval Chief decision tamper"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact Chief decision restored"
fixture_py "$M/decisions.jsonl" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["score"] = "89"
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by Chief approval score below threshold"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after Chief approval score restored"
fixture_py "$M/decisions.jsonl" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["grade"] = "B"
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by non-A Chief approval grade"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after Chief approval grade restored"
fixture_py "$M/decisions.jsonl" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["rationale"] = "all gates clear but no source citation"
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by Chief approval rationale without source evidence id"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after source-backed Chief decision restored"
fixture_py "$M/decisions.jsonl" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["rationale"] = "SRC-0001 current source plus SRC-9999 stale source"
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by Chief approval rationale with stale source evidence id"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after stale Chief rationale source restored"
fixture_py "$M/decisions.jsonl" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["decision"] = "DENY"
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by contradictory Chief approval decision"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after consistent Chief decision restored"
printf '# Draft Report\n\nNumbers changed after packet.\n' > "$M/draft-report.md"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet deliverable losing UPL footer"
printf '\nAttorney work-product - not legal advice. Prepared for licensed review.\n' >> "$M/draft-report.md"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet deliverable report-quality/hash change"
cat > "$M/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: Test fixture ledger and bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED when restored report omits source evidence id"
cat > "$M/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact source-cited deliverable restored"
cp "$M/red_flags.jsonl" "$M/red_flags.baseline.jsonl"
fixture_py "$M/red_flags.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["required_fix"] = ""
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-packet nonblocking red flag accountability tamper"
cp "$M/red_flags.baseline.jsonl" "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact nonblocking red flag ledger restored"
fixture_py "$M/red_flags.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["source"] = "SRC-0001 bank statement plus SRC-9999 stale extract"
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by nonblocking red flag with stale source evidence id"
cp "$M/red_flags.baseline.jsonl" "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after stale nonblocking red flag source restored"
printf '{"id":"RF-STALE","severity":"high","status":"open","finding":"new post-packet issue"}\n' > "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet high red flag"
printf '{"id":"RF-STALE","severity":"high","status":"resolved","finding":"new post-packet issue","resolution_evidence":"fixed"}\n' > "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED by new post-packet red flag ledger after resolution"
cp "$M/red_flags.baseline.jsonl" "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact red flag ledger restored"
cp "$M/citations.jsonl" "$M/citations.baseline.jsonl"
cp "$M/council.jsonl" "$M/council.baseline.jsonl"
cp "$M/adversarial.jsonl" "$M/adversarial.baseline.jsonl"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"weak","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/","defect_type":"ungrounded"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet weak citation"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by verified citation without legal-research reviewer"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://","reviewer":"legal-research"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by malformed verified citation source URL"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/","reviewer":"legal-research","support_summary":"The cited section supports keeping records that substantiate tax positions.","corpus_id":"CORP-1"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED by citation ledger hash change after re-verification"
cp "$M/citations.baseline.jsonl" "$M/citations.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact citation ledger restored"
append_hashed_jsonl "$M/council.jsonl" '{"profile":"accounting","role":"cfo","decision":"fix","red_flags":["new council issue"],"conditions":["fix it"]}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet council fix"
append_hashed_jsonl "$M/council.jsonl" '{"profile":"accounting","role":"cfo","decision":"approve","evidence":"SRC-0001 fixture reapproval","notes":"cfo source-backed reapproval conclusion"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED by council ledger hash change after reapproval"
cp "$M/council.baseline.jsonl" "$M/council.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact council ledger restored"
append_hashed_jsonl "$M/adversarial.jsonl" '{"profile":"accounting","lens":"irs-examiner","decision":"fix","attack":"new adversarial issue","cure":"fix it"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet adversarial fix"
append_hashed_jsonl "$M/adversarial.jsonl" '{"profile":"accounting","lens":"irs-examiner","decision":"survive","attack":"irs examiner no fatal challenge after rescore","evidence":"SRC-0001 fixture rescore"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by adversarial survival attack without source evidence id"
append_hashed_jsonl "$M/adversarial.jsonl" '{"profile":"accounting","lens":"irs-examiner","decision":"survive","attack":"SRC-0001 irs examiner no fatal challenge after rescore","evidence":"SRC-0001 fixture rescore"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED by adversarial ledger hash change after survival"
cp "$M/adversarial.baseline.jsonl" "$M/adversarial.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact adversarial ledger restored"

ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro BLOCKED before docket gate"
log docket_gate_complete
ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro STILL BLOCKED before docket_done"
log docket_done
ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro STILL BLOCKED before docket artifacts"
printf '{"due":"2026-09-15","desc":"tax filing","status":"open"}\n' > "$M/docket.jsonl"
ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro STILL BLOCKED by unsourced docket row"
printf '{"due":"2026-09-15","desc":"tax filing","status":"open","owner":"tax docket clerk","source":"SRC-9999 stale intake deadline"}\n' > "$M/docket.jsonl"
ok "$([ "$(chk matter-retro)" = 1 ] && echo 1 || echo 0)" "matter-retro STILL BLOCKED by non-current docket source id"
printf '{"due":"2026-09-15","desc":"tax filing","status":"open","owner":"tax docket clerk","source":"SRC-0001 intake deadline"}\n' > "$M/docket.jsonl"
ok "$([ "$(chk matter-retro)" = 0 ] && echo 1 || echo 0)" "matter-retro CLEAR after docket completion"

# status reflects state
S="$("$GATE" status m 2>&1)"
ok "$(echo "$S" | grep -q '✅ conflicts_cleared' && echo 1 || echo 0)" "status shows conflicts_cleared ✅"
ok "$(echo "$S" | grep -q '✅ intake_complete' && echo 1 || echo 0)" "status shows intake_complete ✅"
ok "$(echo "$S" | grep -q '✅ adversarial_done' && echo 1 || echo 0)" "status shows adversarial_done ✅"
ok "$(echo "$S" | grep -q '✅ red_flags_clear' && echo 1 || echo 0)" "status shows red_flags_clear ✅"
ok "$(echo "$S" | grep -q '✅ final_packet_ready' && echo 1 || echo 0)" "status shows final_packet_ready ✅"
ok "$(echo "$S" | grep -q '✅ chief_approved' && echo 1 || echo 0)" "status shows chief_approved ✅"
ok "$(echo "$S" | grep -q '✅ docket_gate_complete' && echo 1 || echo 0)" "status shows docket_gate_complete ✅"
ok "$(echo "$S" | grep -q '✅ docket_done' && echo 1 || echo 0)" "status shows docket_done ✅"
ok "$(echo "$S" | grep -q '✅ strategy_artifacts_verified' && echo 1 || echo 0)" "status shows strategy_artifacts_verified ✅"
ok "$(echo "$S" | grep -q '✅ docket_artifacts_verified' && echo 1 || echo 0)" "status shows docket_artifacts_verified ✅"

# the live glaw 'stage' command refuses to advance past an unmet gate (integration)
GLAW_BIN="$ROOT/bin/glaw"
N="$TMP/matters/n"; mkdir -p "$N"; : > "$N/timeline.jsonl"; echo intake > "$N/.stage"; echo n > "$TMP/.active"
"$GLAW_BIN" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$N/.stage")" = intake ] && echo 1 || echo 0)" "glaw stage refuses advance without intake/conflicts + leaves .stage unchanged"
"$GLAW_BIN" stage strategy --force >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$N/.stage")" = intake ] && echo 1 || echo 0)" "glaw stage strategy --force refuses guarded gate"

F="$TMP/matters/f"; mkdir -p "$F"; : > "$F/timeline.jsonl"; echo draft > "$F/.stage"; echo f > "$TMP/.active"
"$GLAW_BIN" stage file --force >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && [ "$(cat "$F/.stage")" = draft ] && echo 1 || echo 0)" "glaw stage file --force refuses final filing"

rm -rf "$TMP"
echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

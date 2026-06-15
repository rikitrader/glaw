#!/usr/bin/env bash
# gate_test.sh — regression test for bin/glaw-gate (the code-enforced hard gates).
# Zero spend. Isolates via a temp GLAW_HOME so it never touches real matters.
# Asserts: a guarded stage is BLOCKED (exit 1) until its prerequisite gate events are
# logged, then CLEAR (exit 0); unguarded stages are always clear.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
GATE="$HERE/../bin/glaw-gate"
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
M="$TMP/matters/m"; mkdir -p "$M"; : > "$M/timeline.jsonl"; echo m > "$TMP/.active"
log(){ printf '{"ts":"t","event":"%s"}\n' "$1" >> "$M/timeline.jsonl"; }
chk(){ "$GATE" check "$1" m >/dev/null 2>&1; echo $?; }   # echoes exit code
append_hashed_jsonl(){
  python3 - "$1" "$2" <<'PY'
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
  }
}
JSON
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
    "responsible_professional": "licensed reviewer",
    "source": "SRC-0001 authorized scope reviewed"
  },
  "upl_footer": "Attorney work-product - not legal advice."
}
JSON
ok "$([ "$(chk strategy)" = 0 ] && echo 1 || echo 0)" "strategy CLEAR after intake/ethics artifacts"

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
  "workflow_profile": "accounting",
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
    "external_deliverable_present": true,
    "source_evidence_manifest_clear": true,
    "senior_review_evidence_source_clear": true,
    "professional_report_manifest_clear": true,
    "upl_footer_clear": true
  }
}
JSON
python3 - "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
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
python3 - "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
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
python3 - "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
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
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before current council ledger artifact"
for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  append_hashed_jsonl "$M/council.jsonl" "{\"profile\":\"accounting\",\"role\":\"$role\",\"decision\":\"approve\",\"evidence\":\"SRC-0001 fixture\",\"notes\":\"$role source-backed approval conclusion\"}"
done
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before current adversarial ledger artifact"
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  append_hashed_jsonl "$M/adversarial.jsonl" "{\"profile\":\"accounting\",\"lens\":\"$lens\",\"decision\":\"survive\",\"attack\":\"$lens no fatal challenge after source review\",\"evidence\":\"SRC-0001 fixture\"}"
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
python3 - "$M" <<'PY'
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
mkdir -p "$M/evidence"
printf 'date,description,amount\n2026-01-01,capital deposit,100.00\n' > "$M/evidence/bank.csv"
python3 - "$M" <<'PY'
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
    for name in ["cfo", "irs-audit-agent", "legal-counsel", "forensic-audit", "outside-critic", "external-reviewer"]
] + [
    {
        "kind": "adversarial",
        "name": name,
        "status": "pass",
        "missing": [],
        "cited_source_ids": ["SRC-0001"],
    }
    for name in ["irs-examiner", "state-tax-auditor", "forensic-accountant", "cfo-controller", "outside-critic"]
]
packet["red_flag_resolution_evidence_manifest"] = []
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
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before reviewer identity manifest"
python3 - "$M" "$HERE/.." <<'PY'
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
    [row("council", name) for name in COUNCIL_PROFILES[profile]]
    + [row("adversarial", name) for name in ADVERSARIAL_PROFILES[profile]]
)
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED before deliverable hash manifest"
python3 - "$M" <<'PY'
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
python3 - "$M" <<'PY'
import hashlib, json, pathlib, sys
d = pathlib.Path(sys.argv[1])
packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
names = ["intake.json", "ethics.json", "citations.jsonl", "council.jsonl", "adversarial.jsonl"]
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
python3 - "$M/decisions.jsonl" "$M/final_packet.json" <<'PY'
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
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after all file gates"
cp "$M/decisions.jsonl" "$M/decisions.baseline.jsonl"
python3 - "$M/decisions.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
row = json.loads(open(p, encoding="utf-8").read())
row["decision"] = "tampered after approval"
open(p, "w", encoding="utf-8").write(json.dumps(row) + "\n")
PY
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by post-approval Chief decision tamper"
cp "$M/decisions.baseline.jsonl" "$M/decisions.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after exact Chief decision restored"
python3 - "$M/decisions.jsonl" <<'PY'
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
python3 - "$M/decisions.jsonl" <<'PY'
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
printf '{"id":"RF-STALE","severity":"high","status":"open","finding":"new post-packet issue"}\n' > "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet high red flag"
printf '{"id":"RF-STALE","severity":"high","status":"resolved","finding":"new post-packet issue","resolution_evidence":"fixed"}\n' > "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file STILL BLOCKED by new post-packet red flag ledger after resolution"
rm -f "$M/red_flags.jsonl"
ok "$([ "$(chk file)" = 0 ] && echo 1 || echo 0)" "file CLEAR after new post-packet red flag ledger removed"
cp "$M/citations.jsonl" "$M/citations.baseline.jsonl"
cp "$M/council.jsonl" "$M/council.baseline.jsonl"
cp "$M/adversarial.jsonl" "$M/adversarial.baseline.jsonl"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"weak","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/"}'
ok "$([ "$(chk file)" = 1 ] && echo 1 || echo 0)" "file BLOCKED by current post-packet weak citation"
append_hashed_jsonl "$M/citations.jsonl" '{"id":"C-1","status":"verified","proposition":"tax return must tie to books","authority":"26 U.S.C. 6001","source_url":"https://uscode.house.gov/","reviewer":"legal-research"}'
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
GLAW_BIN="$HERE/../bin/glaw"
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

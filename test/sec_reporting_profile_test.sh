#!/usr/bin/env bash
# sec_reporting_profile_test.sh — SEC reporting packets require books/reconciliation control.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
ETHICS="$ROOT/bin/glaw-ethics"
COUNCIL="$ROOT/bin/glaw-council"
ADVERSARIAL="$ROOT/bin/glaw-adversarial"
CITES="$ROOT/bin/glaw-citation-gate"
CORPUS="$ROOT/bin/glaw-citation-corpus"
FLAGS="$ROOT/bin/glaw-red-flags"
PACKET="$ROOT/bin/glaw-final-packet"
CONTROL="$ROOT/bin/glaw-accounting-control"
CHIEF="$ROOT/bin/glaw-chief-decision"

"$GLAW" matter new "SEC Reporting Profile" >/dev/null
SLUG="sec-reporting-profile"
M="$TMP/matters/$SLUG"
mkdir -p "$M/evidence" "$M/workpapers"
printf 'audited financial statement source package\n' > "$M/evidence/sec-source.txt"

"$INTAKE" set workflow_track sec-reporting >/dev/null
"$INTAKE" set client_names 'Acme PublicCo' >/dev/null
"$INTAKE" set parties 'Acme PublicCo; SEC; auditor' >/dev/null
"$INTAKE" set jurisdiction 'Federal securities' >/dev/null
"$INTAKE" set goal 'prepare SEC reporting package with audited financial statement tie-out' >/dev/null
"$INTAKE" set source_documents 'audited financials; trial balance; bank reconciliation' >/dev/null
"$INTAKE" set deadlines '2026-08-10 Form 10-Q target' >/dev/null
"$INTAKE" set facts_timeline '2026-06-30 quarter end' >/dev/null
"$INTAKE" set open_questions 'confirm filer status and auditor consent' >/dev/null
"$INTAKE" set conflicts_parties 'Acme PublicCo; SEC; auditor' >/dev/null
"$INTAKE" set authorized_scope 'review and draft only; no filing without human approval' >/dev/null
"$INTAKE" set track_specific.filer_status 'accelerated filer' >/dev/null
"$INTAKE" set track_specific.period_end '2026-06-30' >/dev/null
"$INTAKE" set track_specific.forms_needed '10-Q; 8-K if triggered' >/dev/null
"$INTAKE" set track_specific.audited_financial_sources 'trial balance; audited financials; bank reconciliation' >/dev/null
"$INTAKE" set track_specific.xbrl_scope 'cover financial statements and notes' >/dev/null
"$INTAKE" complete --by 'Morgan Hale, SEC reporting reviewer' >/dev/null

"$ETHICS" record-conflicts --status cleared --notes 'no conflict in SEC reporting fixture' --source 'SRC-0001 party list reviewed' >/dev/null
"$ETHICS" draft-engagement --scope 'review and draft SEC reporting work-product only' --responsible-professional 'Alex Rivera, licensed attorney' --source 'SRC-0001 authorized scope reviewed' >/dev/null
"$ETHICS" complete >/dev/null
"$FLAGS" complete >/dev/null

"$COUNCIL" status --profile auto >"$TMP/council.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'COUNCIL sec-reporting' "$TMP/council.out" && grep -q 'sec-counsel' "$TMP/council.out" && grep -q 'audit-reviewer' "$TMP/council.out" && echo 1 || echo 0)" "council auto-selects SEC reporting profile"
for role in sec-counsel accounting-reviewer disclosure-reviewer audit-reviewer outside-critic; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-0001 $role SEC reporting support reviewed" --notes "$role source-backed SEC reporting conclusion" >/dev/null
done
"$COUNCIL" complete --profile auto >/dev/null

"$ADVERSARIAL" status --profile auto >"$TMP/adversarial.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'ADVERSARIAL sec-reporting' "$TMP/adversarial.out" && grep -q 'sec-staff-reviewer' "$TMP/adversarial.out" && grep -q 'pcaob-audit-reviewer' "$TMP/adversarial.out" && echo 1 || echo 0)" "adversarial auto-selects SEC/PCAOB profile"
for lens in sec-staff-reviewer pcaob-audit-reviewer disclosure-counsel irs-examiner outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "SRC-0001 $lens challenged SEC reporting tie-out and found no fatal defect" --evidence "SRC-0001 SEC reporting support reviewed" >/dev/null
done
"$ADVERSARIAL" complete --profile auto >/dev/null

printf '%s\n' 'Regulation S-X is the cited financial statement reporting authority requiring SEC reporting financial statements to tie to source books and controls.' > "$TMP/ecfr-regsx.txt"
"$CORPUS" capture --id CORP-SEC-0001 --source-url 'https://www.ecfr.gov/' --file "$TMP/ecfr-regsx.txt" --authenticated-copy --segment 'SEC reporting financial statements to tie to source books and controls' >/dev/null
"$CITES" record --id C-SEC-0001 --proposition 'SEC reporting financial statements must tie to source books and controls' --authority 'Regulation S-X' --status verified --source-url 'https://www.ecfr.gov/' --reviewer legal-research --support-summary 'Regulation S-X is the cited financial statement reporting authority; source books and controls remain required support for the package.' --corpus-id CORP-SEC-0001 >/dev/null
"$CITES" complete >/dev/null

cat > "$M/sec-report.md" <<'MD'
# SEC Reporting Review

Owner: GLAW SEC Reporting
Report voice: SEC disclosure and audit-control report.
Findings: Financial reporting package ties to source support.
Evidence: SRC-0001 audited financial statement source package.
Red flags: none.
Sign-off conditions: licensed securities counsel and auditor review before filing.

Attorney work-product - not legal advice. Prepared for licensed review.
MD

"$PACKET" build >/dev/null 2>"$TMP/packet-missing-control.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'accounting_control.json' "$TMP/packet-missing-control.out" && echo 1 || echo 0)" "SEC final packet blocked before accounting control"

cat > "$M/workpapers/ledger.json" <<'JSON'
{
  "rows": [
    {
      "booking_date": "2026-06-30",
      "description": "SEC reporting cash balance",
      "normalized_description": "SEC REPORTING CASH BALANCE",
      "amount": "100.00",
      "currency": "USD",
      "category": "Equity:Owner:Contributions",
      "transaction_hash": "sec-fixture-001",
      "source_method": "deterministic"
    }
  ],
  "audit": [
    {
      "source": "evidence/sec-source.txt",
      "balance_status": "verified"
    }
  ]
}
JSON
cat > "$M/workpapers/bank-rec-input.json" <<'JSON'
{
  "matched": 1,
  "book_only": [],
  "bank_only": [],
  "sum_book": "100.00",
  "sum_bank": "100.00",
  "unreconciled_difference": "0.00",
  "reconciled": true
}
JSON
cat > "$M/workpapers/audit-tieout-bad.json" <<'JSON'
{
  "financial_statements_tie": true,
  "icfr_reviewed": true,
  "pcaob_reviewed": true,
  "open_deficiencies": [
    {
      "id": "D-1",
      "severity": "material"
    }
  ],
  "material_weaknesses": [],
  "unresolved_audit_differences": []
}
JSON
cat > "$M/workpapers/audit-tieout-malformed.json" <<'JSON'
{
  "financial_statements_tie": true,
  "icfr_reviewed": true,
  "pcaob_reviewed": true,
  "open_deficiencies": {},
  "material_weaknesses": [],
  "unresolved_audit_differences": []
}
JSON
"$CONTROL" --matter "$SLUG" --profile sec-reporting --source "SRC-0001 SEC reporting ledger and bank reconciliation support reviewed" --ledger "$M/workpapers/ledger.json" --bank-rec "$M/workpapers/bank-rec-input.json" >/dev/null 2>"$TMP/control-missing-audit.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'audit-tieout' "$TMP/control-missing-audit.out" && echo 1 || echo 0)" "SEC accounting control blocked without audit tie-out"
"$CONTROL" --matter "$SLUG" --profile sec-reporting --source "SRC-0001 SEC reporting ledger and bank reconciliation support reviewed" --ledger "$M/workpapers/ledger.json" --bank-rec "$M/workpapers/bank-rec-input.json" --audit-tieout "$M/workpapers/audit-tieout-malformed.json" >/dev/null 2>"$TMP/control-malformed-audit.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'open_deficiencies must be a JSON array' "$TMP/control-malformed-audit.out" && echo 1 || echo 0)" "SEC accounting control blocked by malformed audit issue array"
"$CONTROL" --matter "$SLUG" --profile sec-reporting --source "SRC-0001 SEC reporting ledger and bank reconciliation support reviewed" --ledger "$M/workpapers/ledger.json" --bank-rec "$M/workpapers/bank-rec-input.json" --audit-tieout "$M/workpapers/audit-tieout-bad.json" >/dev/null 2>"$TMP/control-bad-audit.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'SEC audit tie-out' "$TMP/control-bad-audit.out" && echo 1 || echo 0)" "SEC accounting control blocked by open audit deficiency"
cat > "$M/workpapers/audit-tieout-good.json" <<'JSON'
{
  "financial_statements_tie": true,
  "icfr_reviewed": true,
  "pcaob_reviewed": true,
  "open_deficiencies": [],
  "material_weaknesses": [],
  "unresolved_audit_differences": []
}
JSON
"$CONTROL" --matter "$SLUG" --profile sec-reporting --source "SRC-0001 SEC reporting ledger bank reconciliation audit and ICFR support reviewed" --ledger "$M/workpapers/ledger.json" --bank-rec "$M/workpapers/bank-rec-input.json" --audit-tieout "$M/workpapers/audit-tieout-good.json" >/dev/null
"$PACKET" build >/dev/null 2>"$TMP/packet-ready.out"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q '"workflow_profile": "sec-reporting"' "$M/final_packet.json" && grep -q '"required": true' "$M/final_packet.json" && grep -q '"label": "audit_tieout"' "$M/final_packet.json" && echo 1 || echo 0)" "SEC final packet ready after audit-backed accounting control"
"$CHIEF" --matter "$SLUG" --chief "GLAW Chief Counsel" --score 95 --grade A --decision PROCEED --risks none --conditions "licensed SEC counsel and auditor review before filing" --rationale "SRC-0001 SEC reporting packet, audit tie-out, ICFR, and PCAOB control evidence reviewed" --approve-final >/dev/null
"$GLAW" stage file >/dev/null 2>"$TMP/stage-file-clear.out"; rc=$?
ok "$([ "$rc" = 0 ] && [ "$(cat "$M/.stage")" = file ] && echo 1 || echo 0)" "SEC file gate clears after Chief approval"
cp "$M/final_packet.json" "$M/final_packet.audit-baseline.json"
cp "$M/decisions.jsonl" "$M/decisions.audit-baseline.jsonl"
cp "$M/workpapers/audit-tieout.json" "$M/workpapers/audit-tieout.baseline.json"
python3 - "$M" <<'PY'
import hashlib
import json
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
audit_path = d / "workpapers" / "audit-tieout.json"
audit_path.write_text(json.dumps({
    "financial_statements_tie": True,
    "icfr_reviewed": True,
    "pcaob_reviewed": True,
    "open_deficiencies": [{"id": "D-2", "severity": "material"}],
    "material_weaknesses": [],
    "unresolved_audit_differences": [],
}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
for item in manifest["artifact_hashes"]:
    if item["label"] == "audit_tieout":
        item["sha256"] = hashlib.sha256(audit_path.read_bytes()).hexdigest()
        item["size_bytes"] = audit_path.stat().st_size
manifest["status"] = "fail"
manifest["missing"] = ["audit_tieout.artifact.open_deficiencies empty"]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
lines = [line for line in decision_path.read_text(encoding="utf-8").splitlines() if line.strip()]
row = json.loads(lines[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
lines[-1] = json.dumps(row)
decision_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
"$GLAW" stage file >/dev/null 2>"$TMP/stage-file-audit-tamper.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'current accounting control is incomplete' "$TMP/stage-file-audit-tamper.out" && echo 1 || echo 0)" "SEC file gate blocks audit tie-out workpaper content even with matching packet hashes"
python3 - "$M" <<'PY'
import hashlib
import json
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
audit_path = d / "workpapers" / "audit-tieout.json"
audit_path.write_text(json.dumps({
    "financial_statements_tie": True,
    "icfr_reviewed": True,
    "pcaob_reviewed": True,
    "open_deficiencies": {},
    "material_weaknesses": [],
    "unresolved_audit_differences": [],
}) + "\n", encoding="utf-8")

packet_path = d / "final_packet.json"
packet = json.loads(packet_path.read_text(encoding="utf-8"))
manifest = packet["accounting_control_manifest"]
for item in manifest["artifact_hashes"]:
    if item["label"] == "audit_tieout":
        item["sha256"] = hashlib.sha256(audit_path.read_bytes()).hexdigest()
        item["size_bytes"] = audit_path.stat().st_size
manifest["status"] = "fail"
manifest["missing"] = ["audit_tieout.artifact.open_deficiencies array"]
packet_path.write_text(json.dumps(packet) + "\n", encoding="utf-8")

decision_path = d / "decisions.jsonl"
lines = [line for line in decision_path.read_text(encoding="utf-8").splitlines() if line.strip()]
row = json.loads(lines[-1])
row["approved_packet_sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
row.pop("decision_hash", None)
row["decision_hash"] = hashlib.sha256(
    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
lines[-1] = json.dumps(row)
decision_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
"$GLAW" stage file >/dev/null 2>"$TMP/stage-file-audit-malformed.out"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'current accounting control is incomplete' "$TMP/stage-file-audit-malformed.out" && echo 1 || echo 0)" "SEC file gate blocks malformed audit tie-out arrays even with matching packet hashes"
cp "$M/final_packet.audit-baseline.json" "$M/final_packet.json"
cp "$M/decisions.audit-baseline.jsonl" "$M/decisions.jsonl"
cp "$M/workpapers/audit-tieout.baseline.json" "$M/workpapers/audit-tieout.json"
"$GLAW" stage file >/dev/null 2>"$TMP/stage-file-restored.out"; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "SEC file gate clears after exact audit tie-out workpaper restored"

echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ]

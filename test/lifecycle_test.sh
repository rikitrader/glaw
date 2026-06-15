#!/usr/bin/env bash
# lifecycle_test.sh — full source-only matter lifecycle gate test.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
COUNCIL="$ROOT/bin/glaw-council"
FLAGS="$ROOT/bin/glaw-red-flags"
PACKET="$ROOT/bin/glaw-final-packet"
CHIEF="$ROOT/bin/glaw-chief-decision"
ADVERSARIAL="$ROOT/bin/glaw-adversarial"
ETHICS="$ROOT/bin/glaw-ethics"
CITES="$ROOT/bin/glaw-citation-gate"
DOCKET="$ROOT/bin/glaw-docket-gate"

"$GLAW" matter new "Lifecycle Accounting" >/dev/null
SLUG="lifecycle-accounting"
ok "$([ -f "$TMP/matters/$SLUG/intake.json" ] && echo 1 || echo 0)" "matter new creates intake.json"
"$GLAW" timeline-log chief_approved >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && ! grep -q 'chief_approved' "$TMP/matters/$SLUG/timeline.jsonl" && echo 1 || echo 0)" "manual timeline-log refuses reserved chief_approved gate event"
"$GLAW" timeline-log operator_note >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'operator_note' "$TMP/matters/$SLUG/timeline.jsonl" && echo 1 || echo 0)" "manual timeline-log still allows non-gate operator notes"

"$GLAW" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "strategy blocked before intake/conflicts"

"$INTAKE" set workflow_track accounting-tax >/dev/null
"$INTAKE" set client_names 'Acme Inc.' >/dev/null
"$INTAKE" set parties 'Acme Inc.; Bank' >/dev/null
"$INTAKE" set jurisdiction 'Florida' >/dev/null
"$INTAKE" set goal 'reconstruct books and tax package' >/dev/null
"$INTAKE" set source_documents 'bank.csv' >/dev/null
"$INTAKE" set deadlines '2026-09-15 tax filing' >/dev/null
"$INTAKE" set facts_timeline '2026-01-01 opening balance' >/dev/null
"$INTAKE" set open_questions 'none' >/dev/null
"$INTAKE" set conflicts_parties 'Acme Inc.; Bank' >/dev/null
"$INTAKE" set authorized_scope 'review and draft only' >/dev/null
"$INTAKE" set track_specific.bank_statement_sources 'bank.csv' >/dev/null
"$INTAKE" set track_specific.tax_years '2026' >/dev/null
"$INTAKE" set track_specific.entity_tax_type 'C-corp' >/dev/null
"$INTAKE" set track_specific.books_status 'raw statements' >/dev/null
"$INTAKE" set track_specific.irs_forms_needed '1120' >/dev/null
"$INTAKE" complete >/dev/null
"$ETHICS" record-conflicts --status cleared --notes 'no conflict in test fixture' >/dev/null
"$ETHICS" draft-engagement --scope 'review and draft only' --responsible-professional 'licensed reviewer' >/dev/null
"$ETHICS" complete >/dev/null
"$GLAW" stage strategy >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "strategy clears after intake/conflicts"

"$FLAGS" add --severity high --owner cfo --source test --finding 'cash tie-out missing' --required-fix 'attach bank reconciliation' >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by open high red flag"
"$FLAGS" resolve RF-0001 --evidence 'bank reconciliation attached' >/dev/null
"$FLAGS" complete >/dev/null

"$COUNCIL" record --profile auto --role cfo --decision approve >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked without evidence"
"$COUNCIL" record --profile auto --role cfo --decision approve --evidence "test fixture review basis" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council approve blocked without source evidence id"
for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-9999 test fixture review basis" >/dev/null
done
cp "$TMP/matters/$SLUG/council.jsonl" "$TMP/matters/$SLUG/council.clean.jsonl"
python3 - "$TMP/matters/$SLUG/council.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["evidence"] = "tampered after review"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$COUNCIL" status --profile auto >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "council status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/council.clean.jsonl" "$TMP/matters/$SLUG/council.jsonl"
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked before final packet ready"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before adversarial government lenses survive"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "no fatal finding" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked without evidence"
"$ADVERSARIAL" record --profile auto --lens irs-examiner --decision survive --attack "no fatal finding" --evidence "test fixture" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial survive blocked without source evidence id"
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "no fatal finding" --evidence "SRC-9999 test fixture" >/dev/null
done
cp "$TMP/matters/$SLUG/adversarial.jsonl" "$TMP/matters/$SLUG/adversarial.clean.jsonl"
python3 - "$TMP/matters/$SLUG/adversarial.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["decision"] = "fix"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$ADVERSARIAL" status --profile auto >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "adversarial status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/adversarial.clean.jsonl" "$TMP/matters/$SLUG/adversarial.jsonl"
"$ADVERSARIAL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before citation gate completes"
"$CITES" record --id C-0001 --proposition 'tax return must tie to books' --authority '26 U.S.C. § 6001' --status verified --source-url 'https://uscode.house.gov/' >/dev/null
cp "$TMP/matters/$SLUG/citations.jsonl" "$TMP/matters/$SLUG/citations.clean.jsonl"
python3 - "$TMP/matters/$SLUG/citations.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
rows = [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
rows[0]["authority"] = "tampered authority"
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
"$CITES" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation status blocks tampered review ledger row"
cp "$TMP/matters/$SLUG/citations.clean.jsonl" "$TMP/matters/$SLUG/citations.jsonl"
"$CITES" complete >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before council completion is logged"
"$COUNCIL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before external deliverable exists"
printf '# Draft Report\n\nNumbers tie to source.\n' > "$TMP/matters/$SLUG/draft-report.md"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by deliverable missing UPL footer"
printf '\nAttorney work-product - not legal advice. Prepared for licensed review.\n' >> "$TMP/matters/$SLUG/draft-report.md"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by deliverable missing professional report markers"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: Test fixture ledger and bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by report without source evidence id"
mkdir -p "$TMP/matters/$SLUG/evidence"
printf 'date,description,amount\n2026-01-01,capital deposit,100.00\n' > "$TMP/matters/$SLUG/evidence/bank.csv"
cat > "$TMP/matters/$SLUG/draft-report.md" <<'MD'
# Draft Report

Owner: GLAW Controller
Report voice: controller/CFO report.
Findings: Numbers tie to source.
Evidence: SRC-0001 bank statement.
Red flags: none.
Sign-off conditions: licensed review.

Attorney work-product - not legal advice. Prepared for licensed review.
MD
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by senior reviews without source evidence ids"
for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-0001 test fixture review basis" >/dev/null
done
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "no fatal finding" --evidence "SRC-0001 test fixture" >/dev/null
done
"$COUNCIL" complete --profile auto >/dev/null
"$ADVERSARIAL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ -f "$TMP/matters/$SLUG/final_packet.json" ] && echo 1 || echo 0)" "final packet ready after council and red flags clear"

"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --approve-final --matter "$SLUG" >/dev/null
"$GLAW" stage file >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ "$(cat "$TMP/matters/$SLUG/.stage")" = file ] && echo 1 || echo 0)" "file stage clears after final packet and chief approval"

"$GLAW" stage matter-retro >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "matter-retro blocked before docket gate"
"$GLAW" docket add 2026-09-15 "tax filing due - verify extension" >/dev/null
"$DOCKET" complete >/dev/null
"$GLAW" stage matter-retro >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ "$(cat "$TMP/matters/$SLUG/.stage")" = matter-retro ] && echo 1 || echo 0)" "matter-retro clears after docket gate"

rm -rf "$TMP"
echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

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

for role in cfo irs-audit-agent legal-counsel forensic-audit outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve >/dev/null
done
"$CHIEF" --chief "GLAW Chief Counsel" --decision "PROCEED" --approve-final --matter "$SLUG" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "chief final approval blocked before final packet ready"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before adversarial government lenses survive"
for lens in irs-examiner state-tax-auditor forensic-accountant cfo-controller outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "no fatal finding" --evidence "test fixture" >/dev/null
done
"$ADVERSARIAL" complete --profile auto >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before citation gate completes"
"$CITES" record --id C-0001 --proposition 'tax return must tie to books' --authority '26 U.S.C. § 6001' --status verified --source-url 'https://uscode.house.gov/' >/dev/null
"$CITES" complete >/dev/null
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked before council completion is logged"
"$COUNCIL" complete --profile auto >/dev/null
printf '# Draft Report\n\nNumbers tie to source.\n' > "$TMP/matters/$SLUG/draft-report.md"
"$PACKET" build >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "final packet blocked by deliverable missing UPL footer"
printf '\nAttorney work-product - not legal advice. Prepared for licensed review.\n' >> "$TMP/matters/$SLUG/draft-report.md"
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

#!/usr/bin/env bash
# tax_profile_test.sh — dedicated tax intake auto-routes to tax Council/adversarial profiles.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
COUNCIL="$ROOT/bin/glaw-council"
ADVERSARIAL="$ROOT/bin/glaw-adversarial"

"$GLAW" matter new "Tax Profile" >/dev/null
SLUG="tax-profile"
mkdir -p "$TMP/matters/$SLUG/evidence"
printf 'tax source package\n' > "$TMP/matters/$SLUG/evidence/tax-source.txt"
"$INTAKE" set workflow_track tax >/dev/null
"$INTAKE" set client_names 'Acme Inc.' >/dev/null
"$INTAKE" set parties 'Acme Inc.; IRS; Florida DOR' >/dev/null
"$INTAKE" set jurisdiction 'Federal; Florida' >/dev/null
"$INTAKE" set goal 'prepare tax compliance and audit-ready response package' >/dev/null
"$INTAKE" set source_documents 'returns; IRS notice; GL export' >/dev/null
"$INTAKE" set deadlines '2026-09-15 extended return due' >/dev/null
"$INTAKE" set facts_timeline '2026-06-15 notice received' >/dev/null
"$INTAKE" set open_questions 'confirm extension; confirm notice deadline' >/dev/null
"$INTAKE" set conflicts_parties 'Acme Inc.; IRS; Florida DOR' >/dev/null
"$INTAKE" set authorized_scope 'review and draft only; no filing without human approval' >/dev/null

"$INTAKE" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "tax intake blocked before tax-specific fields"
"$INTAKE" set track_specific.tax_years '2024; 2025' >/dev/null
"$INTAKE" set track_specific.taxpayer_type 'C-corp' >/dev/null
"$INTAKE" set track_specific.tax_forms_needed '1120; 941; 1099' >/dev/null
"$INTAKE" set track_specific.source_records 'returns; IRS notice; GL export; bank records' >/dev/null
"$INTAKE" set track_specific.positions_or_issues 'credits; deductions; penalties; audit adjustments' >/dev/null
"$INTAKE" set track_specific.filing_or_exam_deadlines '2026-09-15 extended return due; verify notice response date' >/dev/null
"$INTAKE" complete >/dev/null
ok "$([ -f "$TMP/matters/$SLUG/intake.json" ] && grep -q '"workflow_track": "tax"' "$TMP/matters/$SLUG/intake.json" && echo 1 || echo 0)" "tax intake completes with tax track"

"$COUNCIL" status --profile auto >"$TMP/council.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'COUNCIL tax' "$TMP/council.out" && grep -q 'tax-strategist' "$TMP/council.out" && grep -q 'irs-audit-agent' "$TMP/council.out" && echo 1 || echo 0)" "council auto-selects tax profile"
for role in tax-strategist irs-audit-agent legal-counsel accounting-reviewer outside-critic external-reviewer; do
  "$COUNCIL" record --profile auto --role "$role" --decision approve --evidence "SRC-0001 tax source package reviewed" --notes "$role source-backed tax conclusion" >/dev/null
done
"$COUNCIL" complete --profile auto >"$TMP/council-complete.out" 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'TAX COUNCIL COMPLETE' "$TMP/council-complete.out" && echo 1 || echo 0)" "tax council completes through auto profile"

"$ADVERSARIAL" status --profile auto >"$TMP/adversarial.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'ADVERSARIAL tax' "$TMP/adversarial.out" && grep -q 'tax-court-counsel' "$TMP/adversarial.out" && grep -q 'penalty-reviewer' "$TMP/adversarial.out" && echo 1 || echo 0)" "adversarial auto-selects tax profile"
for lens in irs-examiner state-tax-auditor tax-court-counsel penalty-reviewer outside-critic; do
  "$ADVERSARIAL" record --profile auto --lens "$lens" --decision survive --attack "$lens challenged tax position against SRC-0001 and found no fatal defect" --evidence "SRC-0001 tax source package reviewed" >/dev/null
done
"$ADVERSARIAL" complete --profile auto >"$TMP/adversarial-complete.out" 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'TAX ADVERSARIAL COMPLETE' "$TMP/adversarial-complete.out" && echo 1 || echo 0)" "tax adversarial completes through auto profile"

echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ]

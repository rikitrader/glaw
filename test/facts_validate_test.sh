#!/usr/bin/env bash
# facts_validate_test.sh — regression test for the launch-guard engine facts_validate.py
# (the single most safety-critical script in GLAW: it decides RUN vs WAIT for the Chief loop).
# Zero spend. Isolates state via a temp HOME so it never touches real matters.
# Asserts the fail-closed contract: ONLY a complete + verified + conflict-free matter
# yields LAUNCH_AUTHORIZED (exit 0); every other condition DENIES (exit 1).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
GUARD="$HERE/../bin/matter-ops/facts_validate.py"
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

# run <slug-fixture-json> -> sets $OUT (text) and $RC (exit code), isolated in a temp HOME
run(){
  local TMP; TMP="$(mktemp -d)"
  mkdir -p "$TMP/.glaw/matters/t"
  printf '%s' "$1" > "$TMP/.glaw/matters/t/facts.json"
  OUT="$(HOME="$TMP" python3 "$GUARD" t 2>&1)"; RC=$?
  rm -rf "$TMP"
}

VALID='{"issuance_date":"2025-08-15","cap_table":"Founders 8,000,000; pool 2,000,000","gross_assets":"$1,200,000","ip_valuation":"$300,000","ein_hq":"88-1234567, 123 Main St, Austin TX","controlled_group":"none","residence_state":"Texas, single","valuation_409a":"$0.10/share"}'

# 1. empty matter -> FACT_INCOMPLETE, DENY
run '{}'
ok "$([ "$RC" = 1 ] && echo 1 || echo 0)" "empty matter exits 1 (DENY)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: FACT_INCOMPLETE' && echo 1 || echo 0)" "empty matter = FACT_INCOMPLETE"

# 2. fully valid -> LAUNCH_AUTHORIZED, exit 0
run "$VALID"
ok "$([ "$RC" = 0 ] && echo 1 || echo 0)" "complete+verified matter exits 0 (AUTHORIZE)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: LAUNCH_AUTHORIZED' && echo 1 || echo 0)" "complete matter = LAUNCH_AUTHORIZED"

# 3. issuance_date on/before 2025-07-04 -> CONTRADICTION -> FACT_CONFLICT, DENY
run "$(echo "$VALID" | sed 's/2025-08-15/2025-06-01/')"
ok "$([ "$RC" = 1 ] && echo 1 || echo 0)" "pre-OBBBA date exits 1 (DENY)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: FACT_CONFLICT' && echo 1 || echo 0)" "pre-OBBBA date = FACT_CONFLICT"

# 4. cross-check: ip_valuation > gross_assets -> FACT_CONFLICT, DENY
run "$(echo "$VALID" | sed 's/\$300,000/$5,000,000/')"
ok "$([ "$RC" = 1 ] && echo 1 || echo 0)" "ip>gross exits 1 (DENY)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: FACT_CONFLICT' && echo 1 || echo 0)" "ip>gross = FACT_CONFLICT (cross-check)"

# 5. weak value (no dollar figure) -> FACT_VALIDATION_PENDING, DENY
run "$(echo "$VALID" | sed 's/\$1,200,000/about a lot/')"
ok "$([ "$RC" = 1 ] && echo 1 || echo 0)" "weak gross_assets exits 1 (DENY)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: FACT_VALIDATION_PENDING' && echo 1 || echo 0)" "weak value = FACT_VALIDATION_PENDING"

# 6. [VERIFY placeholder counts as MISSING (the 358-agent root cause) -> DENY
run "$(echo "$VALID" | sed 's/Texas, single/[VERIFY: ask founder]/')"
ok "$([ "$RC" = 1 ] && echo 1 || echo 0)" "[VERIFY] placeholder exits 1 (DENY)"
ok "$(echo "$OUT" | grep -q 'LAUNCH_STATUS: FACT_INCOMPLETE' && echo 1 || echo 0)" "[VERIFY] placeholder = FACT_INCOMPLETE"

echo
echo "${fail:-0} failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

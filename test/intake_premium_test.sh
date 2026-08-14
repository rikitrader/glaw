#!/usr/bin/env bash
# intake_premium_test.sh - premium lane tags are first-class intake metadata.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
export GLAW_HOME="$TMP"
pass=0
fail=0
ok() {
  if [ "$1" = 1 ]; then
    pass=$((pass + 1))
    echo "  ✓ $2"
  else
    fail=$((fail + 1))
    echo "  ✗ FAIL: $2"
  fi
}

GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
HEAD="$ROOT/bin/glaw-headless"

"$GLAW" matter new "Intake Premium Fixture" >/dev/null
"$INTAKE" premium founder tax uhnw >/"$TMP/premium.out" 2>"$TMP/premium.err"; rc=$?
python3 - "$TMP/matters/intake-premium-fixture/intake.json" "$TMP/premium.out" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
out = open(sys.argv[2], encoding="utf-8").read()
lanes = data.get("universal", {}).get("premium_lanes")
ok = lanes == ["founder-unicorn", "tax-system", "uhnw-family-office"] and "founder-unicorn" in out
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "glaw-intake premium normalizes aliases to canonical lane ids"

"$HEAD" --goal "premium intake fixture" --matter intake-premium-fixture --json > "$TMP/headless.json"; rc=$?
python3 - "$TMP/headless.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
lanes = data.get("premium_lane_requirement", {}).get("required_lanes")
ok = (
    data.get("premium_lane_requirement", {}).get("required") is True
    and lanes == ["founder-unicorn", "tax-system", "uhnw-family-office"]
    and len(data.get("premium_lane_action_plan") or []) == 3
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless reads intake premium tags and routes missing lane packets"

"$INTAKE" premium --clear >/"$TMP/clear.out" 2>"$TMP/clear.err"; rc=$?
"$HEAD" --goal "premium intake fixture cleared" --matter intake-premium-fixture --json > "$TMP/headless-clear.json"; rc2=$?
python3 - "$TMP/headless-clear.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = (
    data.get("premium_lane_requirement", {}).get("required") is False
    and data.get("premium_lane_requirement", {}).get("basis") == "explicit_no_premium_lanes"
    and data.get("premium_lanes", {}).get("status") == "not_required"
    and not data.get("premium_lane_action_plan")
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "glaw-intake premium --clear records explicit no-premium scope"

"$INTAKE" premium mystery-lane >"$TMP/bad.out" 2>"$TMP/bad.err"; rc=$?
ok "$([ "$rc" = 2 ] && grep -q "unknown premium lane" "$TMP/bad.err" && echo 1 || echo 0)" "glaw-intake premium fails closed on unknown lane"

rm -rf "$TMP"
echo
echo "0 failures - $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit 1; }

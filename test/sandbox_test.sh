#!/usr/bin/env bash
# sandbox_test.sh - isolated fail-closed simulation runner.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

SANDBOX="$ROOT/bin/glaw-sandbox"
TMP="$(mktemp -d)"

"$SANDBOX" list --json > "$TMP/list.json"; rc=$?
python3 - "$TMP/list.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
names={item.get("name") for item in data.get("scenarios", [])}
required={
    "conscience-human-act",
    "oversight-kill-switch",
    "deadline-daemon",
    "jurisdiction-pack-fail",
    "profile-map",
    "government-adversary-routing",
    "fortune500-accounting-priority",
    "sec-pcaob-tabletop",
}
sys.exit(0 if data.get("status") == "pass" and required <= names else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "sandbox lists required scenarios"

"$SANDBOX" run --scenario all --json > "$TMP/run.json"; rc=$?
python3 - "$TMP/run.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
scenarios=data.get("scenarios", [])
ok=(
    data.get("status") == "pass"
    and len(scenarios) >= 5
    and all(item.get("status") == "pass" for item in scenarios)
    and "no filing" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "sandbox full run passes fail-closed fixtures"

"$SANDBOX" run --scenario fortune500-accounting-priority --json > "$TMP/accounting.json"; rc=$?
python3 - "$TMP/accounting.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
scenario=data.get("scenarios", [{}])[0]
checks={item.get("id"): item.get("status") for item in scenario.get("checks", [])}
ok=(
    data.get("status") == "pass"
    and scenario.get("name") == "fortune500-accounting-priority"
    and checks.get("accounting_controls_are_first_owner") == "pass"
    and checks.get("all_failed_rows_in_action_plan") == "pass"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "sandbox requires Fortune 500 accounting-control priority"

"$SANDBOX" run --scenario sec-pcaob-tabletop --json > "$TMP/sec.json"; rc=$?
python3 - "$TMP/sec.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
scenario=data.get("scenarios", [{}])[0]
checks={item.get("id"): item.get("status") for item in scenario.get("checks", [])}
ok=(
    data.get("status") == "pass"
    and scenario.get("name") == "sec-pcaob-tabletop"
    and checks.get("sec_and_pcaob_lenses_required") == "pass"
    and checks.get("routes_failed_lens_to_red_team") == "pass"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "sandbox requires SEC/PCAOB adversarial tabletop routing"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

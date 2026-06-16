#!/usr/bin/env bash
# loop_test.sh - glaw-loop routes by gate state and refuses autonomous authority acts.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
LOOP="$ROOT/bin/glaw-loop"

"$GLAW" matter new "Loop Routing" >/dev/null
"$INTAKE" set workflow_track accounting-tax >/dev/null

"$LOOP" status --json > "$TMP/loop-status.json"; rc=$?
python3 - "$TMP/loop-status.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = (
    data.get("matter") == "loop-routing"
    and data.get("next_gate") == "strategy"
    and data.get("owner") == "intake"
    and data.get("workflow_profile") == "accounting-tax"
    and "irs-examiner" in data.get("adversarial_required", [])
    and "quality routing only" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop status routes incomplete accounting-tax matter to intake and lists adversarial profile"

"$LOOP" once --request-action file > "$TMP/loop-file.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'HUMAN AUTHORITY BLOCKED' "$TMP/loop-file.out" && echo 1 || echo 0)" "loop refuses autonomous file request"

"$LOOP" once --json --request-action transmit > "$TMP/loop-transmit.json" 2>&1; rc=$?
python3 - "$TMP/loop-transmit.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data.get("quality_state") == "authority_blocked" and data.get("requested_action") == "transmit"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "loop JSON reports authority-blocked transmit"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

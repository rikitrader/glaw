#!/usr/bin/env bash
# oversight_test.sh - kill-switch and Oversight Board ledger behavior.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
OVERSIGHT="$ROOT/bin/glaw-oversight"

"$OVERSIGHT" status --json > "$TMP/status.json"; rc=$?
python3 - "$TMP/status.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "active" and data.get("state", {}).get("halted") is False else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "oversight starts active"

"$OVERSIGHT" halt --by "Board Chair" --reason "material control concern" --json > "$TMP/halt.json"; rc=$?
python3 - "$TMP/halt.json" "$TMP/oversight/oversight.jsonl" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
rows=[json.loads(line) for line in open(sys.argv[2]) if line.strip()]
ok=data.get("status") == "halted" and data.get("state", {}).get("halted") is True and rows[-1].get("event") == "kill_switch_halted"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "halt records kill-switch state and ledger row"

"$OVERSIGHT" resume --by "Board Chair" --role WRITER --reason "not enough authority" --json > "$TMP/resume-blocked.json" 2>&1; rc=$?
python3 - "$TMP/resume-blocked.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "blocked" else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "resume requires ADMIN authority"

"$OVERSIGHT" resume --by "Board Chair" --role ADMIN --reason "control issue resolved" --json > "$TMP/resume.json"; rc=$?
python3 - "$TMP/resume.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "active" and data.get("state", {}).get("halted") is False else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "ADMIN can resume with reason"

"$OVERSIGHT" escalate --matter matter-one --reason "loop did not converge" --source "SRC-0001 route evidence" --json > "$TMP/escalate.json"; rc=$?
python3 - "$TMP/escalate.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("event") == "oversight_escalation" and data.get("status") == "open" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "escalation records open oversight item"

"$OVERSIGHT" decision --matter matter-one --decision approve --by "Board Chair" --role ADMIN --reason "SRC-0001 controls clear" --source "SRC-0001 controls memo" --json > "$TMP/decision.json"; rc=$?
python3 - "$TMP/decision.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("event") == "oversight_decision" and data.get("decision") == "approve" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "ADMIN can record Board decision"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

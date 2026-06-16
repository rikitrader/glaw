#!/usr/bin/env bash
# daemon_test.sh - standing-goal docket watcher and oversight stop behavior.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
DAEMON="$ROOT/bin/glaw-daemon"
OVERSIGHT="$ROOT/bin/glaw-oversight"

"$DAEMON" status --json > "$TMP/status-empty.json"; rc=$?
python3 - "$TMP/status-empty.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
sys.exit(0 if data.get("status") == "active" and data.get("matter_count") == 0 else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "daemon status starts active with no matters"

"$DAEMON" goal add --name docket-watch --objective "watch every deadline" --horizon-days 45 >/dev/null; rc=$?
"$DAEMON" goal list --json > "$TMP/goals.json"; rc2=$?
python3 - "$TMP/goals.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
goals=data.get("goals", [])
sys.exit(0 if len(goals) == 1 and goals[0].get("name") == "docket-watch" else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "daemon records standing docket goal"

"$GLAW" matter new "Daemon Deadline" >/dev/null
mkdir -p "$TMP/matters/daemon-deadline/evidence"
printf 'deadline source\n' > "$TMP/matters/daemon-deadline/evidence/source.txt"
DUE="$(python3 - <<'PY'
from datetime import date, timedelta
print((date.today() + timedelta(days=5)).isoformat())
PY
)"
"$GLAW" docket add --owner "docket clerk" --source "SRC-0001 court order" "$DUE" "response deadline" >/dev/null
"$DAEMON" once --json > "$TMP/run.json"; rc=$?
python3 - "$TMP/run.json" "$TMP/daemon/runs.jsonl" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
rows=[json.loads(line) for line in open(sys.argv[2]) if line.strip()]
actions=data.get("actions", [])
ok=(
    data.get("status") == "attention_required"
    and actions
    and actions[0].get("matter") == "daemon-deadline"
    and actions[0].get("severity") == "high"
    and "glaw-loop once" in actions[0].get("next_command", "")
    and rows[-1].get("status") == "attention_required"
    and "no filing/signing" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "daemon scan surfaces upcoming sourced deadline and writes run ledger"

"$OVERSIGHT" halt --by "Board Chair" --reason "test halt" >/dev/null
"$DAEMON" once --json > "$TMP/halted.json"; rc=$?
python3 - "$TMP/halted.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=data.get("status") == "halted" and data.get("actions") == [] and "Oversight Board" in data.get("authority", "")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "daemon stops while oversight kill-switch is active"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

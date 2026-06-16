#!/usr/bin/env bash
# headless_test.sh - spawned/orchestrator headless report regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
HEAD="$ROOT/bin/glaw-headless"

"$HEAD" --goal "route matter" --json > "$TMP/no-matter.json"; rc=$?
python3 - "$TMP/no-matter.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data["status"] == "blocked" and data["reason"] == "no active matter" and data["next_owner"] == "orchestrator"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report blocks clearly when no active matter exists"

"$GLAW" matter new "Headless Routing" >/dev/null
"$INTAKE" set workflow_track accounting-tax >/dev/null
"$GLAW" --headless --goal "complete Fortune 500 accounting/tax gate report" --json > "$TMP/report.json"; rc=$?
python3 - "$TMP/report.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
loop = data.get("loop") or {}
open_gates = {row["stage"] for row in data.get("open_gates", [])}
ok = (
    data["status"] == "blocked"
    and data["matter"] == "headless-routing"
    and data["workflow_track"] == "accounting-tax"
    and data["next_owner"] == "intake"
    and data["next_gate"] == "strategy"
    and "strategy" in open_gates
    and "irs-examiner" in loop.get("adversarial_required", [])
    and "no filing/signing" in data["authority"]
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "glaw --headless emits blocked gate report with next owner and adversarial profile"

printf '{"ts":"t","event":"chief_decision","decision":"PROCEED"}\n' > "$TMP/matters/headless-routing/decisions.jsonl"
printf '{"status":"ready"}\n' > "$TMP/matters/headless-routing/final_packet.json"
"$HEAD" --goal "show decisions and artifacts" --matter headless-routing --json > "$TMP/report2.json"; rc=$?
python3 - "$TMP/report2.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
artifacts = {row["path"] for row in data["shipped_artifacts"]}
ok = data["decisions"] and "final_packet.json" in artifacts and data["timeline_events"] >= 1
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report includes decisions, artifacts, and timeline count"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

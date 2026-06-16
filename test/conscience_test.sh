#!/usr/bin/env bash
# conscience_test.sh - autonomous tool-call and response guardrail regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
LOOP="$ROOT/bin/glaw-loop"
CONSCIENCE="$ROOT/bin/glaw-conscience"

"$CONSCIENCE" check-call --command "bin/glaw-intake status" --json > "$TMP/call-pass.json"; rc=$?
python3 - "$TMP/call-pass.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if data.get("status") == "pass" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience allows benign status command"

"$CONSCIENCE" check-call --command "bin/glaw-irs-file submit payload.json --live" --json > "$TMP/live-block.json"; rc=$?
python3 - "$TMP/live-block.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {item.get("id") for item in data.get("failures", [])}
sys.exit(0 if data.get("status") == "fail" and "human_authority_live_filing" in ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience blocks live IRS filing without human authority"

"$CONSCIENCE" check-call --command "bin/glaw-chief-decision --signoff" --json > "$TMP/signoff-block.json"; rc=$?
python3 - "$TMP/signoff-block.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {item.get("id") for item in data.get("failures", [])}
sys.exit(0 if data.get("status") == "fail" and "human_authority_signoff" in ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience blocks signature signoff without human authority"

"$CONSCIENCE" check-call --command "bin/glaw timeline-log chief_approved" --json > "$TMP/event-block.json"; rc=$?
python3 - "$TMP/event-block.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {item.get("id") for item in data.get("failures", [])}
sys.exit(0 if data.get("status") == "fail" and "reserved_gate_events" in ids else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience blocks hand-logged reserved gate events"

"$CONSCIENCE" check-response --text "Final IRS audit packet is ready. [VERIFY bank tie-out]" --json > "$TMP/response-block.json"; rc=$?
python3 - "$TMP/response-block.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ids = {item.get("id") for item in data.get("failures", [])}
ok = data.get("status") == "fail" and "no_unresolved_placeholders" in ids and "source_ids_for_high_stakes_output" in ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience blocks unresolved high-stakes response"

"$CONSCIENCE" check-response --text "Attorney work-product draft. Tax position is supported by SRC-0001; no filing was performed." --json > "$TMP/response-pass.json"; rc=$?
python3 - "$TMP/response-pass.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if data.get("status") == "pass" else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "conscience allows source-backed work-product response"

"$GLAW" matter new "Conscience Loop" >/dev/null
"$INTAKE" set workflow_track accounting-tax >/dev/null
"$LOOP" once --json > "$TMP/loop.json"; rc=$?
python3 - "$TMP/loop.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
criteria = data.get("checker", {}).get("criteria", [])
guard = [item for item in criteria if item.get("id") == "conscience_call_guard"]
ok = guard and guard[0].get("status") == "pass" and data.get("checker", {}).get("conscience", {}).get("status") == "pass"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "glaw-loop records conscience_call_guard in checker"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

#!/usr/bin/env bash
# host_adapter_test.sh - autonomous host JSON adapter regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
HOST="$ROOT/bin/glaw-host"

"$HOST" manifest --json > "$TMP/manifest.json"; rc=$?
python3 - "$TMP/manifest.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
tools = {row["name"] for row in data["tools"]}
contract = data["safety_contract"]
ok = (
    data["name"] == "glaw-host-adapter"
    and {"glaw-loop", "glaw-conscience", "glaw-rbac"} <= tools
    and contract["argv_array_required"] is True
    and contract["human_seal_role"] == "ADMIN"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "manifest exposes tools and host safety contract"

"$HOST" execute --tool glaw --args '["version"]' --json > "$TMP/rbac-block.json"; rc=$?
python3 - "$TMP/rbac-block.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if data["status"] == "blocked" and data.get("phase") == "rbac" else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "execute blocks without host RBAC role"

"$HOST" execute --tool glaw --args '["version"]' --role READER --actor "Host Reader" --json > "$TMP/exec-ok.json"; rc=$?
python3 - "$TMP/exec-ok.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data["status"] == "pass" and data["rbac"]["status"] == "pass" and data["pre_guard"]["status"] == "pass" and data["post_guard"]["status"] == "pass" and data["stdout"].strip()
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "execute runs whitelisted read tool through RBAC and pre/post conscience guards"

"$HOST" execute --tool ../../bin/glaw-rbac --args '["roles"]' --json > "$TMP/path-block.json"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'not a whitelisted executable' "$TMP/path-block.json" && echo 1 || echo 0)" "execute blocks path traversal tool names"

"$HOST" execute --tool glaw --args '"stage file"' --json > "$TMP/args-block.json"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'args must be a JSON array' "$TMP/args-block.json" && echo 1 || echo 0)" "execute requires argv array, not shell string"

"$HOST" execute --tool glaw-irs-file --args '["submit","missing.json","--live"]' --matter host-test --role ADMIN --actor "Host Admin" --json > "$TMP/live-block.json"; rc=$?
python3 - "$TMP/live-block.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
failures = {f["id"] for f in data.get("pre_guard", {}).get("failures", [])}
sys.exit(0 if data["status"] == "blocked" and "human_authority_live_filing" in failures else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "execute blocks live filing before tool invocation"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

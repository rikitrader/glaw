#!/usr/bin/env bash
# extism_test.sh - zeroclaw/Extism contract shim regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
EXT="$ROOT/bin/glaw-extism"

"$EXT" tool_metadata --json > "$TMP/meta.json"; rc=$?
python3 - "$TMP/meta.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
names = {row["name"] for row in data["tools"]}
ok = (
    data["plugin"] == "glaw-extism"
    and data["exports"] == ["tool_metadata", "execute"]
    and {"glaw", "glaw-host", "glaw-mcp", "glaw-rbac"} <= names
    and data["permissions"]["hardware"] == "denied"
    and data["safety_contract"]["human_seal_role"] == "ADMIN"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "Extism metadata exports tools, permissions, and safety contract"

"$EXT" execute --payload '{"tool":"glaw","args":["version"]}' --json > "$TMP/exec-ok.json"; rc=$?
python3 - "$TMP/exec-ok.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data["status"] == "pass" and data["plugin"] == "glaw-extism" and data["pre_guard"]["status"] == "pass"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "Extism execute delegates through guarded host adapter"

"$EXT" execute --payload '{"tool":"../../bin/glaw","args":["version"]}' --json > "$TMP/path-block.json"; rc=$?
python3 - "$TMP/path-block.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data["status"] == "blocked" and "whitelisted" in data["reason"] and data["plugin"] == "glaw-extism"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "Extism execute blocks path traversal through host adapter"

"$EXT" execute --payload '{"tool":"glaw-irs-file","args":["submit","missing.json","--live"],"matter":"x"}' --json > "$TMP/live-block.json"; rc=$?
python3 - "$TMP/live-block.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
failures = {f["id"] for f in data.get("pre_guard", {}).get("failures", [])}
ok = data["status"] == "blocked" and "human_authority_live_filing" in failures
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "Extism execute preserves human-seal pre-call block"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

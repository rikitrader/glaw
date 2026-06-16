#!/usr/bin/env bash
# mcp_test.sh - source-only MCP-style bridge regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
MCP="$ROOT/bin/glaw-mcp"

"$MCP" tools --json > "$TMP/tools.json"; rc=$?
python3 - "$TMP/tools.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
names = {tool["name"] for tool in data["tools"]}
need = {"glaw_manifest", "glaw_status", "glaw_execute"}
sys.exit(0 if need <= names else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "MCP tool list exposes manifest/status/execute"

"$MCP" call glaw_execute --arguments '{"tool":"glaw","args":["version"],"role":"READER","actor":"MCP Reader"}' --json > "$TMP/call-ok.json"; rc=$?
python3 - "$TMP/call-ok.json" <<'PY'
import json, sys
outer = json.load(open(sys.argv[1], encoding="utf-8"))
inner = json.loads(outer["content"][0]["text"])
ok = outer["isError"] is False and inner["status"] == "pass" and inner["rbac"]["status"] == "pass" and inner["pre_guard"]["status"] == "pass"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "MCP glaw_execute delegates through guarded host adapter"

"$MCP" call glaw_execute --arguments '{"tool":"glaw-irs-file","args":["submit","missing.json","--live"],"matter":"mcp-test"}' --json > "$TMP/call-rbac-block.json"; rc=$?
python3 - "$TMP/call-rbac-block.json" <<'PY'
import json, sys
outer = json.load(open(sys.argv[1], encoding="utf-8"))
inner = json.loads(outer["content"][0]["text"])
ok = outer["isError"] is True and inner["status"] == "blocked" and inner.get("phase") == "rbac"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "MCP human-only execution is RBAC-blocked at host layer"

"$MCP" call glaw_execute --arguments '{"tool":"../../bin/glaw","args":["version"]}' --json > "$TMP/call-block.json"; rc=$?
python3 - "$TMP/call-block.json" <<'PY'
import json, sys
outer = json.load(open(sys.argv[1], encoding="utf-8"))
inner = json.loads(outer["content"][0]["text"])
ok = outer["isError"] is True and inner["status"] == "blocked" and "whitelisted" in inner["reason"]
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "MCP glaw_execute blocks path traversal"

python3 - "$MCP" "$TMP/rpc.jsonl" <<'PY'
import json, subprocess, sys
mcp = sys.argv[1]
msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "glaw_execute", "arguments": {"tool": "glaw", "args": ["version"], "role": "READER", "actor": "MCP Reader"}}},
]
payload = "\n".join(json.dumps(m) for m in msgs) + "\n"
proc = subprocess.run([mcp, "serve"], input=payload, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
open(sys.argv[2], "w", encoding="utf-8").write(proc.stdout)
sys.exit(proc.returncode)
PY
rc=$?
python3 - "$TMP/rpc.jsonl" <<'PY'
import json, sys
rows = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip()]
ok = (
    len(rows) == 3
    and rows[0]["result"]["capabilities"].get("tools") == {}
    and any(t["name"] == "glaw_execute" for t in rows[1]["result"]["tools"])
    and rows[2]["result"]["isError"] is False
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "MCP serve handles initialize/tools/list/tools/call JSON-RPC lines"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

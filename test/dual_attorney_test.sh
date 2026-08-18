#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export GLAW_BENCHMARK_HOME="$TMP/legal-10k"
export CLAUDE_CLI_COMMAND="glaw-test-missing-claude"
export CODEX_CLI_COMMAND="glaw-test-missing-codex"
"$ROOT/bin/glaw-legal-benchmark" scaffold >/dev/null
cp "$ROOT/benchmarks/legal-10k/source-packets.jsonl" "$GLAW_BENCHMARK_HOME/source-packets.jsonl"
"$ROOT/bin/glaw-legal-benchmark" import --input "$ROOT/benchmarks/legal-10k/source-backed-pilot.jsonl" >/dev/null
set +e
OUTPUT=$("$ROOT/bin/glaw-dual-attorney" --ids BENCH-000001 2>&1)
CODE=$?
set -e
test "$CODE" -eq 0
printf '%s\n' "$OUTPUT" | python3 -c 'import json,sys; x=json.load(sys.stdin); assert x["status"] == "EXECUTED"; assert x["count"] == 1; assert x["results"][0]["governor_status"] == "REVIEW_REQUIRED"; assert "BLUE_AGENT_UNAVAILABLE" in x["results"][0]["reason_codes"]; assert "RED_AGENT_UNAVAILABLE" in x["results"][0]["reason_codes"]'
python3 - "$GLAW_BENCHMARK_HOME/runs/BENCH-000001" <<'PY'
import json, sys
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path.cwd() / 'lib'))
from legal_governor.dual_attorney import MemoryFirewall, MemoryItem, PrivateMemory, SharedMatterMemory
p=Path(sys.argv[1])
for name in ('snapshot.json','blue-first-pass.json','red-first-pass.json','governor.json','audit.jsonl'):
    assert (p/name).is_file(), name
assert json.loads((p/'governor.json').read_text())['decision']=='REVIEW_REQUIRED'
shared=SharedMatterMemory('M'); blue=PrivateMemory('M','alexandra_vale'); red=PrivateMemory('M','victor_sterling')
firewall=MemoryFirewall(shared,blue,red)
try: firewall.read('alexandra_vale','red_private'); raise AssertionError('blue read red memory')
except PermissionError: pass
try: firewall.read('victor_sterling','blue_private'); raise AssertionError('red read blue memory')
except PermissionError: pass
try: firewall.promote(MemoryItem('X','M','finding','model inference','MODEL_ANALYSIS'))
except ValueError: pass
else: raise AssertionError('unverified memory promoted')
PY
echo "ALL PASS"

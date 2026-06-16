#!/usr/bin/env bash
# memory_test.sh - source-linked cross-matter memory and selective retrieval.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
LEARN="$ROOT/bin/glaw-learnings"
REFLECT="$ROOT/bin/glaw-reflect"

"$LEARN" add '{"error_class":"audit-gap","where":"test","wrong":"unsupported number","fix":"cite bank source","confidence":8}' >/tmp/glaw-memory-bad.out 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && grep -q 'source_links required' /tmp/glaw-memory-bad.out && echo 1 || echo 0)" "memory add blocks unsourced defect"

"$LEARN" add '{"error_class":"cite-caption","where":"matter/a","wrong":"case cited without reporter","fix":"verify caption and reporter","authority":"https://www.courtlistener.com/","confidence":9,"matter":"alpha-tax"}' >/dev/null
"$LEARN" add '{"error_class":"state-deadline","where":"matter/b","wrong":"deadline copied from memory","fix":"cite current state source","source_links":["matter:beta docket SRC-0001"],"confidence":8,"matter":"beta-docket"}' >/dev/null
"$LEARN" add '{"error_class":"scotus-misuse","where":"matter/c","wrong":"off-point Supreme Court authority","fix":"confirm holding supports proposition","authority":"https://www.courtlistener.com/","confidence":9,"matter":"gamma-litigation"}' >/dev/null

"$LEARN" query "reporter caption" --json > "$TMP/query.json"; rc=$?
python3 - "$TMP/query.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("error_class") == "cite-caption" and rows[0].get("memory_id", "").startswith("MEM-")
ok = ok and rows[0].get("source_links")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query returns ranked source-linked result"

"$LEARN" preflight alpha-tax --query "citation reporter" > "$TMP/preflight.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'KNOWN DEFECTS' "$TMP/preflight.txt" && grep -q 'cite-caption' "$TMP/preflight.txt" && grep -q 'MEM-' "$TMP/preflight.txt" && echo 1 || echo 0)" "memory preflight emits source-linked digest"

"$REFLECT" --apply > "$TMP/reflect.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q 'Wrote 1 new synthesized knowledge rules' "$TMP/reflect.txt" && grep -q 'Qdrant' "$TMP/reflect.txt" && echo 1 || echo 0)" "reflection writes source-linked synthesized rule in isolated store"

"$LEARN" query "cite discipline" --type knowledge --json > "$TMP/knowledge.json"; rc=$?
python3 - "$TMP/knowledge.json" <<'PY'
import json
import sys

rows = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(rows) and rows[0].get("type") == "knowledge" and rows[0].get("source_links")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "memory query retrieves synthesized knowledge by type"

"$LEARN" stats > "$TMP/stats.txt"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q "store: $TMP/learnings/learnings.jsonl" "$TMP/stats.txt" && grep -q 'source-linked: 4/4' "$TMP/stats.txt" && echo 1 || echo 0)" "memory stats reports isolated source-linked store"

rm -rf "$TMP" /tmp/glaw-memory-bad.out
echo
echo "0 failures - $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit 1; }

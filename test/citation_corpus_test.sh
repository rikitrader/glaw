#!/usr/bin/env bash
# citation_corpus_test.sh - source corpus capture and tamper detection.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
CORPUS="$ROOT/bin/glaw-citation-corpus"
CITES="$ROOT/bin/glaw-citation-gate"

"$GLAW" matter new "Citation Corpus" >/dev/null

"$CORPUS" capture --id CORP-1 --source-url "https://uscode.house.gov/" \
  --text "26 U.S.C. 6001 supports records sufficient to establish tax liability." \
  --segment "records sufficient to establish tax liability" >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "corpus capture writes source and segment hashes"

"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "corpus status validates captured source"

"$CITES" record --id C-1 --proposition "Tax records must support the return" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://example.com/" \
  --reviewer legal-research --support-summary "URL mismatch should fail." \
  --corpus-id CORP-1 >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "citation record blocks corpus/source-url mismatch"

"$CITES" record --id C-1 --proposition "Tax records must support the return" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://uscode.house.gov/" \
  --reviewer legal-research --support-summary "The captured segment supports recordkeeping substantiation." \
  --corpus-id CORP-1 >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "citation record accepts matching corpus id"

"$CITES" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "citation gate completes with validated corpus"

printf 'tampered\n' >> "$TMP/matters/citation-corpus/citation_corpus/CORP-1.txt"
"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "corpus status blocks source text tamper"

"$CITES" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation gate blocks corpus tamper"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

#!/usr/bin/env bash
# citation_typology_test.sh - falsifiable citation defect taxonomy regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
CITES="$ROOT/bin/glaw-citation-gate"

"$GLAW" matter new "Citation Typology" >/dev/null

"$CITES" record --id C-0001 --proposition "Books must be retained" --authority "26 U.S.C. 6001" \
  --status verified --source-url "https://uscode.house.gov/" --reviewer legal-research >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "verified citation blocked without support summary"

"$CITES" record --id C-0001 --proposition "Books must be retained" --authority "26 U.S.C. 6001" \
  --status verified --source-url "https://uscode.house.gov/" --reviewer legal-research \
  --support-summary "The cited section supports recordkeeping duties." --defect-type misgrounded >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "verified citation blocked when defect type is not none"

"$CITES" record --id C-0002 --proposition "Unsupported claim" --authority "Imaginary case" \
  --status struck --source-url "https://example.com/" --reviewer legal-research >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "blocking citation status requires defect type"

"$CITES" record --id C-0002 --proposition "Unsupported claim" --authority "Imaginary case" \
  --status struck --defect-type incorrect --source-url "https://example.com/" \
  --reviewer legal-research --notes "Authority could not be found." >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "incorrect defect type can be recorded"

"$CITES" status > "$TMP/status-blocked.out" 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && grep -q 'incorrect' "$TMP/status-blocked.out" && echo 1 || echo 0)" "status prints typed blocking citation"

"$CITES" record --id C-0002 --proposition "Books must be retained" --authority "26 U.S.C. 6001" \
  --status verified --source-url "https://uscode.house.gov/" --reviewer legal-research \
  --support-summary "The cited section supports recordkeeping duties." >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "typed failed citation can be replaced with verified support"

"$CITES" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "citation gate completes after latest row is verified with support summary"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

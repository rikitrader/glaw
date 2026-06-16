#!/usr/bin/env bash
# compliance_audit_test.sh - CCO compliance-audit classifier regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"
AUDIT="$ROOT/bin/glaw-compliance-audit"
DOCS="$TMP/docs"
mkdir -p "$DOCS"

cat > "$DOCS/articles.md" <<'MD'
Articles of Incorporation
Employer Identification Number: 12-3456789
Registered agent designation accepted.
MD

cat > "$DOCS/bylaws.md" <<'MD'
Bylaws and organizational written consent ratifying initial actions.
Stock-ledger and cap table maintained.
MD

"$AUDIT" "$DOCS" --type s-corp -o "$TMP/audit.md" > "$TMP/audit.out"; rc=$?
ok "$([ "$rc" = 0 ] && [ -s "$TMP/audit.md" ] && echo 1 || echo 0)" "compliance audit writes report"

ok "$([ "$(grep -c '✅ HAVE' "$TMP/audit.md")" -ge 4 ] && echo 1 || echo 0)" "classifier marks matching required documents as HAVE"
ok "$([ "$(grep -c '🟡 ACTION' "$TMP/audit.md")" -ge 1 ] && grep -q 'IRS CP261 acceptance letter' "$TMP/audit.md" && echo 1 || echo 0)" "classifier marks external recurring items as ACTION"
ok "$([ "$(grep -c '❌ GAP' "$TMP/audit.md")" -ge 1 ] && grep -q 'Form 2553 S-election' "$TMP/audit.md" && echo 1 || echo 0)" "classifier marks missing required documents as GAP"
ok "$([ "$(grep -c '⚪ optional-missing' "$TMP/audit.md")" -ge 1 ] && echo 1 || echo 0)" "classifier marks absent optional documents as optional-missing"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

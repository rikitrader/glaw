#!/usr/bin/env bash
# groundedness_test.sh - auditable citation groundedness regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
CORPUS="$ROOT/bin/glaw-citation-corpus"
CITES="$ROOT/bin/glaw-citation-gate"
GROUND="$ROOT/bin/glaw-groundedness"

"$GLAW" matter new "Groundedness" >/dev/null
"$CORPUS" capture --id CORP-1 --source-url "https://uscode.house.gov/" \
  --text "26 U.S.C. 6001 requires tax records sufficient to establish liability." \
  --segment "requires tax records sufficient to establish liability" >/dev/null
"$CITES" record --id C-1 --proposition "Tax records establish liability" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://uscode.house.gov/" \
  --reviewer legal-research --support-summary "The source requires tax records sufficient to establish liability." \
  --corpus-id CORP-1 >/dev/null

"$GROUND" audit --json > "$TMP/ground.json"; rc=$?
python3 - "$TMP/ground.json" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
row = data["rows"][0]
ok = data["status"] == "pass" and row["entity_grounding"] >= 0.3 and row["relation_preservation"] >= 0.2
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "groundedness audit passes source-backed proposition"

"$CITES" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && [ -f "$TMP/matters/groundedness/groundedness.json" ] && echo 1 || echo 0)" "citation completion writes groundedness artifact"

"$GLAW" matter new "Ungrounded" >/dev/null
"$CORPUS" capture --id CORP-2 --source-url "https://example.com/" \
  --text "This segment discusses unrelated venue facts only." \
  --segment "unrelated venue facts" >/dev/null
"$CITES" record --id C-2 --proposition "Tax records establish liability" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://example.com/" \
  --reviewer legal-research --support-summary "The cited source supposedly supports tax records." \
  --corpus-id CORP-2 >/dev/null
"$CITES" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation completion blocks ungrounded verified row"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

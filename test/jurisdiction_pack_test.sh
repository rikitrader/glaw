#!/usr/bin/env bash
# jurisdiction_pack_test.sh - source-backed jurisdiction matrix gate.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"
PACK="$ROOT/bin/glaw-jurisdiction-pack"

"$PACK" scaffold > "$TMP/scaffold.json"; rc=$?
python3 -m json.tool "$TMP/scaffold.json" >/dev/null 2>&1; rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "jurisdiction scaffold emits JSON"

"$PACK" validate "$TMP/scaffold.json" --json > "$TMP/report.json"; rc=$?
python3 - "$TMP/report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=(
    data.get("status") == "pass"
    and data.get("jurisdiction_count") == 1
    and "state regulator" in data.get("required_adversarial_lenses", [])
    and "not legal advice" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "complete jurisdiction pack passes with adversarial lenses"

printf '{"matter":"bad","source_ids":[],"jurisdictions":[]}' > "$TMP/bad.json"
"$PACK" validate "$TMP/bad.json" --json > "$TMP/bad-report.json"; rc=$?
python3 - "$TMP/bad-report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "source_ids" in ids and "jurisdictions" in ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack fails closed without sources or jurisdictions"

python3 - "$TMP/scaffold.json" "$TMP/missing-lens.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
data["jurisdictions"][0]["adversarial_lenses"]=["state regulator"]
json.dump(data, open(sys.argv[2], "w"))
PY
"$PACK" validate "$TMP/missing-lens.json" --json > "$TMP/missing-lens-report.json"; rc=$?
python3 - "$TMP/missing-lens-report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=data.get("status") == "fail" and any(row.get("id") == "adversarial_lenses" for row in data.get("failures", []))
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack fails without required government/adversarial lenses"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

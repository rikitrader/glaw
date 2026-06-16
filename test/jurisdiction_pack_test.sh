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
    data.get("status") == "fail"
    and any(row.get("id") == "placeholder" for row in data.get("failures", []))
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "scaffold fails production validation as placeholder data"

"$PACK" list > "$TMP/list.txt"; rc=$?
grep -q 'jurisdiction/packs/us-core.json' "$TMP/list.txt"; rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack list includes source-backed US core pack"

"$PACK" validate "$ROOT/jurisdiction/packs/us-core.json" --json > "$TMP/us-core-report.json"; rc=$?
python3 - "$TMP/us-core-report.json" "$ROOT/jurisdiction/packs/us-core.json" <<'PY'
import json, sys
report=json.load(open(sys.argv[1]))
pack=json.load(open(sys.argv[2]))
names={row.get("name") for row in pack.get("jurisdictions", [])}
catalog=pack.get("source_catalog", {})
ok=(
    report.get("status") == "pass"
    and report.get("jurisdiction_count") >= 5
    and not report.get("warnings")
    and {"Delaware", "Florida", "Texas", "New York", "Federal"} <= names
    and all(str(row.get("url", "")).startswith("https://") for row in catalog.values())
    and "not legal advice" in report.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "source-backed US core jurisdiction pack passes with zero review warnings"

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

python3 - "$ROOT/jurisdiction/packs/us-core.json" "$TMP/no-catalog.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
data.pop("source_catalog", None)
json.dump(data, open(sys.argv[2], "w"))
PY
"$PACK" validate "$TMP/no-catalog.json" --json > "$TMP/no-catalog-report.json"; rc=$?
python3 - "$TMP/no-catalog-report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=data.get("status") == "fail" and any(row.get("id") == "source_catalog" for row in data.get("failures", []))
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack fails when source_catalog is missing"

python3 - "$ROOT/jurisdiction/packs/us-core.json" "$TMP/missing-catalog-entry.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
data["source_catalog"].pop(data["source_ids"][0])
json.dump(data, open(sys.argv[2], "w"))
PY
"$PACK" validate "$TMP/missing-catalog-entry.json" --json > "$TMP/missing-catalog-entry-report.json"; rc=$?
python3 - "$TMP/missing-catalog-entry-report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=(
    data.get("status") == "fail"
    and any(row.get("id") == "source_catalog" and "missing source_catalog entry" in row.get("detail", "") for row in data.get("failures", []))
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack fails when a cited source lacks catalog metadata"

python3 - "$ROOT/jurisdiction/packs/us-core.json" "$TMP/orphan-catalog-entry.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
data["source_catalog"]["SRC-9999"]={"title":"orphan source","url":"https://example.com/orphan"}
json.dump(data, open(sys.argv[2], "w"))
PY
"$PACK" validate "$TMP/orphan-catalog-entry.json" --json > "$TMP/orphan-catalog-entry-report.json"; rc=$?
python3 - "$TMP/orphan-catalog-entry-report.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=(
    data.get("status") == "fail"
    and any(row.get("id") == "source_catalog" and "not listed in source_ids" in row.get("detail", "") for row in data.get("failures", []))
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "pack fails when source_catalog has orphan entries"

python3 - "$ROOT/jurisdiction/packs/us-core.json" "$TMP/missing-lens.json" <<'PY'
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

#!/usr/bin/env bash
# rbac_test.sh - role/ring/SOC2 audit regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
RBAC="$ROOT/bin/glaw-rbac"

"$RBAC" check --operation audit --role AUDITOR --actor "Casey Auditor" --json > "$TMP/audit-ok.json"; rc=$?
python3 - "$TMP/audit-ok.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if data["status"] == "pass" and data["ring"] == "R1_AUDIT" and "CC7.2" in data["soc2_controls"] else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "AUDITOR can run audit operation with SOC2 mapping"

"$RBAC" check --operation write --role AUDITOR --actor "Casey Auditor" --json > "$TMP/write-deny.json"; rc=$?
python3 - "$TMP/write-deny.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if data["status"] == "fail" and data["ring"] == "R2_WORKPAPER" and "WRITER" in data["allowed_roles"] else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "AUDITOR cannot write workpapers"

"$RBAC" check --operation human_authority --role WRITER --actor "Wendy Writer" --json > "$TMP/seal-deny.json"; rc=$?
ok "$([ "$rc" = 1 ] && grep -q '"ring": "R4_HUMAN_SEAL"' "$TMP/seal-deny.json" && echo 1 || echo 0)" "WRITER cannot exercise human-seal authority"

"$RBAC" check --operation human_authority --role ADMIN --actor "Alex Admin" --resource transmit --json > "$TMP/seal-ok.json"; rc=$?
python3 - "$TMP/seal-ok.json" "$TMP/audit/rbac.jsonl" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
rows = [json.loads(line) for line in open(sys.argv[2], encoding="utf-8") if line.strip()]
ok = (
    data["status"] == "pass"
    and data["ring"] == "R4_HUMAN_SEAL"
    and "CC6.3" in data["soc2_controls"]
    and len(rows) == 4
    and all(row.get("row_hash") for row in rows)
    and rows[-1].get("previous_hash") == rows[-2].get("row_hash")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "ADMIN human-seal pass writes chained audit row"

"$RBAC" audit --json > "$TMP/audit-read.json"; rc=$?
ok "$([ "$rc" = 0 ] && grep -q '"rows"' "$TMP/audit-read.json" && echo 1 || echo 0)" "RBAC audit command reads audit ledger"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

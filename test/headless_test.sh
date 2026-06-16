#!/usr/bin/env bash
# headless_test.sh - spawned/orchestrator headless report regression.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
INTAKE="$ROOT/bin/glaw-intake"
HEAD="$ROOT/bin/glaw-headless"

"$HEAD" --goal "route matter" --json > "$TMP/no-matter.json"; rc=$?
python3 - "$TMP/no-matter.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
ok = data["status"] == "blocked" and data["reason"] == "no active matter" and data["next_owner"] == "orchestrator"
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report blocks clearly when no active matter exists"

"$GLAW" matter new "Headless Routing" >/dev/null
"$INTAKE" set workflow_track accounting-tax >/dev/null
"$GLAW" --headless --goal "complete Fortune 500 accounting/tax gate report" --json > "$TMP/report.json"; rc=$?
python3 - "$TMP/report.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
loop = data.get("loop") or {}
open_gates = {row["stage"] for row in data.get("open_gates", [])}
ok = (
    data["status"] == "blocked"
    and data["matter"] == "headless-routing"
    and data["workflow_track"] == "accounting-tax"
    and data["next_owner"] == "intake"
    and data["next_gate"] == "strategy"
    and "strategy" in open_gates
    and "irs-examiner" in loop.get("adversarial_required", [])
    and "no filing/signing" in data["authority"]
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "glaw --headless emits blocked gate report with next owner and adversarial profile"

printf '{"ts":"t","event":"chief_decision","decision":"PROCEED"}\n' > "$TMP/matters/headless-routing/decisions.jsonl"
cat > "$TMP/matters/headless-routing/final_packet.json" <<'JSON'
{
  "status": "ready",
  "workflow_profile": "accounting-tax",
  "generated_at": "2026-01-01T00:00:00Z",
  "gates": {
    "compliance_manifest_clear": true,
    "government_adversary_manifest_clear": true
  },
  "compliance_manifest": [
    {
      "id": "government-adversary",
      "owner": "glaw-adversarial",
      "status": "pass",
      "next_command": "bin/glaw-adversarial status --profile auto",
      "required_fix": "record surviving government/regulatory/litigation adversary attacks",
      "missing": []
    },
    {
      "id": "accounting-control",
      "owner": "glaw-accounting",
      "status": "fail",
      "next_command": "bin/glaw-accounting-control",
      "required_fix": "run books-doctor, bank reconciliation, ledger, and tax tie-out controls",
      "missing": ["bank_reconciliation"]
    }
  ],
  "government_adversary_manifest": [
    {
      "lens": "irs-examiner",
      "status": "pass",
      "missing": [],
      "evidence_cited_source_ids": ["SRC-0001"],
      "attack_cited_source_ids": ["SRC-0001"]
    }
  ],
  "accounting_control_manifest": {
    "required": true,
    "status": "fail",
    "missing": ["bank_reconciliation"],
    "path": "accounting_control.json"
  }
}
JSON
"$HEAD" --goal "show decisions and artifacts" --matter headless-routing --json > "$TMP/report2.json"; rc=$?
python3 - "$TMP/report2.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
artifacts = {row["path"] for row in data["shipped_artifacts"]}
plan = data.get("compliance_action_plan") or []
ok = (
    data["decisions"]
    and "final_packet.json" in artifacts
    and data["timeline_events"] >= 1
    and data["final_packet"]["status"] == "ready"
    and data["compliance_failures"][0]["id"] == "accounting-control"
    and data["accounting_control_manifest"]["status"] == "fail"
    and data["accounting_control_failures"][0]["missing"] == ["bank_reconciliation"]
    and data["final_packet"]["accounting_control_failures"][0]["path"] == "accounting_control.json"
    and data["government_adversary_manifest"][0]["lens"] == "irs-examiner"
    and not data["government_adversary_failures"]
    and plan
    and plan[0]["id"] == "accounting-control"
    and plan[0]["owner"] == "glaw-accounting"
    and plan[0]["next_command"] == "bin/glaw-accounting-control"
    and "bank reconciliation" in plan[0]["required_fix"]
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report includes decisions, artifacts, timeline count, compliance, government adversary, and accounting-control manifests"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

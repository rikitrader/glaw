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
PREMIUM="$ROOT/bin/glaw-premium-lanes"

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

python3 - "$TMP/report.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
ok = (
    premium.get("present") is False
    and premium.get("status") == "not_required"
    and not data.get("premium_lane_failures")
    and not data.get("premium_lane_action_plan")
    and data.get("premium_lane_requirement", {}).get("basis") == "not_tagged"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report treats untagged matters as no premium lane required"

"$INTAKE" premium founder --slug headless-routing >/dev/null
"$HEAD" --goal "premium lane required" --matter headless-routing --json > "$TMP/report-premium-required.json"; rc=$?
python3 - "$TMP/report-premium-required.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
plan = data.get("premium_lane_action_plan") or []
failures = data.get("premium_lane_failures") or []
ok = (
    premium.get("present") is False
    and premium.get("status") == "fail"
    and data.get("premium_lane_requirement", {}).get("required") is True
    and data.get("premium_lane_requirement", {}).get("required_lanes") == ["founder-unicorn"]
    and failures
    and failures[0].get("id") == "premium_lane_missing"
    and plan
    and plan[0].get("next_command") == "bin/glaw-premium-lanes attach founder-unicorn --matter-slug headless-routing"
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report blocks explicit premium-scope matters until lane packet is attached"

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
      "required_fix": "run books-doctor, bank reconciliation, ledger, tax tie-out, and SEC audit tie-out controls",
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
    and "SEC audit tie-out" in plan[0]["required_fix"]
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report includes decisions, artifacts, timeline count, compliance, government adversary, and accounting-control manifests"

"$PREMIUM" attach founder-unicorn --matter-slug headless-routing --matter "Headless Routing" --json > "$TMP/premium-attach.json"; rc=$?
"$HEAD" --goal "show premium lane status" --matter headless-routing --json > "$TMP/report-premium-fail.json"; rc2=$?
python3 - "$TMP/report-premium-fail.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
artifacts = {row["path"] for row in data.get("shipped_artifacts", [])}
plan = data.get("premium_lane_action_plan") or []
failures = data.get("premium_lane_failures") or []
lane = premium.get("lanes", [{}])[0]
ok = (
    premium.get("present") is True
    and premium.get("status") == "fail"
    and premium.get("lane_count") == 1
    and lane.get("lane_id") == "founder-unicorn"
    and "workpapers/premium-lane-founder-unicorn.json" in artifacts
    and failures
    and plan
    and plan[0]["owner"] == "glaw-premium-lanes"
    and "bin/glaw-premium-lanes complete --lane founder-unicorn" in plan[0]["next_command"]
    and "--matter-slug headless-routing" in plan[0]["next_command"]
    and "--due YYYY-MM-DD" in plan[0]["next_command"]
    and "--source \"SRC-0001 basis\"" in plan[0]["next_command"]
    and "workpapers/premium-lane-founder-unicorn.json" not in plan[0]["next_command"]
    and "<YYYY-MM-DD>" not in plan[0]["next_command"]
    and "<basis>" not in plan[0]["next_command"]
    and "<lead>" not in plan[0]["next_command"]
    and "reviewer_status" not in plan[0]["next_command"]
    and "workstream_owner" in plan[0]["missing"]
    and "report-only" in premium.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "headless report exposes incomplete premium lane packet with action plan"

ARTIFACT="$(python3 - "$TMP/premium-attach.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
python3 - "$ARTIFACT" <<'PY'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
packet=json.load(open(path))
packet["manifest_sha256"]="0"*64
path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
PY
"$HEAD" --goal "show stale premium lane status" --matter headless-routing --json > "$TMP/report-premium-stale.json"; rc=$?
python3 - "$TMP/report-premium-stale.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
lane = premium.get("lanes", [{}])[0]
ids={failure.get("id") for failure in lane.get("failures", [])}
plan = data.get("premium_lane_action_plan") or []
ok = (
    premium.get("present") is True
    and premium.get("status") == "fail"
    and lane.get("status") == "fail"
    and "manifest_stale" in ids
    and plan
    and "bin/glaw-premium-lanes attach founder-unicorn" in plan[0]["next_command"]
    and "--matter-slug headless-routing" in plan[0]["next_command"]
    and "complete --lane" not in plan[0]["next_command"]
    and "render-packet" not in plan[0]["next_command"]
    and "manifest_stale" in plan[0]["missing"]
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "headless report routes stale premium lane packet to manifest reattach"

"$PREMIUM" attach founder-unicorn --matter-slug headless-routing --json > "$TMP/premium-attach-refresh.json"; rc=$?
ARTIFACT="$(python3 - "$TMP/premium-attach-refresh.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
"$PREMIUM" complete "$ARTIFACT" --owner "Lead partner" --docket-owner "Docketing" --due 2026-12-01 --source "SRC-0001 premium headless source" --json > "$TMP/premium-complete.json"; rc=$?
"$HEAD" --goal "show metadata-complete premium lane status" --matter headless-routing --json > "$TMP/report-premium-no-render.json"; rc2=$?
python3 - "$TMP/report-premium-no-render.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
lane = premium.get("lanes", [{}])[0]
ids={failure.get("id") for failure in lane.get("failures", [])}
plan = data.get("premium_lane_action_plan") or []
ok = (
    premium.get("present") is True
    and premium.get("status") == "fail"
    and lane.get("status") == "fail"
    and lane.get("completed_by") == "Lead partner"
    and lane.get("completed_at")
    and "rendered_template_missing" in ids
    and plan
    and "bin/glaw-premium-lanes render-packet --lane founder-unicorn" in plan[0]["next_command"]
    and "--matter-slug headless-routing" in plan[0]["next_command"]
    and "--source \"SRC-0001 basis\"" in plan[0]["next_command"]
    and "workpapers/premium-lane-founder-unicorn.json" not in plan[0]["next_command"]
    and "<basis>" not in plan[0]["next_command"]
    and "<lead>" not in plan[0]["next_command"]
    and "rendered_template_missing" in plan[0]["missing"]
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "headless report keeps metadata-complete premium lane blocked until templates render"

"$PREMIUM" render-packet "$ARTIFACT" --owner "Lead partner" --source "SRC-0001 premium headless source" --json > "$TMP/premium-render.json"; rc=$?
"$HEAD" --goal "show rendered premium lane status" --matter headless-routing --json > "$TMP/report-premium-before-docket.json"; rc2=$?
python3 - "$TMP/report-premium-before-docket.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
lane = premium.get("lanes", [{}])[0]
ids={failure.get("id") for failure in lane.get("failures", [])}
plan = data.get("premium_lane_action_plan") or []
ok = (
    premium.get("present") is True
    and premium.get("status") == "fail"
    and lane.get("status") == "fail"
    and lane.get("check_packet_status") == "pass"
    and lane.get("docketed") is False
    and "docket_materialized" in ids
    and lane.get("completed_by") == "Lead partner"
    and lane.get("completed_at")
    and plan
    and "bin/glaw-premium-lanes docket --lane founder-unicorn" in plan[0]["next_command"]
    and "docket_materialized" in plan[0]["missing"]
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "headless report keeps rendered premium lane blocked until docket materialization"

"$PREMIUM" docket "$ARTIFACT" --json > "$TMP/premium-docket.json"; rc=$?
"$HEAD" --goal "show completed premium lane status" --matter headless-routing --json > "$TMP/report-premium-pass.json"; rc2=$?
python3 - "$TMP/report-premium-pass.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
premium = data.get("premium_lanes") or {}
lane = premium.get("lanes", [{}])[0]
artifacts={row.get("path") for row in data.get("shipped_artifacts", [])}
ok = (
    premium.get("present") is True
    and premium.get("status") == "pass"
    and not data.get("premium_lane_failures")
    and not data.get("premium_lane_action_plan")
    and lane.get("status") == "pass"
    and lane.get("docketed") is True
    and lane.get("completed_by") == "Lead partner"
    and lane.get("completed_at")
    and any(path.startswith("drafts/premium-lane-founder-unicorn/") for path in artifacts)
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "headless report marks docketed premium lane packet as pass"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

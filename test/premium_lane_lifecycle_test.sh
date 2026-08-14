#!/usr/bin/env bash
# premium_lane_lifecycle_test.sh - every premium lane survives attach -> complete -> docket -> headless.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
TMP="$(mktemp -d)"
export GLAW_HOME="$TMP/glaw-home"
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

GLAW="$ROOT/bin/glaw"
LANES="$ROOT/bin/glaw-premium-lanes"
HEAD="$ROOT/bin/glaw-headless"

for lane in fortune500-enterprise tax-system founder-unicorn uhnw-family-office; do
  matter="Lifecycle $lane"
  "$GLAW" matter new "$matter" >/dev/null
  slug="$(printf '%s' "$matter" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
  "$LANES" attach "$lane" --matter-slug "$slug" --matter "$matter" --json > "$TMP/$lane.attach.json"; rc=$?
  python3 - "$TMP/$lane.attach.json" "$lane" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane=sys.argv[2]
ok=data.get("status") == "attached" and data.get("lane_id") == lane and data.get("artifact", "").endswith(f"premium-lane-{lane}.json")
sys.exit(0 if ok else 1)
PY
  rc2=$?
  ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "$lane attaches as active matter workpaper"

  artifact="$(python3 - "$TMP/$lane.attach.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
  "$LANES" complete "$artifact" --owner "Premium lane lead" --docket-owner "Docket desk" --due 2026-12-15 --source "SRC-0001 premium lifecycle source" --json > "$TMP/$lane.complete.json"; rc=$?
  "$LANES" check-packet "$artifact" --json > "$TMP/$lane.check-before-render.json"; rc2=$?
  "$LANES" render-packet "$artifact" --owner "Premium lane lead" --source "SRC-0001 premium lifecycle source" --json > "$TMP/$lane.render.json"; rc_render=$?
  "$LANES" check-packet "$artifact" --json > "$TMP/$lane.check.json"; rc3=$?
  ok "$([ "$rc" = 1 ] && [ "$rc2" = 1 ] && [ "$rc_render" = 0 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "$lane packet requires rendered templates before readiness check passes"

  "$HEAD" --goal "premium lane lifecycle visibility" --matter "$slug" --json > "$TMP/$lane.headless-before-docket.json"; rc=$?
  python3 - "$TMP/$lane.headless-before-docket.json" "$lane" <<'PY'
import json, sys
headless=json.load(open(sys.argv[1]))
lane=sys.argv[2]
premium=headless.get("premium_lanes", {})
lane_rows=premium.get("lanes", [])
failures=premium.get("failures", [])
action=premium.get("action_plan", [])
failure_ids={row.get("id") for row in failures if isinstance(row, dict)}
ok=(
    premium.get("present") is True
    and premium.get("status") == "fail"
    and lane_rows
    and lane_rows[0].get("lane_id") == lane
    and lane_rows[0].get("check_packet_status") == "pass"
    and lane_rows[0].get("docketed") is False
    and "docket_materialized" in failure_ids
    and action
    and f"bin/glaw-premium-lanes docket --lane {lane}" in action[0].get("next_command", "")
    and headless.get("premium_lane_failures")
    and headless.get("premium_lane_action_plan")
)
sys.exit(0 if ok else 1)
PY
  rc2=$?
  ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "$lane headless status blocks packet-ready lane until docket materialization"

  "$LANES" docket "$artifact" --json > "$TMP/$lane.docket.json"; rc=$?
  "$HEAD" --goal "premium lane lifecycle visibility" --matter "$slug" --json > "$TMP/$lane.headless.json"; rc2=$?
  python3 - "$TMP/$lane.docket.json" "$TMP/$lane.render.json" "$TMP/$lane.headless.json" "$GLAW_HOME" "$slug" "$lane" <<'PY'
import json, sys
from pathlib import Path
docket_report=json.load(open(sys.argv[1]))
render_report=json.load(open(sys.argv[2]))
headless=json.load(open(sys.argv[3]))
home=Path(sys.argv[4])
slug=sys.argv[5]
lane=sys.argv[6]
matter=home/"matters"/slug
packet=json.load(open(matter/"workpapers"/f"premium-lane-{lane}.json"))
docket_rows=[json.loads(line) for line in (matter/"docket.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
timeline=(matter/"timeline.jsonl").read_text(encoding="utf-8")
premium=headless.get("premium_lanes", {})
lane_rows=premium.get("lanes", [])
rendered=render_report.get("rendered", [])
template_texts=[(matter/row.get("path", "")).read_text(encoding="utf-8") for row in rendered if (matter/row.get("path", "")).is_file()]
artifacts={row.get("path") for row in headless.get("shipped_artifacts", [])}
ok=(
    docket_report.get("status") == "pass"
    and render_report.get("status") == "pass"
    and len(docket_report.get("docketed", [])) == len(packet.get("docket_items", []))
    and len(rendered) == len(packet.get("required_packet", []))
    and all("Owner:" in text and "Evidence:" in text and "Sign-off conditions:" in text for text in template_texts)
    and all("DRAFT CONTENT TO BE COMPLETED" not in text and "REVIEW:" not in text for text in template_texts)
    and all(row.get("path") in artifacts for row in rendered)
    and len(docket_rows) == len(packet.get("docket_items", []))
    and all(row.get("lane_id") == lane for row in docket_rows)
    and all(row.get("premium_lane_artifact") == f"workpapers/premium-lane-{lane}.json" for row in docket_rows)
    and "premium_lane_attached" in timeline
    and "premium_lane_packet_completed" in timeline
    and "premium_lane_docketed" in timeline
    and "premium_lane_templates_rendered" in timeline
    and premium.get("present") is True
    and premium.get("status") == "pass"
    and premium.get("lane_count") == 1
    and lane_rows
    and lane_rows[0].get("lane_id") == lane
    and lane_rows[0].get("status") == "pass"
    and not headless.get("premium_lane_failures")
    and not headless.get("premium_lane_action_plan")
)
sys.exit(0 if ok else 1)
PY
  rc3=$?
  ok "$([ "$rc" = 0 ] && [ "$rc_render" = 0 ] && [ "$rc2" = 1 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "$lane docket rows, templates, and headless premium status are lifecycle-consistent"
done

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit 1; }

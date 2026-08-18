#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export GLAW_HOME="$TMP/glaw-home"
"$ROOT/bin/glaw" matter new "Founder Control Assurance Fixture" >/dev/null
slug="founder-control-assurance-fixture"
"$ROOT/bin/glaw-premium-lanes" attach founder-control-assurance --matter-slug "$slug" --json > "$TMP/attach.json"
python3 - "$TMP/attach.json" <<'PY'
import json, sys
from pathlib import Path
d=json.load(open(sys.argv[1]))
assert d["status"] == "attached"
assert d["lane_id"] == "founder-control-assurance"
packet=Path(d["artifact"])
assert packet.is_file()
assert json.loads(packet.read_text())["required_lane_packet"]
PY
mkdir -p "$TMP/glaw-home/matters/$slug/evidence"
cat > "$TMP/glaw-home/matters/$slug/evidence/control-input.json" <<'JSON'
{
  "schema": "glaw-founder-control/v2",
  "denominator_basis": "fully_diluted_economic_ownership",
  "founder_holder": "Founder",
  "threshold_percent": "5.01",
  "vote_floor_percent": "50.1",
  "economic": [{"id":"founder","holder":"Founder","shares":"5.01"},{"id":"investors","holder":"Investors","shares":"94.99"}],
  "voting": [{"id":"founder","holder":"Founder","shares":"5.01","votes_per_share":"100"},{"id":"investors","holder":"Investors","shares":"94.99","votes_per_share":"1"}]
}
JSON
"$ROOT/bin/glaw-founder-control" ledger --matter-slug "$slug" --event-type transfer --holder Founder --shares 1 --effective-date 2026-08-18 --from-holder Founder --to-holder FounderTrust --reason "permitted estate-planning transfer" --source "SRC-0001 assurance fixture" --reviewer "Assurance Lead" --seal-id "SEAL-001" >/dev/null
CERT_FLAGS=(--cap-table-reconciled --voting-universe-reconciled --control-math-passed --dilution-reviewed --transfer-conversion-reviewed --document-precedence-clear --case-law-index-reviewed --jurisdiction-and-forum-reviewed --fiduciary-process-reviewed --accounting-tax-disclosure-handoff --human-seal-recorded)
"$ROOT/bin/glaw-founder-control" certify --matter-slug "$slug" --input "$TMP/glaw-home/matters/$slug/evidence/control-input.json" --reviewer "Assurance Lead" --seal-id "SEAL-001" --source "SRC-0001 assurance fixture" "${CERT_FLAGS[@]}" >/dev/null
"$ROOT/bin/glaw-founder-control" verify --matter-slug "$slug" >/dev/null
if "$ROOT/bin/glaw-premium-lanes" complete --lane founder-control-assurance --matter-slug "$slug" --owner "Assurance Lead" --docket-owner "Docket Desk" --due 2026-12-31 --source "SRC-0001 assurance fixture" >/dev/null; then
  echo "FAIL: completion must remain blocked until templates are rendered" >&2
  exit 1
fi
"$ROOT/bin/glaw-premium-lanes" render-packet --lane founder-control-assurance --matter-slug "$slug" --owner "Assurance Lead" --source "SRC-0001 assurance fixture" >/dev/null
"$ROOT/bin/glaw-premium-lanes" complete --lane founder-control-assurance --matter-slug "$slug" --owner "Assurance Lead" --docket-owner "Docket Desk" --due 2026-12-31 --source "SRC-0001 assurance fixture" >/dev/null
"$ROOT/bin/glaw-premium-lanes" check-packet --lane founder-control-assurance --matter-slug "$slug" >/dev/null
"$ROOT/bin/glaw-premium-lanes" docket --lane founder-control-assurance --matter-slug "$slug" >/dev/null
python3 - "$ROOT/lib/client-lanes/founder-control-document-manifest.json" <<'PY'
import json, sys
d=json.load(open(sys.argv[1]))
assert d["authority_order"][0] == "mandatory_delaware_law"
assert d["authority_order"][-1] == "internal_policies"
assert "conflicts fail closed" in d["conflict_rule"]
PY
echo "ALL PASS"

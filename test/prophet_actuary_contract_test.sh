#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

"$ROOT/bin/glaw-prophet-actuary" scaffold --review-id PA-0001 --question "Is this IFRS 17 reserve model reliable?" --domain IFRS17 > "$TMP/review.json"
"$ROOT/bin/glaw-prophet-actuary" validate "$TMP/review.json" > "$TMP/validate-incomplete.json"
"$ROOT/bin/glaw-prophet-actuary" score "$TMP/review.json" > "$TMP/score-incomplete.json"
python3 - "$TMP/validate-incomplete.json" "$TMP/score-incomplete.json" <<'PY'
import json, sys
assert json.load(open(sys.argv[1]))["valid"] is True
assert json.load(open(sys.argv[2]))["verdict"] == "BLOCK"
PY

python3 - "$TMP/review.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
p["evidence"] = [{"source_id":"SRC-0001","authority_tier":1,"version":"current","effective_date":"2026-01-01","citation":"official section 1"}]
p["scores"] = {"retrieval":96,"data":94,"methodology":92,"calculation":95,"regulatory":91,"model":93}
p["gates"] = {"source_validated":True,"independent_calculation":True,"adversarial_review":True,"regulatory_review":True,"qa_complete":True,"human_actuary_required":False,"qualification_verified":True}
p["professional_posture"] = {"education":["Actuarial Science"],"credentials":["ASA"],"human_reviewer_required":True,"verified":True}
p["findings"] = []
p["verdict"] = "PASS"
json.dump(p, open(sys.argv[1], "w"))
PY
"$ROOT/bin/glaw-prophet-actuary" validate "$TMP/review.json" > "$TMP/validate-complete.json"
"$ROOT/bin/glaw-prophet-actuary" score "$TMP/review.json" > "$TMP/score-complete.json"
"$ROOT/bin/glaw-prophet-actuary" stress --metric reserve --base 100 > "$TMP/stress.json"
"$ROOT/bin/glaw-prophet-actuary" reconcile --opening 100 --inflows 20 --outflows 30 --closing 90 > "$TMP/reconcile-pass.json"
if "$ROOT/bin/glaw-prophet-actuary" reconcile --opening 100 --inflows 20 --outflows 30 --closing 95 > "$TMP/reconcile-block.json"; then exit 1; fi
"$ROOT/bin/glaw-prophet-actuary" route "Review IFRS 17 CSM and risk adjustment" > "$TMP/route.json"
python3 - "$TMP/validate-complete.json" "$TMP/score-complete.json" "$TMP/stress.json" "$TMP/reconcile-pass.json" "$TMP/reconcile-block.json" "$TMP/route.json" <<'PY'
import json, sys
validate, score, stress, recon_pass, recon_block, route = [json.load(open(path)) for path in sys.argv[1:]]
assert validate["valid"] is True
assert score["overall"] == 93.5 and score["verdict"] == "PASS"
assert {row["shock_pct"] for row in stress["scenarios"]} == {-20, -10, 0, 10, 20}
assert recon_pass["verdict"] == "PASS" and recon_block["verdict"] == "BLOCK"
assert route["lane"] == "ifrs17-review" and route["department"] == "actuarial-risk"
PY
echo "prophet-actuary contract tests passed"

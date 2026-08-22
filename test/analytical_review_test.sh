#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/bin/glaw-analytical-review"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

"$CLI" scaffold --review-id AR-0001 --matter DEAL-0001 --artifact-type valuation_model > "$TMP/review.json"
python3 - "$TMP/review.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["reviewer"] = "test"
d["scores"] = {"source_accuracy": 18, "model_integrity": 24, "valuation_soundness": 18, "assumption_quality": 13, "scenario_quality": 9, "recommendation_quality": 9}
d["decision"] = "approved_with_conditions"
d["confidence"] = 80
json.dump(d, open(p, "w"), indent=2)
PY
"$CLI" validate "$TMP/review.json" | rg '"valid": true'
"$CLI" score "$TMP/review.json" | rg '"adjusted_score": 91'

python3 - "$TMP/review.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["material_errors"] = ["terminal value formula does not reference the selected WACC"]
json.dump(d, open(p, "w"), indent=2)
PY
"$CLI" score "$TMP/review.json" | rg '"band": "revise_required"'
echo "analytical review contract: ok"

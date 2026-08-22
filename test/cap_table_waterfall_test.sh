#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/bin/glaw-cap-table-waterfall"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/input.json" <<'JSON'
{"analysis_id":"WF-0001","currency":"USD","exit_value":1000,"holders":[
  {"holder_id":"P","name":"Preferred Fund","security_type":"preferred","shares":100,"ownership_pct":50,"preference_amount":600,"participating":false,"conversion_shares":500},
  {"holder_id":"C","name":"Common Holders","security_type":"common","shares":100,"ownership_pct":50}
]}
JSON

"$CLI" validate "$TMP/input.json" | rg '"valid": true'
"$CLI" analyze "$TMP/input.json" | rg '"payout_total": 1000.0'
"$CLI" analyze "$TMP/input.json" | rg '"payout": 833.33333333'
echo "cap table waterfall contract: ok"

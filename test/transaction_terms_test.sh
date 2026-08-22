#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/bin/glaw-transaction-terms"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/input.json" <<'JSON'
{"analysis_id":"TT-0001","target":"TargetCo","bids":[
 {"bid_id":"B1","bidder":"Buyer A","headline_value":1000,"cash_pct":100,"closing_certainty_pct":90,"financing_certainty_pct":100,"regulatory_risk_pct":10,"earnout_value":100,"escrow_value":20},
 {"bid_id":"B2","bidder":"Buyer B","headline_value":950,"cash_pct":80,"stock_pct":20,"closing_certainty_pct":100,"financing_certainty_pct":100,"regulatory_risk_pct":0,"earnout_value":0,"escrow_value":0}
]}
JSON
"$CLI" validate "$TMP/input.json" | rg '"valid": true'
"$CLI" normalize "$TMP/input.json" | rg '"recommended_bid_id": "B2"'
"$CLI" normalize "$TMP/input.json" | rg '"certainty_adjusted_value": 873.0'
echo "transaction terms contract: ok"

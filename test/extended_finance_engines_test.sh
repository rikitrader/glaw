#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/bids.json" <<'JSON'
{"analysis_id":"TT-0002","weights":{"value":50,"execution":30,"cash":10,"terms":10},"bids":[{"bid_id":"B1","certainty_adjusted_value":100,"closing_certainty_pct":90,"financing_certainty_pct":90,"regulatory_risk_pct":10,"cash_pct":100},{"bid_id":"B2","certainty_adjusted_value":80,"closing_certainty_pct":100,"financing_certainty_pct":100,"regulatory_risk_pct":0,"cash_pct":80}]}
JSON
"$ROOT/bin/glaw-bid-comparison" "$TMP/bids.json" | rg '"recommended_bid_id": "B1"'
cat > "$TMP/guidance.json" <<'JSON'
{"guidance_id":"G-0001","recommended_action":"maintain","scenarios":[{"probability_pct":50,"metrics":{"revenue":100}},{"probability_pct":50,"metrics":{"revenue":120}}]}
JSON
"$ROOT/bin/glaw-guidance-scenarios" "$TMP/guidance.json" | rg '"revenue": 110.0'
cat > "$TMP/register.json" <<'JSON'
{"register_id":"SR-0001","as_of":"2026-08-22","shares_outstanding":1000,"holders":[{"holder_id":"H1","name":"Fund","shares":600,"holder_type":"institutional"},{"holder_id":"H2","name":"Index","shares":300,"holder_type":"passive"}]}
JSON
"$ROOT/bin/glaw-shareholder-register" "$TMP/register.json" | rg '"top10_concentration_pct": 90.0'
"$ROOT/bin/glaw-analytical-review" scaffold --review-id AR-0002 --artifact-type valuation_model > "$TMP/a.json"
cp "$TMP/a.json" "$TMP/b.json"
"$ROOT/bin/glaw-head-to-head" "$TMP/a.json" "$TMP/b.json" | rg '"winner": "tie"'
echo "extended finance engines: ok"

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/request.json" <<'JSON'
{"schema_version":"corporate-finance-pipeline/v1","run_id":"FIN-0001","currency":"USD","valuation_date":"2026-08-22","company":{"tax_rate":0.25,"shares_outstanding":100,"cash":50,"debt":200},"forecast":[{"period":"2027E","revenue":1000,"ebitda":250,"da":50,"capex":60,"nwc":100},{"period":"2028E","revenue":1100,"ebitda":280,"da":55,"capex":65,"nwc":110},{"period":"2029E","revenue":1210,"ebitda":310,"da":60,"capex":70,"nwc":120}],"dcf":{"wacc":0.1,"terminal_growth":0.03},"trading_comps":[{"name":"A","enterprise_value":1000,"ltm_ebitda":100},{"name":"B","enterprise_value":1500,"ltm_ebitda":150}],"transaction_comps":[{"transaction_id":"T1","enterprise_value":1200,"ltm_ebitda":100},{"transaction_id":"T2","enterprise_value":1800,"ltm_ebitda":150}],"merger":{"offer_price":12,"target_shares":50,"cash_pct":0.5,"stock_pct":0.5,"buyer_share_price":20,"buyer_shares":100,"buyer_net_income":200,"target_net_income":40,"synergies":20,"tax_rate":0.25},"waterfall":{"exit_value":1000,"holders":[{"holder":"Founder","ownership_pct":60,"preference":0},{"holder":"Investor","ownership_pct":40,"preference":100}]},"sources":[{"source_id":"SRC-1","version":"approved"}]}
JSON
"$ROOT/bin/glaw-corporate-finance" validate "$TMP/request.json" | rg '"valid": true'
"$ROOT/bin/glaw-corporate-finance" run "$TMP/request.json" > "$TMP/result.json"
python3 - "$TMP/result.json" <<'PY'
import json, sys
r=json.load(open(sys.argv[1]))
assert r["status"] == "REVIEW"
assert r["validation"]["passed"]
assert r["three_statement"]["balance_sheet_balances"]
assert r["three_statement"]["cash_roll_forward"]
assert r["waterfall"]["conserves_value"]
assert r["dcf"]["sensitivity"]["implied_price"][1][1] == r["dcf"]["implied_price"]
assert r["merger"]["pro_forma_eps"] > 0
PY
echo "corporate finance pipeline: ok"

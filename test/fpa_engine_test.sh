#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/request.json" <<'JSON'
{"schema_version":"fpa-pipeline/v1","run_id":"FPA-0001","currency":"USD","periods":["2027E","2028E"],"budget":[{"period":"2027E","revenue":1000,"cogs":400,"opex":300,"capex":100,"nwc":50},{"period":"2028E","revenue":1150,"cogs":450,"opex":330,"capex":120,"nwc":55}],"actuals":[{"period":"2027E","revenue":980,"cogs":390,"opex":310,"capex":95,"nwc":48}],"drivers":{"base_units":100,"price_per_unit":10,"unit_growth":0.1,"price_growth":0.02,"pipeline_coverage":3.2,"minimum_pipeline_coverage":3,"demand_signal":1},"headcount":[{"period":"2027E","starting_fte":100,"planned_hires":10,"planned_exits":3,"approved_hires":12,"annual_cost_per_fte":100000},{"period":"2028E","starting_fte":107,"planned_hires":8,"planned_exits":2,"approved_hires":8,"annual_cost_per_fte":105000}],"capex":[{"project":"ERP","spend":100,"annual_benefit":40,"approved":true,"within_budget":true,"priority":"1"},{"project":"Plant","spend":200,"annual_benefit":25,"approved":false,"within_budget":true,"priority":"2"}],"segments":[{"segment":"North","revenue":600,"direct_cost":250,"allocated_cost":100,"allocation_method":"headcount"},{"segment":"South","revenue":400,"direct_cost":150,"allocated_cost":80,"allocation_method":"revenue"}]}
JSON
"$ROOT/bin/glaw-fpa-engine" validate "$TMP/request.json" | rg '"valid": true'
"$ROOT/bin/glaw-fpa-engine" run "$TMP/request.json" > "$TMP/result.json"
python3 - "$TMP/result.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r["status"]=="REVIEW" and r["validation"]["passed"]
assert r["plan"]["budget_total_revenue"]==2150.0
assert r["plan"]["actualized_periods"]==1
assert r["capex"]["projects"][0]["project"]=="ERP"
assert r["profitability"]["allocation_method_documented"] and r["driver_forecast"]["coverage_ok"]
PY
echo "fpa engine: ok"

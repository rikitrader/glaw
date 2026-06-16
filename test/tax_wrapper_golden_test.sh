#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

assert_json(){
  local file="$1"
  local expr="$2"
  python3 - "$file" "$expr" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
expr=sys.argv[2]
if not eval(expr, {"__builtins__": {}}, {"data": data}):
    raise SystemExit(f"assertion failed: {expr}; data={data}")
PY
}

"$ROOT/bin/glaw-scorp-aaa" --beginning-aaa 1000 --income 500 --loss 200 --distributions 1800 --accumulated-e-and-p 300 --stock-basis 1500 --format json > "$TMP/scorp_aaa.json"
assert_json "$TMP/scorp_aaa.json" "data['ending_aaa']=='0.00' and data['distribution_from_aaa_taxfree']=='1300.00' and data['distribution_dividend_from_aep']=='300.00' and data['distribution_return_of_capital']=='200.00' and data['distribution_capital_gain']=='0.00'"
ok

"$ROOT/bin/glaw-partner-basis" --beginning-basis 100 --contributions 50 --income 40 --tax-exempt-income 10 --liability-increase 100 --distributions 80 --liability-decrease 20 --nondeductible 30 --loss 200 --format json > "$TMP/partner_basis.json"
assert_json "$TMP/partner_basis.json" "data['ending_basis']=='0.00' and data['loss_allowed']=='170.00' and data['loss_suspended']=='30.00' and data['excess_distribution_gain']=='0.00'"
ok

"$ROOT/bin/glaw-subpart-f" --gross-subpart-f 800000 --total-gross-income 10000000 --current-e-and-p 1000000 --shareholder-pct 60 --format json > "$TMP/subpart_f.json"
assert_json "$TMP/subpart_f.json" "data['de_minimis_threshold']=='500000.00' and data['subpart_f_income']=='800000.00' and data['shareholder_inclusion']=='480000.00'"
ok

printf '[{"income":1000,"in_state_sales":100,"everywhere_sales":1000},{"income":2000,"in_state_sales":200,"everywhere_sales":1000}]' > "$TMP/members.json"
"$ROOT/bin/glaw-combined-unitary" "$TMP/members.json" --rate-pct 8 --format json > "$TMP/combined.json"
assert_json "$TMP/combined.json" "data['members']==2 and data['combined_income']=='3000.00' and data['combined_apportionment_pct']=='15.0000' and data['apportioned_income']=='450.00' and data['state_tax']=='36.00'"
ok

"$ROOT/bin/glaw-tfrp" --withheld-income-tax 10000 --employee-fica 5000 --responsible-factors check_signing_authority,controls_payroll --willful-factors knew_taxes_unpaid,paid_other_creditors_instead --format json > "$TMP/tfrp.json"
assert_json "$TMP/tfrp.json" "data['trust_fund_amount']=='15000.00' and data['responsible_score']==50 and data['willful_score']==70 and data['personally_liable'] is True and data['tfrp_exposure']=='15000.00'"
ok

"$ROOT/bin/glaw-ptet" --pass-through-income 100000 --ptet-rate-pct 6.5 --owner-share-pct 60 --federal-marginal-pct 37 --format json > "$TMP/ptet.json"
assert_json "$TMP/ptet.json" "data['ptet_tax']=='6500.00' and data['owner_credit']=='3900.00' and data['federal_deduction_benefit']=='2405.00'"
ok

printf '[{"name":"home","value":100000,"loan":60000},{"name":"car","value":10000,"loan":10000}]' > "$TMP/assets.json"
"$ROOT/bin/glaw-oic" --assets "$TMP/assets.json" --monthly-income 5000 --allowable-expenses 4000 --offer-type lump --format json > "$TMP/oic.json"
assert_json "$TMP/oic.json" "data['net_realizable_equity']=='20000.00' and data['net_monthly_income']=='1000.00' and data['future_income_multiplier']==12 and data['future_income_value']=='12000.00' and data['minimum_offer']=='32000.00'"
ok

"$ROOT/bin/glaw-sfr" --gross-income 50000 --sfr-tax 10000 --correct-tax 6000 --format json > "$TMP/sfr.json"
assert_json "$TMP/sfr.json" "data['sfr_liability']=='10000.00' and data['correct_liability']=='6000.00' and data['savings_from_replacing']=='4000.00' and data['recommend_replace'] is True"
ok

"$ROOT/bin/glaw-wbo-award" --collected-proceeds 3000000 --taxpayer-gross-income 250000 --positive-factors 3 --negative-factors 0 --format json > "$TMP/wbo.json"
assert_json "$TMP/wbo.json" "data['qualifies_7623b']=='yes' and data['award_low']=='450000.00' and data['award_high']=='900000.00' and data['award_likely']=='900000.00'"
ok

"$ROOT/bin/glaw-qm" damages --value 10000 --paid 2000 --due 2026-01-01 --asof 2026-01-31 --rate 0.12 > "$TMP/qm.txt"
grep -q 'Outstanding balance .......... $8,000.00' "$TMP/qm.txt"
grep -q 'Prejudgment interest ......... $78.90' "$TMP/qm.txt"
grep -q 'TOTAL JUDGMENT SOUGHT ........ $8,078.90' "$TMP/qm.txt"
ok

echo "$pass passed"

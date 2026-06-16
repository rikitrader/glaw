#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
export GLAW_HOME="$TMP/home"
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
if not eval(expr, {"__builtins__": {}}, {"data": data, "len": len, "set": set}):
    raise SystemExit(f"assertion failed: {expr}; data={data}")
PY
}

"$ROOT/bin/glaw-child-support" --net-resources 10000 --children 2 --other-children 1 --format json > "$TMP/child.json"
assert_json "$TMP/child.json" "data['net_resources_applied']=='9200.00' and data['guideline_percentage']=='22.50' and data['guideline_monthly_support']=='2070.00'"
ok

"$ROOT/bin/glaw-fbar-8938" --max-aggregate 80000 --year-end-aggregate 60000 --status single --residence us --cfc-inclusion 100000 --format json > "$TMP/fbar.json"
assert_json "$TMP/fbar.json" "data['fbar_fincen114_required']=='YES' and data['form_8938_required']=='YES' and data['sec962_election']['rough_year1_saving']=='26500.00'"
ok

"$ROOT/bin/glaw-form706" --gross-estate 15000000 --funeral-admin 100000 --debts-claims 200000 --year 2025 --format json > "$TMP/form706.json"
assert_json "$TMP/form706.json" "data['taxable_estate']=='14700000.00' and data['applicable_credit_amount']=='5541800.00' and data['net_estate_tax']=='284000.00'"
ok

"$ROOT/bin/glaw-form709" --current-gifts 100000 --num-donees 2 --year 2025 --format json > "$TMP/form709.json"
assert_json "$TMP/form709.json" "data['total_annual_exclusion']=='38000.00' and data['taxable_gifts_this_year']=='62000.00' and data['gift_tax_due']=='0.00'"
ok

"$ROOT/bin/glaw-form990" --gross-receipts 300000 --total-assets 600000 --gross-ubi 10000 --directly-connected-deductions 2000 --public-support 40000 --total-support 100000 --format json > "$TMP/form990.json"
assert_json "$TMP/form990.json" "data['required_annual_return']=='990 (full)' and data['ubit']['net_ubti']=='7000.00' and data['ubit']['ubit_tax']=='1470.00' and data['public_support_test']['public_support_pct']=='40.00'"
ok

cat > "$TMP/chart.json" <<'JSON'
{
  "default": "Expenses:Uncategorized",
  "rules": [
    {"pattern": "stripe", "account": "Revenue:Sales"},
    {"pattern": "rent", "account": "Expenses:Rent"}
  ]
}
JSON
"$ROOT/bin/glaw-coa" validate "$TMP/chart.json" --format json > "$TMP/coa.json"
assert_json "$TMP/coa.json" "data['ok'] is True and data['rule_count']==2 and 'Revenue:Sales' in data['accounts'] and data['warnings']"
ok

printf 'Roe v. Wade, 410 U.S. 113 (1973); 26 U.S.C. § 1368; Fed. R. Civ. P. 12(b)(6).' | "$ROOT/bin/glaw-cites" - --json > "$TMP/cites.json"
assert_json "$TMP/cites.json" "len(data)==4 and {row['type'] for row in data}=={'FullCaseCitation','ReporterCitation','StatuteCitation','RuleCitation'}"
ok

"$ROOT/bin/glaw-journal" --book gap --date 2025-12-31 --memo open --debit Assets:Bank:Checking 100 --credit Equity:Capital 100 >/dev/null
"$ROOT/bin/glaw-journal" --book gap --date 2026-01-15 --memo sale --debit Assets:Bank:Checking 50 --credit Revenue:Sales 50 >/dev/null
"$ROOT/bin/glaw-ledger" --book gap balances --format json > "$TMP/ledger.json"
assert_json "$TMP/ledger.json" "data['balanced'] is True and data['total_debit']=='150' and data['total_credit']=='150'"
ok

"$ROOT/bin/glaw-cashflow" --book gap --period 2026-01 --format json > "$TMP/cashflow.json"
assert_json "$TMP/cashflow.json" "data['reconciles'] is True and data['net_income']=='50' and data['net_change_in_cash']=='50'"
ok

echo "$pass passed"

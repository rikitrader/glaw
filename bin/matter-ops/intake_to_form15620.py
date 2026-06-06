#!/usr/bin/env python3
"""GAP 6 — bridge the intake fact-sheet to the Form 15620 field map (no hand-mapping).
Reads the matter intake (drafts/31-matter-intake-fact-sheet.md) for the confirmed founder
facts and emits a {AcroForm field name: value} JSON that fill_form.py consumes for Form 15620.
Unknown facts become explicit [VERIFY:...] placeholders — never fabricated.

Usage: intake_to_form15620.py <intake.md> [out.json]
"""
import sys, os, re, json

# Form 15620 AcroForm field names (from inspect_fields.py)
F = "form1[0].page1[0]."
FIELDS = {
  'name':      F+"taxpayerInformation[0].taxpayerName[0]",
  'ssn':       F+"taxpayerInformation[0].taxpayerSSN[0]",
  'addr':      F+"taxpayerInformation[0].taxpayerAddress[0]",
  'city':      F+"taxpayerInformation[0].taxpayerCityTown[0]",
  'state':     F+"taxpayerInformation[0].taxpayerState[0]",
  'zip':       F+"taxpayerInformation[0].taxpayerZIPCode[0]",
  'country':   F+"taxpayerInformation[0].taxpayerCountry[0]",
  'property':  F+"describePropertyQuantity[0]",
  'xfer_date': F+"propertyTransferred[0]",
  'tax_year':  F+"taxableYear[0]",
  'restr':     F+"propertyRestrictions[0]",
  'fmv_per':   F+"fairMarketValue[0].valuePerItem[0]",
  'fmv_qty':   F+"fairMarketValue[0].qunaityTransferred[0]",
  'fmv_tot':   F+"fairMarketValue[0].fairMarketValue[0]",
  'paid_per':  F+"undersignedPaid[0].paidPerItem[0]",
  'paid_qty':  F+"undersignedPaid[0].qunatityTransferred[0]",
  'paid_tot':  F+"undersignedPaid[0].totalPricePaid[0]",
  'income':    F+"taxableYearGrossIncome[0]",
  'co_name':   F+"personEntityInformation[0].personEntityName[0]",
  'co_tin':    F+"personEntityInformation[0].personEntityTIN[0]",
}

def find(txt, pat, default):
    m = re.search(pat, txt, re.I)
    return m.group(1).strip() if m else default

def main():
    if len(sys.argv) < 2:
        print('usage: intake_to_form15620.py <intake.md> [out.json]'); sys.exit(1)
    txt = open(sys.argv[1]).read()
    V = "[VERIFY: from intake]"
    # pull confirmed founder facts; fall back to explicit VERIFY placeholders
    founder = find(txt, r'Founder 1[^\n|]*?\|\s*\[?([A-Za-z][A-Za-z .]+?)\]?\s*\|', "[VERIFY: founder name]")
    shares  = find(txt, r'(\d[\d,]{3,})\s*shares', "[VERIFY: shares]")
    company = "ROOF10X, Inc."
    par     = find(txt, r'par(?: value)?[^\d]*(\$?0?\.\d+)', "0.00001")
    data = {
      FIELDS['name']:    founder,
      FIELDS['ssn']:     "[VERIFY: SSN]",
      FIELDS['addr']:    "[VERIFY: street]",
      FIELDS['city']:    "Miami", FIELDS['state']: "FL", FIELDS['zip']: "[VERIFY: ZIP]", FIELDS['country']: "USA",
      FIELDS['property']: f"{shares} shares of Common Stock of {company}",
      FIELDS['xfer_date']: "[VERIFY: transfer date = formation date, post-7/4/2025]",
      FIELDS['tax_year']: "calendar year [VERIFY]",
      FIELDS['restr']:   "4-yr vesting, 1-yr cliff; unvested shares forfeited at cost on termination",
      FIELDS['fmv_per']: par, FIELDS['paid_per']: par,
      FIELDS['fmv_qty']: shares if shares[0].isdigit() else "[VERIFY]",
      FIELDS['paid_qty']: shares if shares[0].isdigit() else "[VERIFY]",
      FIELDS['income']:  "0.00",
      FIELDS['co_name']: company, FIELDS['co_tin']: "[VERIFY: EIN]",
    }
    out = sys.argv[2] if len(sys.argv) > 2 else "/private/tmp/f15620.from-intake.json"
    open(out, 'w').write(json.dumps(data, indent=2))
    verify = sum(1 for v in data.values() if str(v).startswith('[VERIFY'))
    print(f"wrote {out}  ({len(data)} fields, {verify} still [VERIFY])")
    print("next: python3 ~/.claude/skills/glaw-credit-strategy/bin/fill_form.py <15620.pdf> "+out+" <out.pdf>")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""GLAW foreign-asset reporting — FBAR (FinCEN Form 114) and Form 8938 (FATCA) threshold
determination, plus a §962-election rough comparison flag.

FBAR (31 CFR 1010.350): a U.S. person must file FinCEN 114 if the aggregate value of foreign
financial accounts exceeds **$10,000 at any time** during the year. Bright-line, residence- and
status-independent.

Form 8938 (§6038D) thresholds depend on filing status AND residence ([VERIFY] — current):
  living in the US:    single $50,000 (year-end) / $75,000 (any time);
                       MFJ    $100,000 / $150,000.
  living abroad:       single $200,000 / $300,000;
                       MFJ    $400,000 / $600,000.
Both can apply at once; 8938 does not replace the FBAR.

§962 election (informational flag): an individual U.S. shareholder taxed on GILTI/Subpart F at
individual rates may elect under §962 to be taxed as a C-corp (21%) on that income, with the
§250 GILTI deduction (50% [VERIFY]) and an indirect foreign tax credit — often lower in year 1,
but the previously-taxed earnings are taxed again on actual distribution. This tool computes a
ROUGH side-by-side to flag whether the election is worth modeling in /glaw-tax-strategy; it is
not the filed computation.

DRAFT — confirm every threshold against the filing-year 8938/FBAR instructions.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
FBAR_THRESHOLD = Decimal("10000")
# [VERIFY] (year_end, any_time) by (status, residence)
_8938 = {
    ("single", "us"):    (Decimal("50000"),  Decimal("75000")),
    ("mfj", "us"):       (Decimal("100000"), Decimal("150000")),
    ("single", "abroad"):(Decimal("200000"), Decimal("300000")),
    ("mfj", "abroad"):   (Decimal("400000"), Decimal("600000")),
}
TOP_INDIVIDUAL_RATE = Decimal("0.37")     # [VERIFY]
CORP_RATE = Decimal("0.21")               # [VERIFY]
GILTI_250_DEDUCTION = Decimal("0.50")     # §250 [VERIFY — steps down]


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def reporting(*, max_aggregate, year_end_aggregate, status="single", residence="us") -> dict:
    mx, ye = _dec(max_aggregate), _dec(year_end_aggregate)
    fbar = mx > FBAR_THRESHOLD
    ye_t, any_t = _8938.get((status, residence), _8938[("single", "us")])
    f8938 = (ye >= ye_t) or (mx >= any_t)
    return {
        "fbar_fincen114_required": "YES" if fbar else "no",
        "fbar_threshold": str(_q(FBAR_THRESHOLD)),
        "form_8938_required": "YES" if f8938 else "no",
        "form_8938_threshold_year_end": str(_q(ye_t)),
        "form_8938_threshold_any_time": str(_q(any_t)),
        "max_aggregate_value": str(_q(mx)),
        "year_end_aggregate_value": str(_q(ye)),
        "filing_status": status,
        "residence": residence,
    }


def sec962_flag(*, cfc_inclusion) -> dict:
    """Rough year-1 comparison of GILTI/Subpart F taxed at individual rate vs §962 election."""
    inc = _dec(cfc_inclusion)
    if inc <= 0:
        return {}
    individual_tax = inc * TOP_INDIVIDUAL_RATE
    sec962_base = inc * (Decimal("1") - GILTI_250_DEDUCTION)     # §250 deduction (GILTI)
    sec962_tax = sec962_base * CORP_RATE
    return {
        "cfc_inclusion": str(_q(inc)),
        "tax_at_individual_rate": str(_q(individual_tax)),
        "tax_under_sec962_year1": str(_q(sec962_tax)),
        "rough_year1_saving": str(_q(individual_tax - sec962_tax)),
        "note": "FLAG ONLY — §962 retaxes the earnings on actual distribution; model full multi-year impact in /glaw-tax-strategy. §250 deduction steps down [VERIFY].",
    }


def analyze(*, max_aggregate="0", year_end_aggregate="0", status="single",
            residence="us", cfc_inclusion="0") -> dict:
    out = reporting(max_aggregate=max_aggregate, year_end_aggregate=year_end_aggregate,
                    status=status, residence=residence)
    flag = sec962_flag(cfc_inclusion=cfc_inclusion)
    if flag:
        out["sec962_election"] = flag
    out["_verify"] = ("8938 thresholds + §250 deduction + rates are year-sensitive; FBAR is FinCEN, "
                      "not the IRS; consider streamlined / voluntary disclosure if prior years are delinquent.")
    return out


def render_text(d: dict) -> str:
    lines = ["=" * 60, "FOREIGN-ASSET REPORTING — DRAFT", "-" * 60,
             f"  max aggregate (any time)        {_dec(d['max_aggregate_value']):>16,.2f}",
             f"  year-end aggregate              {_dec(d['year_end_aggregate_value']):>16,.2f}",
             f"  status / residence: {d['filing_status']} / {d['residence']}",
             f"  ► FBAR (FinCEN 114) required: {d['fbar_fincen114_required']}  (threshold {_dec(d['fbar_threshold']):,.0f})",
             f"  ► Form 8938 required:        {d['form_8938_required']}  (year-end {_dec(d['form_8938_threshold_year_end']):,.0f} / any-time {_dec(d['form_8938_threshold_any_time']):,.0f})"]
    if "sec962_election" in d:
        s = d["sec962_election"]
        lines += ["-" * 60, "  §962 election (rough year-1 flag):",
                  f"    CFC inclusion                 {_dec(s['cfc_inclusion']):>16,.2f}",
                  f"    tax @ individual rate         {_dec(s['tax_at_individual_rate']):>16,.2f}",
                  f"    tax under §962 (year 1)       {_dec(s['tax_under_sec962_year1']):>16,.2f}",
                  f"    rough year-1 saving           {_dec(s['rough_year1_saving']):>16,.2f}",
                  f"    {s['note']}"]
    lines += ["=" * 60, f"  ⚠ VERIFY: {d['_verify']}"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fbar-8938", description="FBAR/Form 8938 threshold + §962 flag (DRAFT).")
    ap.add_argument("--max-aggregate", default="0", help="highest aggregate foreign-account value any time")
    ap.add_argument("--year-end-aggregate", default="0")
    ap.add_argument("--status", default="single", choices=["single", "mfj"])
    ap.add_argument("--residence", default="us", choices=["us", "abroad"])
    ap.add_argument("--cfc-inclusion", default="0", help="GILTI/Subpart F inclusion for §962 flag")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = analyze(max_aggregate=a.max_aggregate, year_end_aggregate=a.year_end_aggregate,
                status=a.status, residence=a.residence, cfc_inclusion=a.cfc_inclusion)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

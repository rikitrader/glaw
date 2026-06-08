#!/usr/bin/env python3
"""GLAW corporate penalty taxes — accumulated earnings tax (§531) and personal holding company
tax (§541). Both are 20% penalty taxes on a C-corp that retains earnings rather than distributing.

Accumulated earnings tax (§531-537): 20% of accumulated taxable income retained beyond the
reasonable needs of the business, after the accumulated-earnings credit (the greater of the
reasonable needs minus prior accumulations, or the $250,000 minimum — $150,000 for a personal
service corporation).
Personal holding company tax (§541-547): 20% of undistributed personal holding company income for
a corporation that is closely held and has predominantly passive income.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def accumulated_earnings_tax(accumulated_taxable_income, *, reasonable_needs="0",
                             prior_accumulated_e_and_p="0", is_psc=False, rate="20") -> dict:
    ati = _dec(accumulated_taxable_income)
    minimum_credit = Decimal("150000") if is_psc else Decimal("250000")
    needs_credit = max(Decimal("0"), _dec(reasonable_needs) - _dec(prior_accumulated_e_and_p))
    credit = max(minimum_credit, needs_credit)
    taxable = max(Decimal("0"), ati - credit)
    tax = _q(taxable * _dec(rate) / Decimal("100"))
    return {"accumulated_taxable_income": str(_q(ati)), "accumulated_earnings_credit": str(_q(credit)),
            "subject_to_tax": str(_q(taxable)), "accumulated_earnings_tax": str(tax)}


def phc_tax(undistributed_phc_income, *, rate="20") -> dict:
    upi = max(Decimal("0"), _dec(undistributed_phc_income))
    return {"undistributed_phc_income": str(_q(upi)),
            "personal_holding_company_tax": str(_q(upi * _dec(rate) / Decimal("100")))}


def render_text(d: dict) -> str:
    o = ["=" * 56, "CORPORATE PENALTY TAXES", "-" * 56]
    if "accumulated_earnings_tax" in d:
        o += [f"  accumulated taxable income {_dec(d['accumulated_taxable_income']):>14,.2f}",
              f"  accumulated-earnings credit {_dec(d['accumulated_earnings_credit']):>13,.2f}",
              f"  ACCUMULATED EARNINGS TAX   {_dec(d['accumulated_earnings_tax']):>14,.2f}"]
    if "personal_holding_company_tax" in d:
        o += [f"  PHC TAX                    {_dec(d['personal_holding_company_tax']):>14,.2f}"]
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-penalty-taxes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("aet"); a.add_argument("--ati", required=True); a.add_argument("--reasonable-needs", default="0")
    a.add_argument("--prior-aep", default="0"); a.add_argument("--psc", action="store_true")
    p = sub.add_parser("phc"); p.add_argument("--undistributed-phc-income", required=True)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args()
    if args.cmd == "aet":
        d = accumulated_earnings_tax(args.ati, reasonable_needs=args.reasonable_needs,
                                     prior_accumulated_e_and_p=args.prior_aep, is_psc=args.psc)
    else:
        d = phc_tax(args.undistributed_phc_income)
    print(json.dumps(d, indent=2, default=str) if args.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

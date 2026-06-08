#!/usr/bin/env python3
"""GLAW Trust Fund Recovery Penalty engine (IRC §6672) — when a business fails to remit withheld
employment taxes, the IRS can assess the TRUST-FUND portion (the employee income tax withheld plus
the employee share of FICA) at 100 % personally against any person who is both RESPONSIBLE (had
the duty and authority to collect/pay over the tax) and WILLFUL (knew of the obligation and paid
other creditors instead). The employer's matching FICA share is NOT a trust-fund amount.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
RESPONSIBLE_FACTORS = {
    "check_signing_authority": 25, "hires_fires_employees": 20, "controls_payroll": 25,
    "signs_tax_returns": 15, "controls_disbursements": 25, "officer_or_director": 10,
}
WILLFUL_FACTORS = {
    "knew_taxes_unpaid": 35, "paid_other_creditors_instead": 35,
    "reckless_disregard": 20, "continued_after_notice": 25,
}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def trust_fund_amount(withheld_income_tax, employee_fica) -> Decimal:
    return _q(_dec(withheld_income_tax) + _dec(employee_fica))


def tfrp(*, withheld_income_tax, employee_fica, responsible_factors=None,
         willful_factors=None) -> dict:
    tf = trust_fund_amount(withheld_income_tax, employee_fica)
    resp_score = min(100, sum(RESPONSIBLE_FACTORS.get(f, 0) for f in (responsible_factors or [])))
    will_score = min(100, sum(WILLFUL_FACTORS.get(f, 0) for f in (willful_factors or [])))
    responsible = resp_score >= 50
    willful = will_score >= 50
    liable = responsible and willful
    return {"trust_fund_amount": str(tf),
            "withheld_income_tax": str(_q(_dec(withheld_income_tax))),
            "employee_fica": str(_q(_dec(employee_fica))),
            "responsible_score": resp_score, "responsible": responsible,
            "willful_score": will_score, "willful": willful,
            "personally_liable": liable,
            "tfrp_exposure": str(tf if liable else Decimal("0.00")),
            "note": "TFRP is the trust-fund portion only (withheld income tax + employee FICA); "
                    "the employer FICA match is not recoverable under §6672"}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "TRUST FUND RECOVERY PENALTY (IRC §6672)", "-" * 56,
        f"  trust-fund amount        {_dec(d['trust_fund_amount']):>16,.2f}",
        f"  responsible: {d['responsible']} (score {d['responsible_score']})",
        f"  willful: {d['willful']} (score {d['willful_score']})",
        "-" * 56,
        f"  PERSONALLY LIABLE: {d['personally_liable']}",
        f"  TFRP exposure            {_dec(d['tfrp_exposure']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-tfrp")
    ap.add_argument("--withheld-income-tax", required=True)
    ap.add_argument("--employee-fica", required=True)
    ap.add_argument("--responsible-factors", default=None, help="comma-separated")
    ap.add_argument("--willful-factors", default=None, help="comma-separated")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = tfrp(withheld_income_tax=a.withheld_income_tax, employee_fica=a.employee_fica,
             responsible_factors=(a.responsible_factors.split(",") if a.responsible_factors else []),
             willful_factors=(a.willful_factors.split(",") if a.willful_factors else []))
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GLAW Form 1040 + Schedule SE — assemble an individual return from a Schedule C net profit (and
wages / other income), with the self-employment tax.

Schedule SE: net SE earnings = net Schedule C × 92.35 %; SE tax = 12.4 % (Social Security, up to
the wage base less any W-2 SS wages) + 2.9 % (Medicare, no cap); one-half of the SE tax is an
above-the-line deduction. 1040: total income → AGI (less ½ SE tax) → taxable income (less the
standard deduction and the QBI deduction) → income tax via the brackets → total tax (income tax
+ SE tax − credits) → balance due / refund after withholding and payments.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
SS_WAGE_BASE = {2024: Decimal("168600"), 2025: Decimal("176100")}
STD_DEDUCTION = {2024: {"single": Decimal("14600"), "mfj": Decimal("29200")},
                 2025: {"single": Decimal("15000"), "mfj": Decimal("30000")}}
# 2024 ordinary-income brackets: list of (upper_bound, rate); last bound = infinity
BRACKETS = {
    2024: {
        "single": [(11600, "0.10"), (47150, "0.12"), (100525, "0.22"), (191950, "0.24"),
                   (243725, "0.32"), (609350, "0.35"), (None, "0.37")],
        "mfj": [(23200, "0.10"), (94300, "0.12"), (201050, "0.22"), (383900, "0.24"),
                (487450, "0.32"), (731200, "0.35"), (None, "0.37")],
    }
}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def schedule_se(net_sch_c, *, w2_ss_wages="0", year: int = 2024) -> dict:
    net = _dec(net_sch_c)
    if net <= 0:
        return {"net_se_earnings": "0.00", "ss_portion": "0.00", "medicare_portion": "0.00",
                "se_tax": "0.00", "half_se_deduction": "0.00"}
    net_se = net * Decimal("0.9235")
    ss_base = SS_WAGE_BASE.get(year, SS_WAGE_BASE[2024])
    ss_room = max(Decimal("0"), ss_base - _dec(w2_ss_wages))
    ss_portion = _q(min(net_se, ss_room) * Decimal("0.124"))
    medicare_portion = _q(net_se * Decimal("0.029"))
    se_tax = _q(ss_portion + medicare_portion)
    return {"net_se_earnings": str(_q(net_se)), "ss_portion": str(ss_portion),
            "medicare_portion": str(medicare_portion), "se_tax": str(se_tax),
            "half_se_deduction": str(_q(se_tax / 2))}


def income_tax(taxable_income, filing_status: str = "single", year: int = 2024) -> Decimal:
    ti = max(Decimal("0"), _dec(taxable_income))
    brk = BRACKETS.get(year, BRACKETS[2024])[filing_status]
    tax, lower = Decimal("0"), Decimal("0")
    for upper, rate in brk:
        cap = _dec(upper) if upper is not None else ti
        slice_amt = min(ti, cap) - lower
        if slice_amt > 0:
            tax += slice_amt * _dec(rate)
        lower = cap
        if upper is None or ti <= cap:
            break
    return _q(tax)


def form_1040(*, sch_c_net="0", wages="0", w2_ss_wages="0", other_income="0",
              filing_status="single", qbi_deduction="0", withholding="0", payments="0",
              credits="0", year: int = 2024) -> dict:
    se = schedule_se(sch_c_net, w2_ss_wages=w2_ss_wages, year=year)
    total_income = _q(_dec(wages) + _dec(sch_c_net) + _dec(other_income))
    agi = _q(total_income - _dec(se["half_se_deduction"]))
    std = STD_DEDUCTION.get(year, STD_DEDUCTION[2024])[filing_status]
    taxable_income = _q(max(Decimal("0"), agi - std - _dec(qbi_deduction)))
    inc_tax = income_tax(taxable_income, filing_status, year)
    total_tax = _q(inc_tax + _dec(se["se_tax"]) - _dec(credits))
    paid = _dec(withholding) + _dec(payments)
    balance = _q(total_tax - paid)
    return {"filing_status": filing_status, "year": year, "schedule_se": se,
            "total_income": str(total_income), "agi": str(agi),
            "standard_deduction": str(_q(std)), "qbi_deduction": str(_q(_dec(qbi_deduction))),
            "taxable_income": str(taxable_income), "income_tax": str(inc_tax),
            "se_tax": se["se_tax"], "total_tax": str(total_tax),
            "payments": str(_q(paid)),
            "balance_due": str(balance) if balance > 0 else "0.00",
            "refund": str(_q(-balance)) if balance < 0 else "0.00"}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, f"FORM 1040 ({d['filing_status']}, {d['year']})", "-" * 56,
        f"  total income            {_dec(d['total_income']):>16,.2f}",
        f"  AGI (less ½ SE tax)     {_dec(d['agi']):>16,.2f}",
        f"  standard deduction      {_dec(d['standard_deduction']):>16,.2f}",
        f"  QBI deduction           {_dec(d['qbi_deduction']):>16,.2f}",
        f"  taxable income          {_dec(d['taxable_income']):>16,.2f}",
        "-" * 56,
        f"  income tax              {_dec(d['income_tax']):>16,.2f}",
        f"  self-employment tax     {_dec(d['se_tax']):>16,.2f}",
        f"  total tax               {_dec(d['total_tax']):>16,.2f}",
        f"  payments                {_dec(d['payments']):>16,.2f}",
        f"  BALANCE DUE             {_dec(d['balance_due']):>16,.2f}" if _dec(d['balance_due']) > 0
        else f"  REFUND                  {_dec(d['refund']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-form1040")
    ap.add_argument("--sch-c-net", default="0"); ap.add_argument("--wages", default="0")
    ap.add_argument("--w2-ss-wages", default="0"); ap.add_argument("--other-income", default="0")
    ap.add_argument("--filing-status", default="single", choices=["single", "mfj"])
    ap.add_argument("--qbi-deduction", default="0"); ap.add_argument("--withholding", default="0")
    ap.add_argument("--payments", default="0"); ap.add_argument("--credits", default="0")
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = form_1040(sch_c_net=a.sch_c_net, wages=a.wages, w2_ss_wages=a.w2_ss_wages,
                  other_income=a.other_income, filing_status=a.filing_status,
                  qbi_deduction=a.qbi_deduction, withholding=a.withholding, payments=a.payments,
                  credits=a.credits, year=a.year)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

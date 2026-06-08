#!/usr/bin/env python3
"""GLAW S-corporation shareholder basis (Form 7203) — stock + debt basis rollforward with the
loss-limitation ordering. Losses and deductions are allowed only to the extent of stock + debt
basis; the excess is suspended and carried forward.

Ordering (Treas. Reg. §1.1367-1): (1) increase stock basis for capital contributions and income
items; (2) decrease for distributions (not below zero — excess is capital gain); (3) decrease for
nondeductible expenses; (4) decrease for loss/deduction items, limited to remaining stock then
debt basis, with the excess suspended (§1366(d)).
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


def basis(*, beginning_stock="0", beginning_debt="0", contributions="0", income="0",
          tax_exempt_income="0", distributions="0", nondeductible="0", loss="0") -> dict:
    stock = _dec(beginning_stock)
    debt = _dec(beginning_debt)
    # 1) income increases stock basis
    stock += _dec(contributions) + _dec(income) + _dec(tax_exempt_income)
    # 2) distributions reduce stock (excess over basis = capital gain)
    dist = _dec(distributions)
    excess_dist = max(Decimal("0"), dist - stock)
    stock = max(Decimal("0"), stock - dist)
    # 3) nondeductible expenses
    nd = _dec(nondeductible)
    stock = max(Decimal("0"), stock - nd)
    # 4) losses limited to stock + debt; excess suspended
    ls = _dec(loss)
    allowed = min(ls, stock + debt)
    from_stock = min(allowed, stock)
    from_debt = allowed - from_stock
    stock -= from_stock
    debt -= from_debt
    suspended = _q(ls - allowed)
    return {"ending_stock_basis": str(_q(stock)), "ending_debt_basis": str(_q(debt)),
            "loss_allowed": str(_q(allowed)), "loss_suspended": str(suspended),
            "excess_distribution_capital_gain": str(_q(excess_dist))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "S-CORP SHAREHOLDER BASIS (Form 7203)", "-" * 56,
        f"  ending stock basis      {_dec(d['ending_stock_basis']):>16,.2f}",
        f"  ending debt basis       {_dec(d['ending_debt_basis']):>16,.2f}",
        f"  loss allowed            {_dec(d['loss_allowed']):>16,.2f}",
        f"  loss suspended (c/f)    {_dec(d['loss_suspended']):>16,.2f}",
        f"  excess distribution (cap gain) {_dec(d['excess_distribution_capital_gain']):>9,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-scorp-basis")
    for f in ("beginning-stock", "beginning-debt", "contributions", "income", "tax-exempt-income",
              "distributions", "nondeductible", "loss"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = basis(beginning_stock=a.beginning_stock, beginning_debt=a.beginning_debt,
              contributions=a.contributions, income=a.income, tax_exempt_income=a.tax_exempt_income,
              distributions=a.distributions, nondeductible=a.nondeductible, loss=a.loss)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

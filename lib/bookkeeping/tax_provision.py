#!/usr/bin/env python3
"""GLAW income tax provision (ASC 740) — current + deferred, with ETR reconciliation.

  taxable income   = pretax book income + permanent differences ± temporary differences
  current tax      = taxable income × rate
  deferred tax     = (− temporary differences) × rate   (a book>tax temp diff now → DTL)
  total provision  = current + deferred = (pretax + permanent) × rate
  effective rate   = total provision ÷ pretax book income

Permanent differences (e.g. fines, 50% meals) never reverse; temporary differences
(e.g. MACRS vs book depreciation) reverse and create deferred tax. Sign convention here:
a positive temporary difference = tax deduction taken NOW in excess of book (book income
> taxable income now), which creates a deferred tax LIABILITY.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def provision(pretax_book: Decimal, permanent: Decimal, temporary: Decimal,
              rate_pct: Decimal) -> dict:
    rate = rate_pct / Decimal("100")
    taxable_income = pretax_book + permanent - temporary
    current = _q(taxable_income * rate)
    deferred = _q(temporary * rate)                 # +temp diff now → deferred tax liability (expense now)
    total = _q(current + deferred)
    etr = (total / pretax_book * 100) if pretax_book else Decimal("0")
    statutory = _q(pretax_book * rate)
    perm_effect = _q(permanent * rate)
    # ETR reconciliation: statutory + tax effect of permanent diffs = total provision
    lines = [{"account": "Expenses:Income Tax", "debit": str(total), "credit": "0"},
             {"account": "Liabilities:Income Tax Payable", "debit": "0", "credit": str(current)}]
    if deferred > 0:
        lines.append({"account": "Liabilities:Deferred Tax", "debit": "0", "credit": str(deferred)})
    elif deferred < 0:
        lines.append({"account": "Assets:Deferred Tax", "debit": str(-deferred), "credit": "0"})
    return {"pretax_book": _q(pretax_book), "permanent_diff": _q(permanent),
            "temporary_diff": _q(temporary), "taxable_income": _q(taxable_income),
            "statutory_rate_pct": rate_pct, "statutory_tax": statutory,
            "permanent_tax_effect": perm_effect,
            "current_tax": current, "deferred_tax": deferred, "total_provision": total,
            "effective_rate_pct": _q(etr),
            "deferred_tax_type": "liability" if deferred > 0 else ("asset" if deferred < 0 else "none"),
            "entry": lines}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "INCOME TAX PROVISION (ASC 740)", "-" * 56,
        f"  pretax book income     {d['pretax_book']:>16,.2f}",
        f"  + permanent diffs      {d['permanent_diff']:>16,.2f}",
        f"  − temporary diffs      {d['temporary_diff']:>16,.2f}",
        f"  = taxable income       {d['taxable_income']:>16,.2f}",
        "-" * 56,
        f"  current tax (@{d['statutory_rate_pct']}%)    {d['current_tax']:>16,.2f}",
        f"  deferred tax ({d['deferred_tax_type']})  {d['deferred_tax']:>16,.2f}",
        f"  total provision        {d['total_provision']:>16,.2f}",
        "-" * 56,
        "  ETR reconciliation:",
        f"    statutory tax        {d['statutory_tax']:>16,.2f}",
        f"    permanent tax effect {d['permanent_tax_effect']:>16,.2f}",
        f"    effective rate       {d['effective_rate_pct']:>15,.2f}%",
        "=" * 56,
    ])


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-tax-provision")
    ap.add_argument("--pretax", required=True, help="pretax book income")
    ap.add_argument("--permanent", default="0", help="permanent differences (net)")
    ap.add_argument("--temporary", default="0", help="temporary differences (net; +ve → DTL)")
    ap.add_argument("--rate", required=True, help="statutory tax rate %%")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = provision(Decimal(a.pretax), Decimal(a.permanent), Decimal(a.temporary), Decimal(a.rate))
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

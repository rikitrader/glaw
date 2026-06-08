#!/usr/bin/env python3
"""GLAW Subpart F income (§951-952) — a U.S. shareholder of a CFC includes its pro-rata share of
Subpart F income (foreign personal holding company income — dividends, interest, rents, royalties,
gains — plus foreign base company sales/services income) currently, even if not distributed.

Gates:
- De minimis (§954(b)(3)(A)): if gross Subpart F income < the LESSER of 5% of gross income or
  $1,000,000, none is Subpart F income.
- Full inclusion (§954(b)(3)(B)): if it exceeds 70% of gross income, ALL gross income is Subpart F.
- E&P limit (§952(c)): the inclusion cannot exceed the CFC's current E&P.
- High-tax exception (§954(b)(4)): excluded if taxed abroad above 90% of the U.S. rate (18.9%).
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


def subpart_f(*, gross_subpart_f, total_gross_income, current_e_and_p,
              foreign_effective_rate_pct="0", us_rate_pct="21", shareholder_pct="100") -> dict:
    gsf = _dec(gross_subpart_f)
    gi = _dec(total_gross_income)
    de_minimis_threshold = min(gi * Decimal("0.05"), Decimal("1000000"))
    high_tax = _dec(foreign_effective_rate_pct) > _dec(us_rate_pct) * Decimal("0.90")
    if high_tax:
        amount, basis = Decimal("0"), "excluded — high-tax exception (>90% of U.S. rate)"
    elif gsf < de_minimis_threshold:
        amount, basis = Decimal("0"), "excluded — de minimis (< lesser of 5% GI or $1M)"
    elif gi > 0 and gsf > gi * Decimal("0.70"):
        amount, basis = gi, "FULL INCLUSION — Subpart F > 70% of gross income"
    else:
        amount, basis = gsf, "Subpart F income included"
    amount = min(amount, max(Decimal("0"), _dec(current_e_and_p)))      # §952(c) E&P limit
    shareholder = amount * _dec(shareholder_pct) / Decimal("100")
    return {"de_minimis_threshold": str(_q(de_minimis_threshold)), "basis": basis,
            "subpart_f_income": str(_q(amount)),
            "shareholder_inclusion": str(_q(shareholder))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "SUBPART F INCOME (§951-952)", "-" * 56,
        f"  basis: {d['basis']}",
        f"  Subpart F income         {_dec(d['subpart_f_income']):>16,.2f}",
        f"  SHAREHOLDER INCLUSION    {_dec(d['shareholder_inclusion']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-subpart-f")
    ap.add_argument("--gross-subpart-f", required=True); ap.add_argument("--total-gross-income", required=True)
    ap.add_argument("--current-e-and-p", required=True); ap.add_argument("--foreign-effective-rate-pct", default="0")
    ap.add_argument("--shareholder-pct", default="100")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = subpart_f(gross_subpart_f=a.gross_subpart_f, total_gross_income=a.total_gross_income,
                  current_e_and_p=a.current_e_and_p, foreign_effective_rate_pct=a.foreign_effective_rate_pct,
                  shareholder_pct=a.shareholder_pct)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

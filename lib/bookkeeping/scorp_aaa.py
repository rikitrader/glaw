#!/usr/bin/env python3
"""GLAW S-corporation Accumulated Adjustments Account (AAA) rollforward + distribution ordering.

AAA tracks the cumulative post-1982 income that has already been taxed to the shareholders and can
be distributed tax-free. Rollforward: AAA + separately/non-separately stated income − deductions
and losses − non-dividend distributions (AAA is not reduced below zero by distributions). A
distribution is sourced (§1368): (1) from AAA — tax-free to the extent of stock basis; (2) from
accumulated earnings & profits (AE&P) — a taxable dividend; (3) remaining — return of capital to
basis; (4) excess over basis — capital gain.
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


def aaa_rollforward(*, beginning_aaa="0", income="0", loss="0", distributions="0",
                    accumulated_e_and_p="0", stock_basis="0") -> dict:
    aaa = _dec(beginning_aaa) + _dec(income) - _dec(loss)
    dist = _dec(distributions)
    basis = _dec(stock_basis)
    aep = _dec(accumulated_e_and_p)

    from_aaa = min(dist, max(Decimal("0"), aaa))
    rem = dist - from_aaa
    from_aep_dividend = min(rem, aep)
    rem -= from_aep_dividend
    from_basis = min(rem, max(Decimal("0"), basis - from_aaa))
    capital_gain = rem - from_basis

    ending_aaa = aaa - from_aaa                       # AAA not reduced below 0 by distributions
    return {"ending_aaa": str(_q(ending_aaa)),
            "distribution_from_aaa_taxfree": str(_q(from_aaa)),
            "distribution_dividend_from_aep": str(_q(from_aep_dividend)),
            "distribution_return_of_capital": str(_q(from_basis)),
            "distribution_capital_gain": str(_q(capital_gain))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "S-CORP AAA + DISTRIBUTION ORDERING (§1368)", "-" * 56,
        f"  ending AAA               {_dec(d['ending_aaa']):>16,.2f}",
        f"  tax-free from AAA        {_dec(d['distribution_from_aaa_taxfree']):>16,.2f}",
        f"  taxable dividend (AE&P)  {_dec(d['distribution_dividend_from_aep']):>16,.2f}",
        f"  return of capital        {_dec(d['distribution_return_of_capital']):>16,.2f}",
        f"  capital gain             {_dec(d['distribution_capital_gain']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-scorp-aaa")
    for f in ("beginning-aaa", "income", "loss", "distributions", "accumulated-e-and-p", "stock-basis"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = aaa_rollforward(beginning_aaa=a.beginning_aaa, income=a.income, loss=a.loss,
                        distributions=a.distributions, accumulated_e_and_p=a.accumulated_e_and_p,
                        stock_basis=a.stock_basis)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

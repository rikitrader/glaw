#!/usr/bin/env python3
"""GLAW partner outside-basis rollforward (§705) + §704(d) loss limitation.

Outside basis = beginning basis + capital contributions + share of income (taxable + tax-exempt)
+ increase in the partner's share of partnership liabilities − distributions − decrease in
liability share − share of losses and nondeductible expenses. Losses are deductible only to the
extent of outside basis (§704(d)); the excess is suspended and carried forward.
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


def outside_basis(*, beginning_basis="0", contributions="0", income="0", tax_exempt_income="0",
                  liability_increase="0", distributions="0", liability_decrease="0",
                  nondeductible="0", loss="0") -> dict:
    b = _dec(beginning_basis) + _dec(contributions) + _dec(income) + _dec(tax_exempt_income) + _dec(liability_increase)
    dist = _dec(distributions) + _dec(liability_decrease)
    excess_dist = max(Decimal("0"), dist - b)
    b = max(Decimal("0"), b - dist)
    b = max(Decimal("0"), b - _dec(nondeductible))
    ls = _dec(loss)
    allowed = min(ls, b)
    b -= allowed
    return {"ending_basis": str(_q(b)), "loss_allowed": str(_q(allowed)),
            "loss_suspended": str(_q(ls - allowed)),
            "excess_distribution_gain": str(_q(excess_dist))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "PARTNER OUTSIDE BASIS (§705 / §704(d))", "-" * 56,
        f"  ending outside basis    {_dec(d['ending_basis']):>16,.2f}",
        f"  loss allowed            {_dec(d['loss_allowed']):>16,.2f}",
        f"  loss suspended (c/f)    {_dec(d['loss_suspended']):>16,.2f}",
        f"  excess distribution gain{_dec(d['excess_distribution_gain']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-partner-basis")
    for f in ("beginning-basis", "contributions", "income", "tax-exempt-income", "liability-increase",
              "distributions", "liability-decrease", "nondeductible", "loss"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = outside_basis(beginning_basis=a.beginning_basis, contributions=a.contributions, income=a.income,
                      tax_exempt_income=a.tax_exempt_income, liability_increase=a.liability_increase,
                      distributions=a.distributions, liability_decrease=a.liability_decrease,
                      nondeductible=a.nondeductible, loss=a.loss)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

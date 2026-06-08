#!/usr/bin/env python3
"""GLAW §163(j) business interest limitation — a business's deduction for net business interest is
capped at 30% of Adjusted Taxable Income (ATI) plus business interest income plus floor-plan
financing interest. Disallowed interest carries forward indefinitely.

  Allowed = business interest income + 30% × ATI + floor-plan interest
  Deductible business interest expense = min(business interest expense, allowed)
  Disallowed (carryforward) = business interest expense − deductible
Small-business exception: a taxpayer under the §448(c) gross-receipts threshold (~$30M, 3-yr avg)
is exempt — supply exempt=True. (ATI no longer adds back depreciation/amortization post-2021.)
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


def sec163j(*, business_interest_expense, ati, business_interest_income="0", floor_plan_interest="0",
            limit_pct="30", exempt=False) -> dict:
    bie = _dec(business_interest_expense)
    if exempt:
        return {"exempt": True, "allowed_limit": str(_q(bie)), "deductible_interest": str(_q(bie)),
                "disallowed_carryforward": "0.00"}
    allowed = (_dec(business_interest_income) + _dec(ati) * _dec(limit_pct) / Decimal("100")
               + _dec(floor_plan_interest))
    deductible = min(bie, allowed)
    disallowed = max(Decimal("0"), bie - deductible)
    return {"exempt": False, "allowed_limit": str(_q(allowed)),
            "deductible_interest": str(_q(deductible)),
            "disallowed_carryforward": str(_q(disallowed))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "§163(j) BUSINESS INTEREST LIMITATION", "-" * 56,
        f"  allowed limit (30% ATI+) {_dec(d['allowed_limit']):>16,.2f}",
        f"  deductible interest      {_dec(d['deductible_interest']):>16,.2f}",
        f"  disallowed (c/f)         {_dec(d['disallowed_carryforward']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-sec163j")
    ap.add_argument("--business-interest-expense", required=True); ap.add_argument("--ati", required=True)
    ap.add_argument("--business-interest-income", default="0"); ap.add_argument("--floor-plan-interest", default="0")
    ap.add_argument("--exempt", action="store_true")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = sec163j(business_interest_expense=a.business_interest_expense, ati=a.ati,
                business_interest_income=a.business_interest_income, floor_plan_interest=a.floor_plan_interest,
                exempt=a.exempt)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

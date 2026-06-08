#!/usr/bin/env python3
"""GLAW state franchise / margin / minimum tax — the non-income-based entity taxes:

- Delaware franchise tax (C-corp): the LESSER of the Authorized Shares Method and the Assumed Par
  Value Capital Method; floor $175, and a $400/M cap is NOT applied here (large-corp cap $200k+).
- Texas franchise (margin) tax: taxable margin = total revenue − the GREATEST of (COGS,
  compensation, 30% of revenue, or revenue − $1M); margin × apportionment × rate (0.375% for
  retail/wholesale, 0.75% otherwise). No tax due if revenue ≤ the no-tax-due threshold or tax < $1,000.
- California minimum franchise tax: $800 flat minimum.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
TX_NO_TAX_THRESHOLD = Decimal("2470000")     # 2024-2025 no-tax-due revenue threshold [VERIFY annually]


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def delaware_franchise(*, authorized_shares, issued_shares, total_gross_assets) -> dict:
    # Authorized Shares Method (tiered): <=5000 -> $175; <=10000 -> $250; +$85 per additional 10k
    sh = int(_dec(authorized_shares))
    if sh <= 5000:
        asm = Decimal("175")
    elif sh <= 10000:
        asm = Decimal("250")
    else:
        asm = Decimal("250") + Decimal((sh - 10000 + 9999) // 10000) * Decimal("85")
    # Assumed Par Value Capital Method: assumed par = gross assets / issued shares; capital = par × authorized;
    # tax = $400 per $1,000,000 of assumed par value capital, min $400
    issued = max(Decimal("1"), _dec(issued_shares))
    assumed_par = _dec(total_gross_assets) / issued
    apvc = assumed_par * _dec(authorized_shares)
    apvm = max(Decimal("400"), (apvc / Decimal("1000000")) * Decimal("400"))
    tax = max(Decimal("175"), min(asm, _q(apvm)))
    return {"method": "delaware_franchise", "authorized_shares_method": str(_q(asm)),
            "assumed_par_value_method": str(_q(apvm)), "franchise_tax": str(_q(tax))}


def texas_margin(*, total_revenue, cogs="0", compensation="0", apportionment_pct="100",
                 retail_wholesale=False) -> dict:
    rev = _dec(total_revenue)
    if rev <= TX_NO_TAX_THRESHOLD:
        return {"method": "texas_margin", "taxable_margin": "0.00", "franchise_tax": "0.00",
                "note": f"revenue <= no-tax-due threshold {TX_NO_TAX_THRESHOLD:,}"}
    deduction = max(_dec(cogs), _dec(compensation), rev * Decimal("0.30"), rev - Decimal("1000000"))
    margin = max(Decimal("0"), rev - deduction)
    apportioned = margin * _dec(apportionment_pct) / Decimal("100")
    rate = Decimal("0.00375") if retail_wholesale else Decimal("0.0075")
    tax = apportioned * rate
    if tax < Decimal("1000"):
        tax = Decimal("0")                          # < $1,000 -> no tax due
    return {"method": "texas_margin", "taxable_margin": str(_q(margin)),
            "apportioned_margin": str(_q(apportioned)), "franchise_tax": str(_q(tax))}


def california_minimum() -> dict:
    return {"method": "california_minimum", "franchise_tax": "800.00"}


def render_text(d: dict) -> str:
    return "\n".join(["=" * 56, f"FRANCHISE TAX — {d['method']}", "-" * 56,
                      f"  FRANCHISE TAX            {_dec(d['franchise_tax']):>16,.2f}", "=" * 56])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-franchise-tax")
    sub = ap.add_subparsers(dest="cmd", required=True)
    de = sub.add_parser("de"); de.add_argument("--authorized-shares", required=True)
    de.add_argument("--issued-shares", required=True); de.add_argument("--total-gross-assets", required=True)
    tx = sub.add_parser("tx"); tx.add_argument("--total-revenue", required=True)
    tx.add_argument("--cogs", default="0"); tx.add_argument("--compensation", default="0")
    tx.add_argument("--apportionment-pct", default="100"); tx.add_argument("--retail-wholesale", action="store_true")
    sub.add_parser("ca")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.cmd == "de":
        d = delaware_franchise(authorized_shares=a.authorized_shares, issued_shares=a.issued_shares,
                               total_gross_assets=a.total_gross_assets)
    elif a.cmd == "tx":
        d = texas_margin(total_revenue=a.total_revenue, cogs=a.cogs, compensation=a.compensation,
                         apportionment_pct=a.apportionment_pct, retail_wholesale=a.retail_wholesale)
    else:
        d = california_minimum()
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

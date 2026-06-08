#!/usr/bin/env python3
"""GLAW combined / unitary state return — a unitary group files one combined return: pool the
members' business income, then apportion to the state with the COMBINED apportionment factors
(the Finnigan or Joyce rule governs whether a member with no nexus still counts in the numerator;
this uses the combined-denominator approach and a single combined sales factor).

Combined income = Σ member business income. Combined sales factor = (Σ in-state sales) / (Σ everywhere
sales). State tax = combined income × combined factor × rate. (Single-sales-factor states only need
the sales factor; supply payroll/property only if the state uses a 3-factor formula.)
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")
_PCT = Decimal("0.0001")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _qp(d): return Decimal(str(d)).quantize(_PCT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def combined(members: list, *, rate_pct, factor="sales") -> dict:
    income = sum((_dec(m.get("income", 0)) for m in members), Decimal("0"))
    in_state = sum((_dec(m.get("in_state_sales", 0)) for m in members), Decimal("0"))
    everywhere = sum((_dec(m.get("everywhere_sales", 0)) for m in members), Decimal("0"))
    if factor == "sales":
        app = (in_state / everywhere) if everywhere else Decimal("0")
    else:                                            # equal-weighted 3-factor
        def f(k_in, k_all):
            i = sum((_dec(m.get(k_in, 0)) for m in members), Decimal("0"))
            a = sum((_dec(m.get(k_all, 0)) for m in members), Decimal("0"))
            return (i / a) if a else Decimal("0")
        app = (f("in_state_sales", "everywhere_sales") + f("in_state_payroll", "everywhere_payroll")
               + f("in_state_property", "everywhere_property")) / Decimal("3")
    apportioned = income * app
    tax = apportioned * _dec(rate_pct) / Decimal("100")
    return {"members": len(members), "combined_income": str(_q(income)),
            "combined_apportionment_pct": str(_qp(app * 100)),
            "apportioned_income": str(_q(apportioned)), "state_tax": str(_q(tax))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, f"COMBINED / UNITARY RETURN ({d['members']} members)", "-" * 56,
        f"  combined income          {_dec(d['combined_income']):>16,.2f}",
        f"  combined apportionment    {_dec(d['combined_apportionment_pct']):>14}%",
        f"  apportioned income       {_dec(d['apportioned_income']):>16,.2f}",
        f"  STATE TAX                {_dec(d['state_tax']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-combined-unitary")
    ap.add_argument("members", help="JSON file/'-': [{income, in_state_sales, everywhere_sales, ...}]")
    ap.add_argument("--rate-pct", required=True)
    ap.add_argument("--factor", default="sales", choices=["sales", "three"])
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.members == "-" else Path(a.members).read_text(encoding="utf-8")
    d = combined(json.loads(raw), rate_pct=a.rate_pct, factor=a.factor)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

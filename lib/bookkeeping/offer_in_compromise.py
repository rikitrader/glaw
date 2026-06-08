#!/usr/bin/env python3
"""GLAW offer-in-compromise engine (Form 656, doubt as to collectibility) — the minimum
acceptable offer equals the taxpayer's Reasonable Collection Potential (RCP):

  RCP = net realizable equity in assets + future income value
  net realizable equity = sum over assets of max(0, quick-sale value (80%) − loan balance)
  future income value   = max(0, monthly income − allowable living expenses) × multiplier
     lump-sum cash offer (paid in <= 5 months)  → 12 months
     periodic-payment offer (6-24 months)        → 24 months

An offer below RCP is generally rejected; an offer at/above RCP with doubt-as-to-collectibility
is the floor. (Allowable expenses follow the IRS Collection Financial Standards — supply them.)
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")
MULTIPLIER = {"lump": 12, "periodic": 24}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def rcp(assets: list[dict], monthly_income, allowable_expenses, *, offer_type="lump") -> dict:
    nre = Decimal("0")
    rows = []
    for a in assets:
        qsv = _dec(a.get("value", 0)) * Decimal("0.80")       # quick-sale value
        equity = max(Decimal("0"), qsv - _dec(a.get("loan", 0)))
        nre += equity
        rows.append({"asset": a.get("name", "?"), "value": str(_q(_dec(a.get("value", 0)))),
                     "quick_sale_80pct": str(_q(qsv)), "loan": str(_q(_dec(a.get("loan", 0)))),
                     "net_equity": str(_q(equity))})
    net_monthly = max(Decimal("0"), _dec(monthly_income) - _dec(allowable_expenses))
    mult = MULTIPLIER.get(offer_type, 12)
    fiv = _q(net_monthly * mult)
    rcp_total = _q(nre + fiv)
    return {"offer_type": offer_type, "assets": rows,
            "net_realizable_equity": str(_q(nre)),
            "net_monthly_income": str(_q(net_monthly)), "future_income_multiplier": mult,
            "future_income_value": str(fiv),
            "reasonable_collection_potential": str(rcp_total),
            "minimum_offer": str(rcp_total)}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "OFFER IN COMPROMISE (Form 656 — doubt as to collectibility)", "-" * 56,
        f"  net realizable equity    {_dec(d['net_realizable_equity']):>16,.2f}",
        f"  net monthly income       {_dec(d['net_monthly_income']):>16,.2f}",
        f"  future income value (×{d['future_income_multiplier']}) {_dec(d['future_income_value']):>14,.2f}",
        "-" * 56,
        f"  RCP / MINIMUM OFFER      {_dec(d['minimum_offer']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-oic")
    ap.add_argument("--assets", required=True, help="JSON file/'-': [{name, value, loan}]")
    ap.add_argument("--monthly-income", required=True)
    ap.add_argument("--allowable-expenses", required=True)
    ap.add_argument("--offer-type", default="lump", choices=["lump", "periodic"])
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.assets == "-" else Path(a.assets).read_text(encoding="utf-8")
    d = rcp(json.loads(raw), a.monthly_income, a.allowable_expenses, offer_type=a.offer_type)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

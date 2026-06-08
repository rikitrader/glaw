#!/usr/bin/env python3
"""GLAW FX revaluation — restate monetary foreign-currency balances to the closing rate.

Monetary assets/liabilities held in a foreign currency are remeasured each period end to
the closing spot rate; the difference is an unrealized FX gain or loss. Produces the
revaluation per balance and the net journal entry (Dr/Cr the account, offset to FX gain/loss).

Input JSON: [{"account": "...", "currency": "EUR", "foreign_amount": 100000,
              "booked_rate": 1.05, "closing_rate": 1.10, "monetary": true}]
booked_rate / closing_rate = units of REPORTING currency per 1 unit foreign.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def revalue(items: list[dict]) -> dict:
    rows, net_gain = [], Decimal("0")
    for it in items:
        if it.get("monetary") is False:
            continue                                   # non-monetary items are not revalued
        fa = _dec(it.get("foreign_amount"))
        booked = _dec(it.get("booked_rate"))
        closing = _dec(it.get("closing_rate"))
        # account type drives the gain/loss sign: a higher home-currency value is a GAIN on an
        # asset (worth more) but a LOSS on a liability (you owe more). Default asset.
        is_liab = (it.get("type") or "asset").lower().startswith("liab") \
            or str(it.get("account") or "").startswith("Liabilities")
        old_home = _q(fa * booked)
        new_home = _q(fa * closing)
        delta = new_home - old_home                    # change in home-currency carrying value
        pnl = -delta if is_liab else delta             # P&L effect (gain +, loss −)
        net_gain += pnl
        rows.append({"account": it.get("account"), "currency": it.get("currency"),
                     "type": "liability" if is_liab else "asset",
                     "foreign_amount": _q(fa), "booked_rate": booked, "closing_rate": closing,
                     "carrying_old": old_home, "carrying_new": new_home,
                     "fx_adjustment": _q(delta), "fx_pnl": _q(pnl)})
    # build the net revaluation entry. The account's carrying value moves by `delta`:
    #   asset      → Dr when delta>0 (asset grows), Cr when delta<0
    #   liability  → Cr when delta>0 (liability grows), Dr when delta<0
    lines = []
    for r in rows:
        adj = r["fx_adjustment"]
        if adj == 0:
            continue
        grows = adj > 0
        if r["type"] == "liability":
            lines.append({"account": r["account"], "debit": "0", "credit": str(adj)} if grows
                         else {"account": r["account"], "debit": str(-adj), "credit": "0"})
        else:
            lines.append({"account": r["account"], "debit": str(adj), "credit": "0"} if grows
                         else {"account": r["account"], "debit": "0", "credit": str(-adj)})
    if net_gain > 0:      # net gain → credit FX gain (income)
        lines.append({"account": "Income:FX Gain/Loss", "debit": "0", "credit": str(_q(net_gain))})
    elif net_gain < 0:
        lines.append({"account": "Expenses:FX Gain/Loss", "debit": str(_q(-net_gain)), "credit": "0"})
    return {"items": rows, "net_fx_gain": _q(net_gain),
            "result": "gain" if net_gain > 0 else ("loss" if net_gain < 0 else "none"),
            "entry": lines}


def render_text(d: dict) -> str:
    o = ["=" * 78, "FX REVALUATION", "-" * 78,
         f"  {'Account':<24}{'Ccy':>5}{'Foreign':>13}{'Old (home)':>14}{'New (home)':>14}{'FX adj':>12}"]
    for r in d["items"]:
        o.append(f"  {str(r['account'])[:23]:<24}{str(r['currency']):>5}{r['foreign_amount']:>13,.2f}"
                 f"{r['carrying_old']:>14,.2f}{r['carrying_new']:>14,.2f}{r['fx_adjustment']:>12,.2f}")
    o.append("-" * 78)
    o.append(f"  net FX {d['result']}: {d['net_fx_gain']:,.2f}")
    o.append("=" * 78)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-fx-reval")
    ap.add_argument("items", nargs="?", default="-", help="positions JSON (or '-')")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.items in (None, "-") else open(a.items, encoding="utf-8").read()
    items = json.loads(raw)
    if isinstance(items, dict) and "items" in items:
        items = items["items"]
    d = revalue(items)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

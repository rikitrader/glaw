#!/usr/bin/env python3
"""GLAW 13-week cash-flow projection — the treasury runway tool.

Input JSON: {"opening_cash": N, "minimum_cash": M (optional),
             "items": [{"week": 1..13, "amount": +/-, "label": "..."}]}
Projects the running cash balance week by week and flags any week that breaches the
minimum (or goes negative). The thing that actually prevents running out of cash.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def project(opening: Decimal, items: list[dict], *, weeks: int = 13,
            minimum: Decimal = Decimal("0")) -> dict:
    inflow = {w: Decimal("0") for w in range(1, weeks + 1)}
    outflow = {w: Decimal("0") for w in range(1, weeks + 1)}
    for it in items:
        w = int(it.get("week", 0))
        if not (1 <= w <= weeks):
            continue
        amt = _dec(it.get("amount"))
        (inflow if amt >= 0 else outflow)[w] += amt
    rows, bal, breaches, trough = [], opening, [], opening
    for w in range(1, weeks + 1):
        net = inflow[w] + outflow[w]
        bal += net
        trough = min(trough, bal)
        breach = bal < minimum
        if breach:
            breaches.append(w)
        rows.append({"week": w, "inflow": inflow[w], "outflow": outflow[w],
                     "net": net, "ending_cash": bal, "breach": breach})
    return {"opening_cash": opening, "minimum_cash": minimum, "weeks": weeks,
            "rows": rows, "ending_cash": bal, "trough": trough,
            "breach_weeks": breaches, "solvent": not breaches}


def render_text(p: dict) -> str:
    o = ["=" * 70, "13-WEEK CASH FLOW", "-" * 70,
         f"  opening cash: {p['opening_cash']:,.2f}   minimum: {p['minimum_cash']:,.2f}", "-" * 70,
         f"  {'Wk':<4}{'Inflow':>14}{'Outflow':>14}{'Net':>14}{'Ending cash':>16}  Flag"]
    for r in p["rows"]:
        flag = "⚠️ BREACH" if r["breach"] else ""
        o.append(f"  {r['week']:<4}{r['inflow']:>14,.0f}{r['outflow']:>14,.0f}"
                 f"{r['net']:>14,.0f}{r['ending_cash']:>16,.0f}  {flag}")
    o.append("-" * 70)
    o.append(f"  ending cash: {p['ending_cash']:,.2f}   trough: {p['trough']:,.2f}   "
             f"{'SOLVENT ✓' if p['solvent'] else 'BREACHES weeks ' + str(p['breach_weeks'])}")
    o.append("=" * 70)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-cashflow-13w")
    ap.add_argument("plan", nargs="?", default="-", help="plan JSON (or '-')")
    ap.add_argument("--weeks", type=int, default=13)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.plan in (None, "-") else open(a.plan, encoding="utf-8").read()
    d = json.loads(raw)
    res = project(_dec(d.get("opening_cash", 0)), d.get("items", []),
                  weeks=a.weeks, minimum=_dec(d.get("minimum_cash", 0)))
    print(json.dumps(res, indent=2, default=str) if a.format == "json" else render_text(res))
    return 0 if res["solvent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

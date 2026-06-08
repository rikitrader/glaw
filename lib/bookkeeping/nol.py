#!/usr/bin/env python3
"""GLAW net-operating-loss (NOL) carryforward engine.

Post-TCJA NOLs (years beginning after 2017) carry forward indefinitely but offset at most 80 %
of taxable income in the year used. Pre-2018 NOLs (if supplied with "pre_tcja": true) have no
80 % limit. Losses are used FIFO (oldest first). A current-year loss (negative taxable income)
adds to the carryforward instead of being used.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def apply_nol(taxable_income, carryforwards: list[dict] | None = None, *,
              current_year: int | None = None) -> dict:
    """taxable_income (before NOL) + prior NOLs [{year, amount, pre_tcja?}] →
    {nol_deduction, taxable_income_after_nol, used:[...], remaining_carryforward:[...]}."""
    ti = _dec(taxable_income)
    pool = sorted([dict(c) for c in (carryforwards or [])], key=lambda c: int(c.get("year", 0)))

    # a current-year loss is not "used" — it becomes a new carryforward
    if ti < 0:
        pool.append({"year": current_year or 9999, "amount": str(_q(-ti)), "pre_tcja": False})
        return {"taxable_income_before_nol": str(_q(ti)), "nol_deduction": "0.00",
                "taxable_income_after_nol": str(_q(ti)),
                "post_tcja_cap": "0.00", "used": [],
                "remaining_carryforward": [{"year": c.get("year"), "amount": str(_q(_dec(c["amount"])))}
                                           for c in pool if _dec(c["amount"]) > 0]}

    cap = _q(ti * Decimal("0.80"))                        # 80 % limit applies to post-TCJA NOLs
    used, remaining = [], []
    post_used = Decimal("0")                              # post-TCJA NOL used so far (subject to cap)
    offset = Decimal("0")
    for c in pool:
        amt = _dec(c["amount"])
        if amt <= 0:
            continue
        room = ti - offset
        if c.get("pre_tcja"):
            take = min(amt, room)                         # no 80 % cap on pre-TCJA NOLs
        else:
            take = min(amt, room, cap - post_used)        # capped at 80 % of taxable income
            post_used += take
        take = _q(take)
        if take > 0:
            used.append({"year": c.get("year"), "used": str(take)})
            offset += take
        left = _q(amt - take)
        if left > 0:
            remaining.append({"year": c.get("year"), "amount": str(left),
                              "pre_tcja": bool(c.get("pre_tcja"))})
    return {"taxable_income_before_nol": str(_q(ti)), "nol_deduction": str(_q(offset)),
            "taxable_income_after_nol": str(_q(ti - offset)), "post_tcja_cap": str(cap),
            "used": used, "remaining_carryforward": remaining}


def render_text(d: dict) -> str:
    o = ["=" * 56, "NOL CARRYFORWARD", "-" * 56,
         f"  taxable income before NOL {_dec(d['taxable_income_before_nol']):>16,.2f}",
         f"  80% limitation cap        {_dec(d['post_tcja_cap']):>16,.2f}",
         "  NOL used:"]
    for u in d["used"]:
        o.append(f"    from {u['year']}  {_dec(u['used']):>16,.2f}")
    o += [f"  NOL deduction             {_dec(d['nol_deduction']):>16,.2f}",
          f"  taxable income after NOL  {_dec(d['taxable_income_after_nol']):>16,.2f}",
          "  remaining carryforward:"]
    for r in d["remaining_carryforward"]:
        o.append(f"    {r['year']}  {_dec(r['amount']):>16,.2f}")
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-nol")
    ap.add_argument("--taxable-income", required=True, help="taxable income before NOL")
    ap.add_argument("--carryforwards", default=None, help="JSON file/'-': [{year, amount, pre_tcja?}]")
    ap.add_argument("--year", type=int, default=None, help="current year (labels a current-year loss)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    cf = []
    if a.carryforwards:
        raw = sys.stdin.read() if a.carryforwards == "-" else Path(a.carryforwards).read_text(encoding="utf-8")
        cf = json.loads(raw)
    d = apply_nol(a.taxable_income, cf, current_year=a.year)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

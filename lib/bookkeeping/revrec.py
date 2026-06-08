#!/usr/bin/env python3
"""GLAW revenue recognition (ASC 606) — deferred-revenue release schedule.

Cash received up front is a liability (deferred/unearned revenue) recognized as the
performance obligation is satisfied. Produces the period-by-period recognition schedule
and the journal entries (Dr Deferred Revenue / Cr Revenue) to post via glaw-journal.

  ratable    straight-line over N periods (subscriptions, retainers)
  milestone  recognize by explicit milestone percentages (must sum to 100)
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def ratable(amount: Decimal, periods: int) -> list[Decimal]:
    if periods <= 0:
        raise SystemExit("ERROR: --periods must be > 0 for ratable recognition")
    per = _q(amount / periods)
    out, accum = [], Decimal("0")
    for i in range(periods):
        v = per if i < periods - 1 else (amount - accum)   # true-up final period
        accum += v
        out.append(v)
    return out


def milestone(amount: Decimal, pcts: list[Decimal]) -> list[Decimal]:
    if sum(pcts) != Decimal("100"):
        raise SystemExit(f"ERROR: milestone percentages sum to {sum(pcts)}, not 100")
    out, accum = [], Decimal("0")
    for i, p in enumerate(pcts):
        v = _q(amount * p / Decimal("100")) if i < len(pcts) - 1 else (amount - accum)
        accum += v
        out.append(v)
    return out


def schedule(amount: Decimal, *, method: str, periods: int = 0,
             pcts: list[Decimal] | None = None) -> dict:
    if method == "ratable":
        recog = ratable(amount, periods)
    elif method == "milestone":
        recog = milestone(amount, pcts or [])
    else:
        raise SystemExit("ERROR: method must be ratable or milestone")
    rows, deferred, recognized = [], amount, Decimal("0")
    for i, r in enumerate(recog, start=1):
        deferred -= r
        recognized += r
        rows.append({"period": i, "recognized": _q(r), "recognized_to_date": _q(recognized),
                     "deferred_balance": _q(deferred),
                     "entry": [{"account": "Liabilities:Deferred Revenue", "debit": str(_q(r)), "credit": "0"},
                               {"account": "Income:Revenue", "debit": "0", "credit": str(_q(r))}]})
    return {"contract_amount": _q(amount), "method": method, "periods": len(recog),
            "total_recognized": _q(recognized), "ending_deferred": _q(deferred), "schedule": rows}


def render_text(d: dict) -> str:
    o = ["=" * 60, f"REVENUE RECOGNITION (ASC 606, {d['method']})", "-" * 60,
         f"  contract {d['contract_amount']:>14,.2f}", "-" * 60,
         f"  {'Period':<8}{'Recognized':>14}{'To date':>14}{'Deferred':>14}"]
    for r in d["schedule"]:
        o.append(f"  {r['period']:<8}{r['recognized']:>14,.2f}{r['recognized_to_date']:>14,.2f}"
                 f"{r['deferred_balance']:>14,.2f}")
    o.append("-" * 60)
    o.append(f"  total recognized {d['total_recognized']:>12,.2f}   ending deferred {d['ending_deferred']:>12,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-revrec")
    ap.add_argument("--amount", required=True)
    ap.add_argument("--method", default="ratable", choices=["ratable", "milestone"])
    ap.add_argument("--periods", type=int, default=0)
    ap.add_argument("--milestones", default="", help="comma %% for milestone method, e.g. 30,40,30")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    pcts = [Decimal(x) for x in a.milestones.split(",") if x.strip()] if a.milestones else None
    d = schedule(Decimal(a.amount), method=a.method, periods=a.periods, pcts=pcts)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

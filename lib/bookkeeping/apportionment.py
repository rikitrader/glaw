#!/usr/bin/env python3
"""GLAW multi-state income apportionment — split business income across states by the sales /
payroll / property factors.

Each state's factor for a category = state amount ÷ everywhere amount. The apportionment
percentage is a weighted average of the factors:
  three-factor (equal)   — (sales + payroll + property) / 3
  double-weighted sales  — (2·sales + payroll + property) / 4
  single-sales factor    — sales only   (the modern majority rule)
A factor whose everywhere-denominator is zero is dropped from the average (so the weights
re-normalize). State taxable income = apportionment % × apportionable business income.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_DP = Decimal("0.000001")
_CENT = Decimal("0.01")
WEIGHTS = {"three_factor": {"sales": 1, "payroll": 1, "property": 1},
           "double_sales": {"sales": 2, "payroll": 1, "property": 1},
           "single_sales": {"sales": 1, "payroll": 0, "property": 0}}


def _q(d: Decimal, e=_CENT) -> Decimal:
    return d.quantize(e, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def apportion(states: list[dict], apportionable_income, *, method: str = "three_factor") -> dict:
    w = WEIGHTS.get(method, WEIGHTS["three_factor"])
    income = _dec(apportionable_income)
    totals = {c: sum((_dec(s.get(c, 0)) for s in states), Decimal("0")) for c in ("sales", "payroll", "property")}
    # only categories with a nonzero everywhere-denominator AND a positive weight participate
    active = {c: w[c] for c in ("sales", "payroll", "property") if w[c] > 0 and totals[c] > 0}
    weight_sum = sum(active.values())

    rows = []
    allocated = Decimal("0")
    for i, s in enumerate(states):
        factors = {c: (_dec(s.get(c, 0)) / totals[c]) for c in active}
        weighted = sum(factors[c] * active[c] for c in active)
        pct = (weighted / weight_sum) if weight_sum else Decimal("0")
        if i == len(states) - 1:
            ti = _q(income - allocated)                      # last state absorbs the rounding residual
        else:
            ti = _q(income * pct)
            allocated += ti
        rows.append({"state": s.get("state", "?"), "method": method,
                     "factors": {c: str(_q(factors[c], _DP)) for c in active},
                     "apportionment_pct": str(_q(pct * 100, _DP)),
                     "taxable_income": str(ti)})
    return {"method": method, "apportionable_income": str(_q(income)),
            "states": rows,
            "total_apportioned": str(_q(sum((_dec(r["taxable_income"]) for r in rows), Decimal("0"))))}


def render_text(d: dict) -> str:
    o = ["=" * 60, f"STATE APPORTIONMENT ({d['method']})", "-" * 60,
         f"  apportionable income {_dec(d['apportionable_income']):>16,.2f}", "-" * 60]
    for s in d["states"]:
        o.append(f"  {s['state']:<8} {_dec(s['apportionment_pct']):>8,.4f}%   "
                 f"taxable income {_dec(s['taxable_income']):>16,.2f}")
    o += ["-" * 60, f"  total apportioned {_dec(d['total_apportioned']):>16,.2f}", "=" * 60]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-apportion")
    ap.add_argument("states", help="JSON file/'-': [{state, sales, payroll, property}]")
    ap.add_argument("--income", required=True, help="apportionable business income")
    ap.add_argument("--method", default="three_factor", choices=list(WEIGHTS))
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.states == "-" else Path(a.states).read_text(encoding="utf-8")
    d = apportion(json.loads(raw), a.income, method=a.method)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

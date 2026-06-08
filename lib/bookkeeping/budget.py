#!/usr/bin/env python3
"""GLAW budget-vs-actual — variance analysis from the ledger.

Compares a budget (JSON: {account: planned_amount}) against actuals computed from a
GLAW ledger (`glaw-bank-ingest --format json`). Reports per-account variance, percent
variance, and whether it is favorable or unfavorable (expenses over budget = bad;
income under budget = bad). Exit non-zero if any account breaches `--threshold`.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import statements as S   # noqa: E402


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def actuals_by_account(rows: list[dict]) -> dict[str, tuple[str, Decimal]]:
    """{account: (kind, actual)} for P&L accounts. kind = 'income' | 'expense'.
    actual is positive (revenue earned / expense incurred)."""
    pl = S.profit_loss(S.account_balances(rows))
    out: dict[str, tuple[str, Decimal]] = {}
    for r in pl["income"]:
        out[r["account"]] = ("income", r["amount"])
    for r in pl["expenses"]:
        out[r["account"]] = ("expense", r["amount"])
    return out


def variance(budget: dict[str, object], rows: list[dict], *, threshold_pct: Decimal = Decimal("10")
             ) -> dict:
    act = actuals_by_account(rows)
    lines = []
    breaches = 0
    for acct in sorted(set(budget) | set(act)):
        planned = _dec(budget.get(acct, 0))
        kind, actual = act.get(acct, ("expense" if acct.startswith("Expenses") else "income", Decimal("0")))
        var = actual - planned                     # actual minus budget
        # favorable: income above plan OR expense below plan
        if kind == "income":
            favorable = var >= 0
        else:
            favorable = var <= 0
        pct = (abs(var) / planned * 100) if planned != 0 else (Decimal("0") if actual == 0 else Decimal("100"))
        breach = (not favorable) and pct > threshold_pct
        if breach:
            breaches += 1
        lines.append({"account": acct, "kind": kind, "budget": planned, "actual": actual,
                      "variance": var, "variance_pct": pct.quantize(Decimal("0.1")),
                      "favorable": favorable, "breach": breach})
    return {"lines": lines, "breaches": breaches, "threshold_pct": threshold_pct,
            "on_budget": breaches == 0}


def render_text(v: dict) -> str:
    o = ["=" * 78, "BUDGET vs ACTUAL", "-" * 78,
         f"  {'Account':<34}{'Budget':>11}{'Actual':>11}{'Variance':>11}{'%':>6}  Flag",
         "-" * 78]
    for ln in v["lines"]:
        flag = "OK" if ln["favorable"] else ("BREACH" if ln["breach"] else "watch")
        o.append(f"  {ln['account']:<34}{ln['budget']:>11,.0f}{ln['actual']:>11,.0f}"
                 f"{ln['variance']:>11,.0f}{ln['variance_pct']:>5}%  {flag}")
    o.append("-" * 78)
    o.append(f"  threshold {v['threshold_pct']}%  |  breaches: {v['breaches']}  |  "
             f"{'ON BUDGET ✓' if v['on_budget'] else 'OVER THRESHOLD ✗'}")
    o.append("=" * 78)
    return "\n".join(o)


def _rows(payload) -> list[dict]:
    if isinstance(payload, dict) and "rows" in payload:
        return payload["rows"]
    if isinstance(payload, list):
        return payload
    raise SystemExit("ERROR: --actual must be glaw-bank-ingest JSON ({'rows': [...]})")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-budget-vs-actual")
    ap.add_argument("--budget", required=True, help="budget JSON: {account: planned_amount}")
    ap.add_argument("--actual", required=True, help="glaw-bank-ingest --format json (actuals)")
    ap.add_argument("--threshold", type=float, default=10.0, help="breach threshold %% (default 10)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    budget = json.load(open(a.budget, encoding="utf-8"))
    rows = _rows(json.load(open(a.actual, encoding="utf-8")))
    v = variance(budget, rows, threshold_pct=Decimal(str(a.threshold)))
    print(json.dumps(v, indent=2, default=str) if a.format == "json" else render_text(v))
    return 0 if v["on_budget"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

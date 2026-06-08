#!/usr/bin/env python3
"""glaw-cashflow — indirect-method statement of cash flows from the ledger.

Takes two balance snapshots (opening = day before the period; closing = period end),
buckets every account's change by its cash-flow tag, and presents:
  net income → operating adjustments → CFO → CFI → CFF → net change in cash,
reconciled to the actual change in cash.
"""
from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S      # noqa: E402
import ledger as L          # noqa: E402
import coa_tags as T        # noqa: E402


def _bounds(period: str):
    y, m = (int(x) for x in period.split("-")[:2])
    start = date(y, m, 1)
    end = date(y, m, monthrange(y, m)[1])
    return (start - timedelta(days=1)).isoformat(), end.isoformat()


def compute(book: str, *, period: str | None = None, frm: str | None = None,
            to: str | None = None, chart: str | None = None) -> dict:
    led = L.Ledger(book)
    if period:
        opening_asof, closing_asof = _bounds(period)
    else:
        opening_asof = (date.fromisoformat(frm) - timedelta(days=1)).isoformat() if frm else None
        closing_asof = to
    overrides = T.load_chart_tags(chart)
    classify = lambda a: T.classify(a, overrides)   # noqa: E731
    opening = led.balances(opening_asof) if opening_asof else {}
    closing = led.balances(closing_asof)
    cf = S.cash_flow_indirect(opening, closing, classify)
    cf["book"] = book
    cf["period"] = period or f"{frm or '...'}..{to or 'latest'}"
    return cf


def render_text(cf: dict) -> str:
    def m(x):
        return f"{Decimal(str(x)):>16,.2f}"
    o = ["=" * 60, f"STATEMENT OF CASH FLOWS (indirect) — {cf['book']}  {cf['period']}", "-" * 60,
         "  OPERATING ACTIVITIES",
         f"    Net income{m(cf['net_income'])}"]
    for r in cf["operating_adjustments"]:
        o.append(f"    {r['account'][:36]:<38}{m(r['amount'])}")
    o.append(f"    Net cash from operating{m(cf['operating'])}")
    o.append("  INVESTING ACTIVITIES")
    for r in cf["investing"]:
        o.append(f"    {r['account'][:36]:<38}{m(r['amount'])}")
    o.append(f"    Net cash from investing{m(cf['investing_total'])}")
    o.append("  FINANCING ACTIVITIES")
    for r in cf["financing"]:
        o.append(f"    {r['account'][:36]:<38}{m(r['amount'])}")
    o.append(f"    Net cash from financing{m(cf['financing_total'])}")
    o.append("-" * 60)
    o.append(f"  NET CHANGE IN CASH{m(cf['net_change_in_cash'])}")
    o.append(f"  (change in cash balance{m(cf['change_in_cash'])})  "
             f"{'reconciled ✓' if cf['reconciles'] else 'DOES NOT RECONCILE ✗'}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-cashflow")
    ap.add_argument("--book", required=True)
    ap.add_argument("--period", default=None, help="reporting month YYYY-MM")
    ap.add_argument("--from", dest="frm", default=None)
    ap.add_argument("--to", default=None)
    ap.add_argument("--chart", default=None, help="chart tags name for exact classification")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    cf = compute(a.book, period=a.period, frm=a.frm, to=a.to, chart=a.chart)
    print(json.dumps(cf, indent=2, default=str) if a.format == "json" else render_text(cf))
    return 0 if cf["reconciles"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GLAW comparative reporting — MTD / prior period / YTD / budget, from the ledger.

Single-period statements answer "what is the balance". Comparatives answer "how does
this period compare" — the view a CFO and a board actually read. Income-statement figures
are period-bounded (activity within the window); balance-sheet figures are as-of the
window end.
"""
from __future__ import annotations

import json
import sys
from calendar import monthrange
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S      # noqa: E402
import ledger as L          # noqa: E402


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _month_bounds(period: str) -> tuple[date, date]:
    y, m = (int(x) for x in period.split("-")[:2])
    return date(y, m, 1), date(y, m, monthrange(y, m)[1])


def _in_window(postings, frm: date, to: date):
    return [p for p in postings if frm <= date.fromisoformat(p["date"]) <= to]


def _pl_total(postings) -> dict:
    """P&L summary {revenue, expenses, net_income, by_account} from a posting list."""
    bal = S.balances_from_postings(postings)
    pl = S.profit_loss(bal)
    by = {}
    for r in pl["income"]:
        by[r["account"]] = r["amount"]
    for r in pl["expenses"]:
        by[r["account"]] = -r["amount"]   # show expenses negative in the P&L column
    return {"revenue": pl["revenue_total"], "expenses": pl["expense_total"],
            "net_income": pl["net_income"], "by_account": by}


def comparative(book: str, period: str, *, budget: dict | None = None) -> dict:
    led = L.Ledger(book)
    postings = led.postings()
    cur_f, cur_t = _month_bounds(period)
    # prior month
    pm = (cur_f.replace(day=1))
    prior_f, prior_t = _month_bounds(f"{pm.year - (pm.month == 1)}-{12 if pm.month == 1 else pm.month - 1:02d}")
    ytd_f = date(cur_f.year, 1, 1)

    cols = {
        "current": _pl_total(_in_window(postings, cur_f, cur_t)),
        "prior": _pl_total(_in_window(postings, prior_f, prior_t)),
        "ytd": _pl_total(_in_window(postings, ytd_f, cur_t)),
    }
    accounts = sorted(set().union(*[set(c["by_account"]) for c in cols.values()]))
    lines = []
    for acct in accounts:
        cur = cols["current"]["by_account"].get(acct, Decimal("0"))
        pri = cols["prior"]["by_account"].get(acct, Decimal("0"))
        ytd = cols["ytd"]["by_account"].get(acct, Decimal("0"))
        row = {"account": acct, "current": cur, "prior": pri, "ytd": ytd,
               "vs_prior": cur - pri}
        if budget is not None:
            bud = _dec(budget.get(acct, 0))
            row["budget"] = bud
            row["vs_budget"] = cur - bud
        lines.append(row)
    return {"book": book, "period": period, "has_budget": budget is not None,
            "lines": lines,
            "net_income": {"current": cols["current"]["net_income"],
                           "prior": cols["prior"]["net_income"], "ytd": cols["ytd"]["net_income"]}}


def render_text(c: dict) -> str:
    has_b = c["has_budget"]
    hdr = f"  {'Account':<30}{'Current':>13}{'Prior':>13}{'Δ Prior':>13}{'YTD':>13}"
    if has_b:
        hdr += f"{'Budget':>13}{'Δ Budget':>13}"
    o = ["=" * (len(hdr) + 2), f"COMPARATIVE P&L — {c['book']}  period {c['period']}", "-" * (len(hdr) + 2),
         hdr, "-" * (len(hdr) + 2)]
    for ln in c["lines"]:
        row = (f"  {ln['account'][:29]:<30}{ln['current']:>13,.0f}{ln['prior']:>13,.0f}"
               f"{ln['vs_prior']:>13,.0f}{ln['ytd']:>13,.0f}")
        if has_b:
            row += f"{ln['budget']:>13,.0f}{ln['vs_budget']:>13,.0f}"
        o.append(row)
    ni = c["net_income"]
    o.append("-" * (len(hdr) + 2))
    o.append(f"  {'NET INCOME':<30}{ni['current']:>13,.0f}{ni['prior']:>13,.0f}"
             f"{ni['current'] - ni['prior']:>13,.0f}{ni['ytd']:>13,.0f}")
    o.append("=" * (len(hdr) + 2))
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-comparative")
    ap.add_argument("--book", required=True)
    ap.add_argument("--period", required=True, help="reporting month YYYY-MM")
    ap.add_argument("--budget", default=None, help="optional budget JSON {account: amount}")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    budget = json.load(open(a.budget, encoding="utf-8")) if a.budget else None
    c = comparative(a.book, a.period, budget=budget)
    print(json.dumps(c, indent=2, default=str) if a.format == "json" else render_text(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

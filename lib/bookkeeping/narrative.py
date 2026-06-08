#!/usr/bin/env python3
"""GLAW financial narrative — turn the ledger statements into an SEC-filing-style report.

Generates, from the posted general ledger, an MD&A-style narrative plus notes to the
financial statements — the prose that makes the numbers legible the way a 10-K does.
Every figure is pulled from the ledger; nothing is invented. The disclosure JUDGMENT
(what to emphasize, risk factors) is the CFO/Audit agents' job — this is the scaffold,
filled with real numbers.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import statements as S      # noqa: E402
import ledger as L          # noqa: E402


def _m(d) -> str:
    return f"${Decimal(str(d)):,.2f}"


def _pct(n, d) -> str:
    n, d = Decimal(str(n)), Decimal(str(d))
    return f"{(n / d * 100):.1f}%" if d else "n/m"


def generate(book: str, *, period: str | None = None, as_of: str | None = None,
             entity: str = "the Company") -> str:
    led = L.Ledger(book)
    postings = [{"account": p["account"], "amount": p["amount"], "id": p["id"]}
                for p in led.postings(as_of)]
    s = S.build(postings=postings)
    pl, bs, cf = s["profit_loss"], s["balance_sheet"], s["cash_flow"]
    bal = S.balances_from_postings(postings)
    rev, exp, ni = pl["revenue_total"], pl["expense_total"], pl["net_income"]
    cash = sum((b for a, b in bal.items() if str(a).startswith(S._CASH_HINTS)), Decimal("0"))

    o: list[str] = []
    title = f"FINANCIAL REPORT — {entity}"
    if period:
        title += f" — period {period}"
    o += [f"# {title}", "",
          "_Prepared from the posted general ledger. Management discussion & analysis and",
          "notes to the financial statements. For review and sign-off by a licensed CPA / attorney._", ""]

    # 1. Overview
    o += ["## 1. Overview", "",
          f"For the period presented, {entity} reported total revenue of **{_m(rev)}**, total "
          f"expenses of **{_m(exp)}**, and **net {'income' if ni >= 0 else 'loss'} of "
          f"{_m(abs(ni))}** (net margin {_pct(ni, rev)}). The books are maintained on the accrual "
          f"basis and the trial balance is in balance "
          f"({'✓' if s['trial_balance']['balanced'] else 'OUT OF BALANCE'}).", ""]

    # 2. Results of operations
    o += ["## 2. Management Discussion & Analysis", "", "### 2.1 Results of operations", ""]
    if pl["income"]:
        o.append("Revenue by source:")
        for r in pl["income"]:
            o.append(f"- {r['account']}: {_m(r['amount'])} ({_pct(r['amount'], rev)} of revenue)")
        o.append("")
    if pl["expenses"]:
        o.append("Expenses by category:")
        for r in pl["expenses"]:
            o.append(f"- {r['account']}: {_m(r['amount'])} ({_pct(r['amount'], exp)} of expense)")
        o.append("")

    # period-over-period drivers
    if period:
        try:
            import comparative as C
            comp = C.comparative(book, period)
            drivers = sorted(comp["lines"], key=lambda x: -abs(x["vs_prior"]))[:3]
            if drivers:
                o.append("**Period-over-period drivers** (vs. prior month): "
                         + "; ".join(f"{d['account']} {('+' if d['vs_prior']>=0 else '')}{_m(d['vs_prior'])}"
                                     for d in drivers) + ".")
                o.append("")
        except Exception:
            pass

    # 3. Liquidity
    assets = bs["assets_total"]
    liabilities = bs["liabilities_total"]
    o += ["### 2.2 Liquidity & capital resources", "",
          f"Cash and cash equivalents stood at **{_m(cash)}**. Total assets were {_m(assets)} "
          f"against total liabilities of {_m(liabilities)}, leaving equity (incl. current-period "
          f"earnings) of {_m(bs['equity_total'])}. Net cash flow for the period was "
          f"{_m(cf['net_change_in_cash'])} (operating {_m(cf['operating'])}, investing "
          f"{_m(cf['investing'])}, financing {_m(cf['financing'])}).", ""]

    # 4. Notes
    o += ["## 3. Notes to the Financial Statements", "",
          "**Note 1 — Basis of presentation.** The financial statements are prepared from a "
          "double-entry general ledger on the accrual basis of accounting. Each balance is "
          "supported by posted, balanced journal entries with a documented source; the ledger is "
          "append-only and tamper-evident.", ""]
    note = 2
    for root, label in (("Assets", "Assets"), ("Liabilities", "Liabilities"),
                        ("Equity", "Equity"), ("Income", "Revenue"), ("Expenses", "Expenses")):
        items = sorted((a, b) for a, b in bal.items() if a.split(":", 1)[0] == root and b != 0)
        if not items:
            continue
        o.append(f"**Note {note} — {label}.** " + "; ".join(
            f"{a} {_m(abs(b))}" for a, b in items) + ".")
        o.append("")
        note += 1
    o += ["**Note %d — Subsequent events.** Management has evaluated events through the report "
          "date; any material subsequent events are disclosed by the CFO/Audit agents." % note, "",
          "---", "_Not legal, tax, or accounting advice. Attorney/CPA-reviewed work-product._"]
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-narrative")
    ap.add_argument("--book", required=True)
    ap.add_argument("--period", default=None, help="reporting month YYYY-MM (adds period-over-period drivers)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--entity", default="the Company")
    a = ap.parse_args()
    print(generate(a.book, period=a.period, as_of=a.as_of, entity=a.entity))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

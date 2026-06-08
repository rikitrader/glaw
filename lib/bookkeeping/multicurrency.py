#!/usr/bin/env python3
"""GLAW multi-currency GL — per-currency balances + current-rate translation.

A flat ledger cannot sum balances across currencies (books-doctor fails a mixed book).
This module makes a multi-currency book reportable: it groups balances by the currency of
each entry, then translates every currency into a single REPORTING currency using the
current-rate method —
  balance-sheet accounts (assets/liabilities) at the closing rate,
  income/expense at the average rate,
  equity at the historical rate —
and posts the residual that mixed rates create to **Equity:CTA** (cumulative translation
adjustment), so the translated trial balance balances. This is exactly the translation a
foreign operation needs before it can be consolidated into the parent's reporting currency.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402
import statements as S      # noqa: E402

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def balances_by_currency(book: str, *, as_of: str | None = None,
                         reporting: str = "USD") -> dict[str, dict[str, Decimal]]:
    """{currency: {account: signed_balance}} — each entry's currency tags its postings.
    Entries with no currency are treated as the reporting currency."""
    out: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for e in L.Ledger(book).entries(as_of):
        ccy = e.get("currency") or reporting
        for ln in e["lines"]:
            out[ccy][ln["account"]] += _dec(ln["debit"]) - _dec(ln["credit"])
    return {c: dict(v) for c, v in out.items()}


def translate(by_ccy: dict[str, dict[str, Decimal]], rates: dict, *,
              reporting: str = "USD", cta_account: str = "Equity:CTA") -> dict:
    """Translate every currency to the reporting currency (current-rate method).
    rates: {ccy: {"closing": r, "average": r, "historical": r}} (average/historical
    default to closing). The plug to balance = the CTA."""
    rep: dict[str, Decimal] = defaultdict(Decimal)
    used = {}
    for ccy, accts in by_ccy.items():
        if ccy == reporting:
            for a, b in accts.items():
                rep[a] += b
            continue
        rt = rates.get(ccy) or {}
        closing = _dec(rt.get("closing", 1))
        average = _dec(rt.get("average", rt.get("closing", 1)))
        historical = _dec(rt.get("historical", rt.get("closing", 1)))
        used[ccy] = {"closing": str(closing), "average": str(average), "historical": str(historical)}
        for a, b in accts.items():
            root = a.split(":", 1)[0]
            if root in ("Income", "Revenue", "Expenses"):
                r = average
            elif root == "Equity":
                r = historical
            else:                              # assets, liabilities → closing rate
                r = closing
            rep[a] += _q(b * r)
    # mixed rates leave the translated TB out of balance; the residual is the CTA
    imbalance = sum(rep.values(), Decimal("0"))
    cta = -imbalance
    if cta != 0:
        rep[cta_account] += cta
    return {"reporting": reporting, "rates_used": used,
            "balances": {a: b for a, b in rep.items() if b != 0},
            "cta": _q(cta), "balanced": sum(rep.values(), Decimal("0")) == 0}


def report(book: str, *, reporting: str = "USD", rates: dict | None = None,
           as_of: str | None = None) -> dict:
    by_ccy = balances_by_currency(book, as_of=as_of, reporting=reporting)
    currencies = sorted(by_ccy)
    tr = translate(by_ccy, rates or {}, reporting=reporting)
    # statements from the translated (single-currency) balances
    stmts = S.build(postings=[{"account": a, "amount": b} for a, b in tr["balances"].items()])
    return {"book": book, "reporting": reporting, "currencies": currencies,
            "by_currency": {c: {a: str(b) for a, b in v.items()} for c, v in by_ccy.items()},
            "translated": {a: str(b) for a, b in tr["balances"].items()},
            "cta": str(tr["cta"]), "translated_balances": tr["balanced"],
            "trial_balance_balanced": stmts["trial_balance"]["balanced"],
            "net_income": str(stmts["profit_loss"]["net_income"])}


def render_text(r: dict) -> str:
    o = ["=" * 64, f"MULTI-CURRENCY GL — {r['book']}  (reporting {r['reporting']})", "-" * 64,
         f"  currencies present: {', '.join(r['currencies'])}", "-" * 64,
         "  PER-CURRENCY balances:"]
    for c, accts in r["by_currency"].items():
        o.append(f"   [{c}]")
        for a, b in sorted(accts.items()):
            if _dec(b) != 0:
                o.append(f"     {a:<38}{_dec(b):>16,.2f}")
    o.append("-" * 64)
    o.append(f"  TRANSLATED to {r['reporting']} (current-rate method):")
    for a, b in sorted(r["translated"].items()):
        o.append(f"     {a:<38}{_dec(b):>16,.2f}")
    o.append(f"  CTA (cumulative translation adjustment): {_dec(r['cta']):,.2f}")
    o.append(f"  translated TB balances: {'✓' if r['trial_balance_balanced'] else '✗'}   "
             f"net income: {_dec(r['net_income']):,.2f}")
    o.append("=" * 64)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fx-report")
    ap.add_argument("--book", required=True)
    ap.add_argument("--reporting", default="USD", help="reporting currency (default USD)")
    ap.add_argument("--rates", default=None, help="rates JSON: {ccy:{closing,average,historical}}")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    rates = json.load(open(a.rates, encoding="utf-8")) if a.rates else {}
    r = report(a.book, reporting=a.reporting, rates=rates, as_of=a.as_of)
    print(json.dumps(r, indent=2, default=str) if a.format == "json" else render_text(r))
    return 0 if r["trial_balance_balanced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

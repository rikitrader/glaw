#!/usr/bin/env python3
"""GLAW sales & use tax engine — economic-nexus determination (post-Wayfair) + the sales-tax-due
schedule, reconciled to the GL Sales Tax Payable.

Economic nexus: a state's threshold is typically $100,000 in sales OR 200 transactions in the
current or prior year (some states are sales-only, some have higher thresholds — both are
supplied per state). For each state where nexus exists, taxable sales × the state rate = the tax
due; the engine then ties the computed liability to the posted Liabilities:Sales Tax Payable.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402

_CENT = Decimal("0.01")
DEFAULT_SALES_THRESHOLD = Decimal("100000")
DEFAULT_TXN_THRESHOLD = 200


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def nexus_and_tax(states: list[dict]) -> dict:
    """states: [{state, sales, transactions, taxable_sales, rate, sales_threshold?, txn_threshold?,
    txn_nexus?}]. Returns per-state nexus + tax due and the total liability."""
    rows = []
    total = Decimal("0")
    for s in states:
        sales = _dec(s.get("sales", 0))
        txns = int(s.get("transactions", 0))
        s_thr = _dec(s.get("sales_threshold", DEFAULT_SALES_THRESHOLD))
        t_thr = int(s.get("txn_threshold", DEFAULT_TXN_THRESHOLD))
        txn_counts = s.get("txn_nexus", True)               # some states dropped the txn test
        nexus = sales >= s_thr or (txn_counts and txns >= t_thr)
        taxable = _dec(s.get("taxable_sales", sales))
        rate = _dec(s.get("rate", 0))
        tax = _q(taxable * rate / Decimal("100")) if nexus else _q(Decimal("0"))
        total += tax
        reason = ("sales≥threshold" if sales >= s_thr else
                  ("transactions≥threshold" if (txn_counts and txns >= t_thr) else "no nexus"))
        rows.append({"state": s.get("state", "?"), "sales": str(_q(sales)), "transactions": txns,
                     "nexus": nexus, "reason": reason, "taxable_sales": str(_q(taxable)),
                     "rate_pct": str(rate), "tax_due": str(tax)})
    return {"states": rows, "total_tax_due": str(_q(total))}


def reconcile(book: str, computed_total, *, as_of: str | None = None,
              account: str = "Liabilities:Sales Tax Payable") -> dict:
    bal = L.Ledger(book).balances(as_of)
    posted = _q(-bal.get(account, Decimal("0")))            # credit-normal liability → positive
    computed = _q(_dec(computed_total))
    return {"computed_tax_due": str(computed), "posted_sales_tax_payable": str(posted),
            "difference": str(_q(computed - posted)), "ties_out": computed == posted}


def render_text(d: dict) -> str:
    o = ["=" * 64, "SALES & USE TAX — economic nexus", "-" * 64,
         f"  {'state':<8}{'sales':>14}{'txns':>7}  nexus  {'rate':>7}{'tax due':>14}"]
    for s in d["states"]:
        o.append(f"  {s['state']:<8}{_dec(s['sales']):>14,.0f}{s['transactions']:>7}  "
                 f"{'YES' if s['nexus'] else ' no':<5}{_dec(s['rate_pct']):>7,.2f}{_dec(s['tax_due']):>14,.2f}")
    o += ["-" * 64, f"  total tax due {_dec(d['total_tax_due']):>16,.2f}", "=" * 64]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-sales-use-tax")
    ap.add_argument("states", help="JSON file/'-': [{state, sales, transactions, taxable_sales, rate}]")
    ap.add_argument("--book", default=None, help="reconcile the total to this book's Sales Tax Payable")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.states == "-" else Path(a.states).read_text(encoding="utf-8")
    d = nexus_and_tax(json.loads(raw))
    if a.book:
        d["reconciliation"] = reconcile(a.book, d["total_tax_due"], as_of=a.as_of)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

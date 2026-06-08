#!/usr/bin/env python3
"""GLAW financial-statement generator — native, deterministic, no hledger.

Consumes the JSON produced by `glaw-bank-ingest --format json` (a list of
categorized transactions) and computes the four core statements directly from
double-entry postings:

  Trial Balance · Profit & Loss · Balance Sheet · Statement of Cash Flows

Double-entry model (matches the engine's ledger export):
  each transaction posts  +amount → the bank account  and  -amount → the contra
  account (its mapped `category`). Every posting set sums to 0, so debits == credits
  and Assets == Liabilities + Equity + Net Income hold BY CONSTRUCTION — the books
  cannot silently go out of balance.

Sign convention (plaintext-accounting / hledger): a positive balance is a debit
(Assets, Expenses); a negative balance is a credit (Liabilities, Equity, Income).
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from collections import defaultdict
from typing import Iterable

# Account roots → statement classification.
_ROOTS = ("Assets", "Liabilities", "Equity", "Income", "Revenue", "Expenses")
_INCOME_ROOTS = ("Income", "Revenue")
_CASH_HINTS = ("Assets:Bank", "Assets:Cash")


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _resolve_contra(category: str | None, default: str = "Expenses:Uncategorized") -> str:
    """Mirror glaw_engine.export.ledger._resolve_contra: full account paths pass
    through; bare buckets nest under Expenses:."""
    if not category:
        return default
    safe = category.replace(" ", ":").replace("/", ":")
    roots = ("Expenses:", "Income:", "Revenue:", "Assets:", "Liabilities:", "Equity:")
    return safe if safe.startswith(roots) else f"Expenses:{safe}"


def account_balances(rows: Iterable[dict], *, bank_account: str = "Assets:Bank:Checking"
                     ) -> dict[str, Decimal]:
    """Post every transaction double-entry and return {account: signed balance}."""
    bal: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for r in rows:
        amt = _dec(r.get("amount"))
        contra = _resolve_contra(r.get("category"))
        bal[bank_account] += amt      # debit/credit the bank
        bal[contra] -= amt            # opposite leg
    return dict(bal)


def _root(acct: str) -> str:
    head = acct.split(":", 1)[0]
    return head if head in _ROOTS else "Unclassified"


def trial_balance(bal: dict[str, Decimal]) -> dict:
    rows = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    for acct in sorted(bal):
        b = bal[acct]
        if b == 0:
            continue
        debit = b if b > 0 else Decimal("0")
        credit = -b if b < 0 else Decimal("0")
        total_debit += debit
        total_credit += credit
        rows.append({"account": acct, "debit": debit, "credit": credit})
    balanced = (total_debit + (-total_credit)) == 0  # debits == credits
    return {"rows": rows, "total_debit": total_debit, "total_credit": total_credit,
            "balanced": total_debit == total_credit}


def profit_loss(bal: dict[str, Decimal]) -> dict:
    income, expenses = [], []
    rev_total = Decimal("0")
    exp_total = Decimal("0")
    for acct in sorted(bal):
        b = bal[acct]
        if b == 0:
            continue
        if _root(acct) in _INCOME_ROOTS:
            amt = -b                  # credit balance shown as positive revenue
            income.append({"account": acct, "amount": amt})
            rev_total += amt
        elif _root(acct) == "Expenses":
            expenses.append({"account": acct, "amount": b})
            exp_total += b
    return {"income": income, "expenses": expenses, "revenue_total": rev_total,
            "expense_total": exp_total, "net_income": rev_total - exp_total}


def balance_sheet(bal: dict[str, Decimal], net_income: Decimal) -> dict:
    assets, liabilities, equity = [], [], []
    a_total = l_total = e_total = Decimal("0")
    for acct in sorted(bal):
        b = bal[acct]
        if b == 0:
            continue
        root = _root(acct)
        if root == "Assets":
            assets.append({"account": acct, "amount": b}); a_total += b
        elif root == "Liabilities":
            liabilities.append({"account": acct, "amount": -b}); l_total += -b
        elif root == "Equity":
            equity.append({"account": acct, "amount": -b}); e_total += -b
    # current-period earnings roll into equity
    equity.append({"account": "Equity:RetainedEarnings (current period)", "amount": net_income})
    e_total += net_income
    return {"assets": assets, "liabilities": liabilities, "equity": equity,
            "assets_total": a_total, "liabilities_total": l_total, "equity_total": e_total,
            "balances": a_total == (l_total + e_total)}


def cash_flow(rows: Iterable[dict]) -> dict:
    """Direct cash-flow by activity. Cash change = sum of bank postings; classify the
    contra (the reason for the cash move) into Operating / Investing / Financing."""
    op = inv = fin = Decimal("0")
    for r in rows:
        amt = _dec(r.get("amount"))
        contra = _resolve_contra(r.get("category"))
        root = _root(contra)
        if root in _INCOME_ROOTS or root == "Expenses":
            op += amt
        elif root == "Assets":           # buying/selling assets/investments
            inv += amt
        elif root in ("Liabilities", "Equity"):
            fin += amt
        else:
            op += amt                    # unclassified → operating (and flagged in TB)
    return {"operating": op, "investing": inv, "financing": fin,
            "net_change_in_cash": op + inv + fin}


def build(rows: list[dict], *, bank_account: str = "Assets:Bank:Checking") -> dict:
    bal = account_balances(rows, bank_account=bank_account)
    tb = trial_balance(bal)
    pl = profit_loss(bal)
    bs = balance_sheet(bal, pl["net_income"])
    cf = cash_flow(rows)
    unclassified = sorted(a for a in bal if _root(a) == "Unclassified" and bal[a] != 0)
    return {"trial_balance": tb, "profit_loss": pl, "balance_sheet": bs,
            "cash_flow": cf, "unclassified_accounts": unclassified,
            "transaction_count": len(rows)}


def _m(d: Decimal) -> str:
    return f"{d:,.2f}"


def render_text(s: dict, *, currency: str = "USD") -> str:
    out: list[str] = []
    tb, pl, bs, cf = s["trial_balance"], s["profit_loss"], s["balance_sheet"], s["cash_flow"]
    out.append("=" * 66)
    out.append(f"TRIAL BALANCE   ({currency})")
    out.append("-" * 66)
    out.append(f"  {'Account':<38}{'Debit':>13}{'Credit':>13}")
    for r in tb["rows"]:
        deb = _m(r["debit"]) if r["debit"] else ""
        cred = _m(r["credit"]) if r["credit"] else ""
        out.append(f"  {r['account']:<38}{deb:>13}{cred:>13}")
    out.append("-" * 66)
    out.append(f"  {'TOTAL':<38}{_m(tb['total_debit']):>13}{_m(tb['total_credit']):>13}")
    out.append(f"  {'BALANCED ✓' if tb['balanced'] else '*** OUT OF BALANCE ***'}")
    out.append("")
    out.append(f"PROFIT & LOSS   ({currency})")
    out.append("-" * 60)
    for r in pl["income"]:
        out.append(f"  {r['account']:<48}{_m(r['amount']):>10}")
    out.append(f"  {'Total revenue':<48}{_m(pl['revenue_total']):>10}")
    for r in pl["expenses"]:
        out.append(f"  {r['account']:<48}{_m(-r['amount']):>10}")
    out.append(f"  {'Total expenses':<48}{_m(-pl['expense_total']):>10}")
    out.append(f"  {'NET INCOME':<48}{_m(pl['net_income']):>10}")
    out.append("")
    out.append(f"BALANCE SHEET   ({currency})")
    out.append("-" * 60)
    for label, items, tot in (("Assets", bs["assets"], bs["assets_total"]),
                              ("Liabilities", bs["liabilities"], bs["liabilities_total"]),
                              ("Equity", bs["equity"], bs["equity_total"])):
        out.append(f"  {label}")
        for r in items:
            out.append(f"    {r['account']:<46}{_m(r['amount']):>10}")
        out.append(f"    {'Total ' + label:<46}{_m(tot):>10}")
    ok = "Assets = Liabilities + Equity ✓" if bs["balances"] else "*** DOES NOT BALANCE ***"
    out.append(f"  {ok}")
    out.append("")
    out.append(f"STATEMENT OF CASH FLOWS   ({currency})")
    out.append("-" * 60)
    out.append(f"  {'Operating':<48}{_m(cf['operating']):>10}")
    out.append(f"  {'Investing':<48}{_m(cf['investing']):>10}")
    out.append(f"  {'Financing':<48}{_m(cf['financing']):>10}")
    out.append(f"  {'NET CHANGE IN CASH':<48}{_m(cf['net_change_in_cash']):>10}")
    if s["unclassified_accounts"]:
        out.append("")
        out.append("⚠️  unclassified accounts (no Assets/Liabilities/Equity/Income/Expenses root):")
        for a in s["unclassified_accounts"]:
            out.append(f"    {a}")
    out.append("=" * 60)
    return "\n".join(out)


def _load_rows(src: str | None) -> list[dict]:
    raw = sys.stdin.read() if (src in (None, "-")) else open(src, encoding="utf-8").read()
    data = json.loads(raw)
    if isinstance(data, dict) and "rows" in data:   # glaw-bank-ingest --format json
        return data["rows"]
    if isinstance(data, list):
        return data
    raise SystemExit("ERROR: input is not glaw-bank-ingest JSON (expected {'rows': [...]})")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-statements")
    ap.add_argument("json", nargs="?", default="-",
                    help="glaw-bank-ingest --format json file (or '-' for stdin)")
    ap.add_argument("--account", default="Assets:Bank:Checking", help="bank account name")
    ap.add_argument("--currency", default="USD")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    rows = _load_rows(a.json)
    s = build(rows, bank_account=a.account)
    if a.format == "json":
        print(json.dumps(s, indent=2, default=str))
    else:
        print(render_text(s, currency=a.currency))
    # exit non-zero if the books don't balance (a real control signal)
    ok = s["trial_balance"]["balanced"] and s["balance_sheet"]["balances"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

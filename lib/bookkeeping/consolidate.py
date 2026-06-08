#!/usr/bin/env python3
"""GLAW consolidation — combine multiple entity ledgers and eliminate intercompany.

Each entity is its own GLAW ledger book. Consolidation sums every entity's account
balances, then posts ELIMINATION entries to remove intercompany balances/transactions
(intercompany AR/AP, intercompany sales/COGS, investment-in-sub vs subsidiary equity).
The consolidated trial balance must still balance (debits == credits).

Eliminations JSON: a list of balanced entries, same shape as journal entries:
  [{"memo": "eliminate IC AR/AP", "lines": [{"account":"Assets:IC Receivable","credit":50000},
                                             {"account":"Liabilities:IC Payable","debit":50000}]}]
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402
import statements as S      # noqa: E402


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _entity_equity_and_ni(bal: dict[str, Decimal]) -> tuple[Decimal, Decimal]:
    """From one entity's balances: (equity_total, net_income), both as positive figures.
    Equity & income are credit-normal (negative signed) → flip the sign."""
    equity = sum((-b for a, b in bal.items() if a.split(":", 1)[0] == "Equity"), Decimal("0"))
    ni = sum((-b for a, b in bal.items()
              if a.split(":", 1)[0] in ("Income", "Revenue", "Expenses")), Decimal("0"))
    return equity, ni


def equity_method(cost: Decimal, ownership: Decimal, net_income: Decimal,
                  dividends: Decimal) -> dict:
    """Equity-method roll-forward for a 20-50% investee (significant influence, no control):
    the investee is NOT consolidated; the parent carries an investment that rolls forward as
      Investment = cost + ownership × cumulative net income − ownership × dividends,
    recognizing ownership × NI as equity-method income."""
    income = (ownership * net_income).quantize(Decimal("0.01"))
    div_share = (ownership * dividends).quantize(Decimal("0.01"))
    ending = (cost + income - div_share).quantize(Decimal("0.01"))
    return {"cost": cost, "ownership": ownership, "equity_method_income": income,
            "dividends_received": div_share, "ending_investment": ending,
            "entries": [
                {"memo": "equity-method income",
                 "lines": [{"account": "Assets:Investment in Affiliate", "debit": str(income), "credit": "0"},
                           {"account": "Income:Equity-Method Income", "debit": "0", "credit": str(income)}]},
                {"memo": "dividends received (reduce investment)",
                 "lines": [{"account": "Assets:Bank:Checking", "debit": str(div_share), "credit": "0"},
                           {"account": "Assets:Investment in Affiliate", "debit": "0", "credit": str(div_share)}]},
            ]}


def consolidate(books: list[str], eliminations: list[dict] | None = None,
                *, as_of: str | None = None, ownership: dict | None = None,
                nci_account: str = "Equity:Non-Controlling Interest",
                controlling_account: str = "Equity:Retained Earnings (controlling)") -> dict:
    ownership = ownership or {}
    combined: dict[str, Decimal] = {}
    per_entity = {}
    for b in books:
        bal = L.Ledger(b).balances(as_of)
        per_entity[b] = {a: str(v) for a, v in bal.items()}
        for a, v in bal.items():
            combined[a] = combined.get(a, Decimal("0")) + v
    # apply eliminations (each a balanced entry; debit positive, credit negative on the signed bal)
    elim_total = Decimal("0")
    for e in (eliminations or []):
        td = sum(_dec(l.get("debit", 0)) for l in e["lines"])
        tc = sum(_dec(l.get("credit", 0)) for l in e["lines"])
        if td != tc:
            raise SystemExit(f"ERROR: elimination '{e.get('memo','')}' does not balance ({td} != {tc})")
        for l in e["lines"]:
            signed = _dec(l.get("debit", 0)) - _dec(l.get("credit", 0))
            combined[l["account"]] = combined.get(l["account"], Decimal("0")) + signed
        elim_total += td
    # NON-CONTROLLING INTEREST: for a controlled sub owned < 100%, reclass the minority share
    # of the sub's net equity (equity + net income) from controlling equity to the NCI line.
    nci = []
    for b in books:
        own = _dec(ownership.get(b, 1))
        if own >= 1 or own <= 0:
            continue                                   # wholly owned (or not controlled) → no NCI
        eq, ni = _entity_equity_and_ni(L.Ledger(b).balances(as_of))
        nci_amt = ((Decimal(1) - own) * (eq + ni)).quantize(Decimal("0.01"))
        if nci_amt == 0:
            continue
        # Dr controlling equity (reduce it) / Cr NCI (its own equity line) — total equity unchanged
        combined[controlling_account] = combined.get(controlling_account, Decimal("0")) + nci_amt
        combined[nci_account] = combined.get(nci_account, Decimal("0")) - nci_amt
        nci.append({"entity": b, "ownership": str(own), "nci_share": str(nci_amt)})
    tb = S.trial_balance(combined)
    s = S.build(postings=[{"account": a, "amount": v} for a, v in combined.items()])
    return {"books": books, "eliminations": len(eliminations or []),
            "elimination_total": str(elim_total), "nci": nci,
            "per_entity": per_entity, "consolidated_balances": {a: str(v) for a, v in combined.items()},
            "trial_balance_balanced": tb["balanced"],
            "balance_sheet_balances": s["balance_sheet"]["balances"],
            "net_income": str(s["profit_loss"]["net_income"])}


def render_text(d: dict) -> str:
    o = ["=" * 60, f"CONSOLIDATION — {', '.join(d['books'])}", "-" * 60,
         f"  entities: {len(d['books'])}   eliminations: {d['eliminations']}", "-" * 60,
         f"  {'Account':<40}{'Consolidated':>18}"]
    for a, v in sorted(d["consolidated_balances"].items()):
        if _dec(v) != 0:
            o.append(f"  {a[:39]:<40}{_dec(v):>18,.2f}")
    if d.get("nci"):
        o.append("  Non-controlling interest:")
        for n in d["nci"]:
            o.append(f"     {n['entity']} (owned {Decimal(n['ownership'])*100:.0f}%) → NCI {_dec(n['nci_share']):,.2f}")
    o.append("-" * 60)
    o.append(f"  trial balance balanced: {'✓' if d['trial_balance_balanced'] else '✗'}   "
             f"BS balances: {'✓' if d['balance_sheet_balances'] else '✗'}   "
             f"net income: {_dec(d['net_income']):,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-consolidate")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("combine", help="full consolidation (default)")
    for p in (ap, c):
        p.add_argument("--books", help="comma-separated ledger book names")
        p.add_argument("--eliminate", default=None, help="eliminations JSON file")
        p.add_argument("--ownership", default=None, help="ownership JSON {book: fraction} for NCI")
        p.add_argument("--as-of", default=None)
        p.add_argument("--format", default="text", choices=["text", "json"])
    em = sub.add_parser("equity-method", help="20-50%% investee roll-forward (not consolidated)")
    em.add_argument("--cost", required=True); em.add_argument("--ownership", required=True)
    em.add_argument("--net-income", required=True, help="cumulative net income since acquisition")
    em.add_argument("--dividends", default="0", help="cumulative dividends received")
    em.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()

    if a.cmd == "equity-method":
        d = equity_method(_dec(a.cost), _dec(a.ownership), _dec(a.net_income), _dec(a.dividends))
        if a.format == "json":
            print(json.dumps(d, indent=2, default=str))
        else:
            print(f"EQUITY METHOD ({_dec(a.ownership)*100:.0f}% investee)\n"
                  f"  cost {d['cost']:,.2f} + income {d['equity_method_income']:,.2f} "
                  f"− dividends {d['dividends_received']:,.2f} = investment {d['ending_investment']:,.2f}")
        return 0

    if not a.books:
        ap.error("--books is required")
    books = [b.strip() for b in a.books.split(",") if b.strip()]
    elims = json.load(open(a.eliminate, encoding="utf-8")) if a.eliminate else None
    if isinstance(elims, dict) and "eliminations" in elims:
        elims = elims["eliminations"]
    own = json.load(open(a.ownership, encoding="utf-8")) if a.ownership else None
    d = consolidate(books, elims, as_of=a.as_of, ownership=own)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0 if d["trial_balance_balanced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

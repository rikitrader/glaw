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


def consolidate(books: list[str], eliminations: list[dict] | None = None,
                *, as_of: str | None = None) -> dict:
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
    tb = S.trial_balance(combined)
    s = S.build(postings=[{"account": a, "amount": v} for a, v in combined.items()])
    return {"books": books, "eliminations": len(eliminations or []),
            "elimination_total": str(elim_total),
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
    o.append("-" * 60)
    o.append(f"  trial balance balanced: {'✓' if d['trial_balance_balanced'] else '✗'}   "
             f"BS balances: {'✓' if d['balance_sheet_balances'] else '✗'}   "
             f"net income: {_dec(d['net_income']):,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-consolidate")
    ap.add_argument("--books", required=True, help="comma-separated ledger book names")
    ap.add_argument("--eliminate", default=None, help="eliminations JSON file")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    books = [b.strip() for b in a.books.split(",") if b.strip()]
    elims = json.load(open(a.eliminate, encoding="utf-8")) if a.eliminate else None
    if isinstance(elims, dict) and "eliminations" in elims:
        elims = elims["eliminations"]
    d = consolidate(books, elims, as_of=a.as_of)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0 if d["trial_balance_balanced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

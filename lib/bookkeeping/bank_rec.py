#!/usr/bin/env python3
"""GLAW bank reconciliation — line-match the books against the bank statement.

The Golden Rule only checks opening+net==closing. A real reconciliation matches
each cleared item between two independent transaction sets and surfaces what does
NOT match:

  matched      — same amount, dates within --window days (cleared)
  book-only    — recorded in the books, not (yet) on the bank: deposits-in-transit
                 and outstanding/unpresented checks (timing items)
  bank-only    — on the bank, not (yet) in the books: fees, interest, direct debits
                 to be recorded

unreconciled_difference = sum(book) − sum(bank).  Zero ⇒ every item is matched.

Inputs are `glaw-bank-ingest --format json` payloads (or a raw row list).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from decimal import Decimal


def _rows(payload) -> list[dict]:
    if isinstance(payload, dict) and "rows" in payload:
        return payload["rows"]
    if isinstance(payload, list):
        return payload
    raise SystemExit("ERROR: expected glaw-bank-ingest JSON ({'rows': [...]}) or a row list")


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _date(v):
    try:
        return date.fromisoformat(str(v)[:10])
    except Exception:
        return None


def _label(r: dict) -> str:
    d = (str(r.get("booking_date"))[:10]) if r.get("booking_date") else "????-??-??"
    return f"{d}  {_dec(r.get('amount')):>12,.2f}  {(r.get('description') or '')[:40]}"


def reconcile(books: list[dict], bank: list[dict], *, window_days: int = 5) -> dict:
    # index bank rows; greedy match by exact amount within the date window
    bank_items = [{"r": b, "amt": _dec(b.get("amount")), "d": _date(b.get("booking_date")),
                   "used": False} for b in bank]
    matched = 0
    book_only: list[dict] = []
    for bk in books:
        amt = _dec(bk.get("amount"))
        d = _date(bk.get("booking_date"))
        hit = None
        for it in bank_items:
            if it["used"] or it["amt"] != amt:
                continue
            if d is not None and it["d"] is not None and abs((d - it["d"]).days) > window_days:
                continue
            hit = it
            break
        if hit is not None:
            hit["used"] = True
            matched += 1
        else:
            book_only.append(bk)
    bank_only = [it["r"] for it in bank_items if not it["used"]]

    sum_book = sum((_dec(b.get("amount")) for b in books), Decimal("0"))
    sum_bank = sum((_dec(b.get("amount")) for b in bank), Decimal("0"))
    return {
        "matched": matched,
        "book_only": book_only,
        "bank_only": bank_only,
        "sum_book": sum_book,
        "sum_bank": sum_bank,
        "unreconciled_difference": sum_book - sum_bank,
        "reconciled": (sum_book - sum_bank) == 0 and not book_only and not bank_only,
    }


def render_text(rc: dict) -> str:
    o: list[str] = []
    o.append("=" * 64)
    o.append("BANK RECONCILIATION")
    o.append("-" * 64)
    o.append(f"  matched (cleared):        {rc['matched']}")
    o.append(f"  book total:               {rc['sum_book']:>14,.2f}")
    o.append(f"  bank total:               {rc['sum_bank']:>14,.2f}")
    o.append(f"  unreconciled difference:  {rc['unreconciled_difference']:>14,.2f}")
    if rc["book_only"]:
        o.append("")
        o.append(f"  BOOK-ONLY ({len(rc['book_only'])}) — in books, not on bank (deposits in transit / outstanding):")
        for r in rc["book_only"]:
            o.append(f"    {_label(r)}")
    if rc["bank_only"]:
        o.append("")
        o.append(f"  BANK-ONLY ({len(rc['bank_only'])}) — on bank, not in books (fees / interest / to record):")
        for r in rc["bank_only"]:
            o.append(f"    {_label(r)}")
    o.append("-" * 64)
    o.append("  RECONCILED ✓" if rc["reconciled"]
             else f"  NOT RECONCILED — {len(rc['book_only'])} book-only, {len(rc['bank_only'])} bank-only")
    o.append("=" * 64)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-bank-rec")
    ap.add_argument("--books", required=True, help="books ledger JSON (glaw-bank-ingest --format json)")
    ap.add_argument("--bank", required=True, help="bank statement JSON (glaw-bank-ingest --format json)")
    ap.add_argument("--window", type=int, default=5, help="date-match window in days (default 5)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    books = _rows(json.load(open(a.books, encoding="utf-8")))
    bank = _rows(json.load(open(a.bank, encoding="utf-8")))
    rc = reconcile(books, bank, window_days=a.window)
    if a.format == "json":
        print(json.dumps(rc, indent=2, default=str))
    else:
        print(render_text(rc))
    return 0 if rc["reconciled"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GLAW cash application — match incoming receipts to open AR invoices.

Closes the AR loop: a payment comes in, this matches it to the customer's open invoices
(by explicit invoice ref, else oldest-first), and reports what is fully paid, partially
paid, still open, and any unapplied cash / overpayment.

Input JSON:
  {"invoices": [{"id":"INV-1","party":"Acme","amount":1000,"date":"2026-01-05"}, ...],
   "receipts": [{"party":"Acme","amount":1000,"date":"2026-02-01","apply_to":"INV-1"?}, ...]}
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def apply_cash(invoices: list[dict], receipts: list[dict]) -> dict:
    inv = [{"id": i.get("id"), "party": i.get("party"), "open": _dec(i.get("amount")),
            "amount": _dec(i.get("amount")), "date": i.get("date")} for i in invoices]
    by_id = {i["id"]: i for i in inv if i["id"]}
    applications, unapplied = [], Decimal("0")
    for r in receipts:
        party, amt = r.get("party"), _dec(r.get("amount"))
        target = by_id.get(r.get("apply_to")) if r.get("apply_to") else None
        # candidate invoices: explicit target, else this party's open invoices oldest-first
        queue = [target] if target else sorted(
            [i for i in inv if i["party"] == party and i["open"] > 0],
            key=lambda x: str(x["date"]))
        for i in queue:
            if amt <= 0:
                break
            if i is None or i["open"] <= 0:
                continue
            pay = min(amt, i["open"])
            i["open"] -= pay
            amt -= pay
            applications.append({"receipt_party": party, "invoice": i["id"],
                                 "applied": str(pay), "invoice_remaining": str(i["open"])})
        if amt > 0:
            unapplied += amt                          # overpayment / no matching invoice
    open_items = [{"id": i["id"], "party": i["party"], "amount": str(i["amount"]),
                   "remaining": str(i["open"]),
                   "status": "paid" if i["open"] == 0 else ("partial" if i["open"] < i["amount"] else "open")}
                  for i in inv]
    total_open = sum(i["open"] for i in inv)
    return {"applications": applications, "open_items": open_items,
            "unapplied_cash": str(unapplied), "total_still_open": str(total_open),
            "fully_applied": unapplied == 0}


def render_text(d: dict) -> str:
    o = ["=" * 60, "CASH APPLICATION", "-" * 60, "  applications:"]
    for a in d["applications"]:
        o.append(f"    {a['receipt_party']:<16} → {a['invoice']:<10} applied {_dec(a['applied']):>12,.2f}"
                 f"  (inv remaining {_dec(a['invoice_remaining']):,.2f})")
    o.append("  open items:")
    for i in d["open_items"]:
        o.append(f"    {i['id']:<10} {i['party']:<16} {i['status']:<8} remaining {_dec(i['remaining']):>12,.2f}")
    o.append("-" * 60)
    o.append(f"  total still open: {_dec(d['total_still_open']):,.2f}   unapplied cash: {_dec(d['unapplied_cash']):,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-cash-apply")
    ap.add_argument("json", nargs="?", default="-", help="invoices+receipts JSON (or '-')")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.json in (None, "-") else open(a.json, encoding="utf-8").read()
    d = json.loads(raw)
    res = apply_cash(d.get("invoices", []), d.get("receipts", []))
    print(json.dumps(res, indent=2, default=str) if a.format == "json" else render_text(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

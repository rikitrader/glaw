#!/usr/bin/env python3
"""GLAW AR/AP aging — bucket open invoices/bills by age.

Input: JSON list of open items, each {party, amount, date} (date = invoice or due
date, ISO). Buckets relative to --as-of: Current 0-30, 31-60, 61-90, 90+. Reports
totals per bucket and per party. Deterministic; no network.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from decimal import Decimal

BUCKETS = ["Current (0-30)", "31-60", "61-90", "90+"]


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _bucket(days: int) -> str:
    if days <= 30:
        return BUCKETS[0]
    if days <= 60:
        return BUCKETS[1]
    if days <= 90:
        return BUCKETS[2]
    return BUCKETS[3]


def age(items: list[dict], as_of: date) -> dict:
    by_bucket = {b: Decimal("0") for b in BUCKETS}
    by_party: dict[str, dict] = {}
    total = Decimal("0")
    for it in items:
        amt = _dec(it.get("amount"))
        try:
            d = date.fromisoformat(str(it.get("date"))[:10])
            days = (as_of - d).days
        except Exception:
            days = 0
        b = _bucket(max(days, 0))
        party = it.get("party") or "(unknown)"
        by_bucket[b] += amt
        total += amt
        p = by_party.setdefault(party, {bk: Decimal("0") for bk in BUCKETS} | {"total": Decimal("0")})
        p[b] += amt
        p["total"] += amt
    return {"as_of": as_of.isoformat(), "by_bucket": by_bucket, "by_party": by_party,
            "total": total, "overdue": by_bucket[BUCKETS[1]] + by_bucket[BUCKETS[2]] + by_bucket[BUCKETS[3]]}


def render_text(a: dict) -> str:
    o = ["=" * 78, f"AGING  (as of {a['as_of']})", "-" * 78,
         f"  {'Party':<26}" + "".join(f"{b:>13}" for b in BUCKETS) + f"{'Total':>13}", "-" * 78]
    for party, p in sorted(a["by_party"].items(), key=lambda kv: -kv[1]["total"]):
        o.append(f"  {party[:25]:<26}" + "".join(f"{p[b]:>13,.2f}" for b in BUCKETS)
                 + f"{p['total']:>13,.2f}")
    o.append("-" * 78)
    o.append(f"  {'TOTAL':<26}" + "".join(f"{a['by_bucket'][b]:>13,.2f}" for b in BUCKETS)
             + f"{a['total']:>13,.2f}")
    o.append(f"  overdue (31+ days): {a['overdue']:,.2f}")
    o.append("=" * 78)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-aging")
    ap.add_argument("items", nargs="?", default="-", help="open-items JSON [{party,amount,date}] (or '-')")
    ap.add_argument("--as-of", required=True, help="aging date YYYY-MM-DD")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.items in (None, "-") else open(a.items, encoding="utf-8").read()
    items = json.loads(raw)
    if isinstance(items, dict) and "items" in items:
        items = items["items"]
    res = age(items, date.fromisoformat(a.as_of))
    print(json.dumps(res, indent=2, default=str) if a.format == "json" else render_text(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

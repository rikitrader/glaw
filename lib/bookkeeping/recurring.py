#!/usr/bin/env python3
"""GLAW recurring entries — standard period-end journal entries from templates.

Many adjusting entries repeat every period unchanged: rent accrual, insurance/prepaid
amortization, depreciation, deferred-revenue release. Define them once as templates;
this stamps them with a date and either prints the balanced entries or posts them to a
ledger book. Each template must balance (debits == credits), validated before posting.

Templates JSON:
  {"templates": [
     {"name": "rent accrual", "source": "recurring",
      "lines": [{"account": "Expenses:Rent", "debit": 5000},
                {"account": "Liabilities:Accrued Rent", "credit": 5000}]}, ... ]}
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def build_entries(templates: list[dict], date: str) -> list[dict]:
    out = []
    for t in templates:
        lines = t.get("lines", [])
        td = sum(_dec(l.get("debit", 0)) for l in lines)
        tc = sum(_dec(l.get("credit", 0)) for l in lines)
        if td != tc:
            raise SystemExit(f"ERROR: template '{t.get('name','?')}' does not balance ({td} != {tc})")
        out.append({"date": date, "memo": t.get("name", "recurring"),
                    "source": t.get("source", "recurring"), "lines": lines})
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-recurring")
    ap.add_argument("templates", nargs="?", default="-", help="templates JSON (or '-')")
    ap.add_argument("--date", required=True, help="posting date YYYY-MM-DD")
    ap.add_argument("--book", default=None, help="post to this ledger book (else just print entries)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.templates in (None, "-") else open(a.templates, encoding="utf-8").read()
    payload = json.loads(raw)
    templates = payload["templates"] if isinstance(payload, dict) and "templates" in payload else payload
    entries = build_entries(templates, a.date)
    if a.book:
        import ledger as L
        led = L.Ledger(a.book)
        posted = [led.post(e) for e in entries]
        if a.format == "json":
            print(json.dumps(posted, indent=2, default=str))
        else:
            for e, r in zip(entries, posted):
                print(f"posted #{r.get('id')}  {a.date}  {e['memo']}")
        return 0
    if a.format == "json":
        print(json.dumps(entries, indent=2, default=str))
    else:
        for e in entries:
            print(f"{e['date']}  {e['memo']}: " +
                  ", ".join(f"{l['account']} {'Dr' if _dec(l.get('debit',0)) else 'Cr'} "
                            f"{_dec(l.get('debit',0)) or _dec(l.get('credit',0)):,.2f}" for l in e["lines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

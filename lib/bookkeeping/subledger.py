#!/usr/bin/env python3
"""GLAW subledgers — registered schedules that auto-post their period entry to the ledger.

The calc tools produce schedules; the controller posts each period by hand. A subledger
registers a schedule once and posts the due entry automatically each close:

  fixed-asset       book depreciation, straight-line monthly (Dr Depreciation / Cr Accum Dep)
  deferred-revenue  ratable release monthly (Dr Deferred Revenue / Cr Revenue)
  loan              amortizing payment monthly (Dr Interest + Dr Loan Payable / Cr Cash)

`post --through <YYYY-MM>` posts every entry dated on/before that month-end that hasn't
posted yet, advancing each item's high-water mark. Idempotent: re-running posts nothing new.
Stored at $GLAW_HOME/books/<book>/subledgers.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import ledger as L          # noqa: E402
import amortize as AMORT    # noqa: E402

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _month_end(year: int, month: int) -> str:
    return date(year, month, monthrange(year, month)[1]).isoformat()


def _months_from(start: str, i: int) -> str:
    y, m = (int(x) for x in start.split("-")[:2])
    m0 = (m - 1) + i
    return _month_end(y + m0 // 12, (m0 % 12) + 1)


def _store_path(book: str) -> Path:
    return L.Ledger(book).dir / "subledgers.json"


def _load(book: str) -> list[dict]:
    p = _store_path(book)
    return json.loads(p.read_text()) if p.exists() else []


def _save(book: str, items: list[dict]) -> None:
    p = _store_path(book)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(items, indent=2, default=str))


def _add(book: str, item: dict) -> dict:
    items = _load(book)
    item["id"] = (max((i["id"] for i in items), default=0) + 1)
    item["posted_through_period"] = 0
    items.append(item)
    _save(book, items)
    return item


def register_asset(book: str, name: str, cost: Decimal, life_years: int, *,
                   salvage: Decimal = Decimal("0"), start: str,
                   exp_acct="Expenses:Depreciation", accum="Assets:Accumulated Depreciation") -> dict:
    n = life_years * 12
    monthly = _q((cost - salvage) / n)
    entries, accum_amt = [], Decimal("0")
    for i in range(1, n + 1):
        amt = monthly if i < n else (cost - salvage - accum_amt)
        accum_amt += amt
        entries.append({"period": i, "date": _months_from(start, i - 1),
                        "memo": f"Depreciation — {name}",
                        "lines": [{"account": exp_acct, "debit": str(_q(amt)), "credit": "0"},
                                  {"account": accum, "debit": "0", "credit": str(_q(amt))}]})
    return _add(book, {"type": "fixed-asset", "name": name, "cost": str(_q(cost)),
                       "life_years": life_years, "entries": entries})


def register_deferred(book: str, name: str, amount: Decimal, periods: int, *, start: str,
                      deferred="Liabilities:Deferred Revenue", revenue="Income:Revenue") -> dict:
    monthly = _q(amount / periods)
    entries, rec = [], Decimal("0")
    for i in range(1, periods + 1):
        amt = monthly if i < periods else (amount - rec)
        rec += amt
        entries.append({"period": i, "date": _months_from(start, i - 1),
                        "memo": f"Revenue recognition — {name}",
                        "lines": [{"account": deferred, "debit": str(_q(amt)), "credit": "0"},
                                  {"account": revenue, "debit": "0", "credit": str(_q(amt))}]})
    return _add(book, {"type": "deferred-revenue", "name": name, "amount": str(_q(amount)),
                       "periods": periods, "entries": entries})


def register_loan(book: str, name: str, principal: Decimal, rate_pct: Decimal, payments: int, *,
                  start: str, interest="Expenses:Interest", loan_acct="Liabilities:Loan",
                  cash="Assets:Bank:Checking") -> dict:
    sched = AMORT.loan_schedule(principal, rate_pct, payments)
    entries = []
    for r in sched["schedule"]:
        i = r["period"]
        entries.append({"period": i, "date": _months_from(start, i - 1),
                        "memo": f"Loan payment — {name}",
                        "lines": [{"account": interest, "debit": str(r["interest"]), "credit": "0"},
                                  {"account": loan_acct, "debit": str(r["principal"]), "credit": "0"},
                                  {"account": cash, "debit": "0", "credit": str(r["payment"])}]})
    return _add(book, {"type": "loan", "name": name, "principal": str(_q(principal)),
                       "payments": payments, "entries": entries})


def post_due(book: str, through: str) -> dict:
    """Post every subledger entry dated on/before `through` (a date or YYYY-MM) not yet posted."""
    if len(through) == 7:
        y, m = (int(x) for x in through.split("-"))
        through = _month_end(y, m)
    cutoff = date.fromisoformat(through)
    led = L.Ledger(book)
    items = _load(book)
    posted, detail = 0, []
    for it in items:
        hwm = it.get("posted_through_period", 0)
        for e in it["entries"]:
            if e["period"] <= hwm:
                continue
            if date.fromisoformat(e["date"]) > cutoff:
                break
            led.post({"date": e["date"], "memo": e["memo"], "source": f"subledger:{it['type']}",
                      "lines": e["lines"]})
            it["posted_through_period"] = e["period"]
            posted += 1
            detail.append({"item": it["name"], "period": e["period"], "date": e["date"]})
    _save(book, items)
    return {"book": book, "through": through, "posted": posted, "detail": detail}


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-subledger")
    ap.add_argument("--book", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add-asset")
    p.add_argument("--name", required=True); p.add_argument("--cost", required=True)
    p.add_argument("--life", type=int, required=True, help="useful life in years")
    p.add_argument("--salvage", default="0"); p.add_argument("--start", required=True, help="YYYY-MM")
    p = sub.add_parser("add-deferred")
    p.add_argument("--name", required=True); p.add_argument("--amount", required=True)
    p.add_argument("--periods", type=int, required=True); p.add_argument("--start", required=True)
    p = sub.add_parser("add-loan")
    p.add_argument("--name", required=True); p.add_argument("--principal", required=True)
    p.add_argument("--rate", required=True); p.add_argument("--payments", type=int, required=True)
    p.add_argument("--start", required=True)
    p = sub.add_parser("post"); p.add_argument("--through", required=True, help="YYYY-MM or date")
    sub.add_parser("list")
    a = ap.parse_args()

    if a.cmd == "add-asset":
        it = register_asset(a.book, a.name, Decimal(a.cost), a.life, salvage=Decimal(a.salvage), start=a.start)
        print(f"registered fixed-asset #{it['id']} '{a.name}' — {len(it['entries'])} monthly entries")
    elif a.cmd == "add-deferred":
        it = register_deferred(a.book, a.name, Decimal(a.amount), a.periods, start=a.start)
        print(f"registered deferred-revenue #{it['id']} '{a.name}' — {len(it['entries'])} monthly entries")
    elif a.cmd == "add-loan":
        it = register_loan(a.book, a.name, Decimal(a.principal), Decimal(a.rate), a.payments, start=a.start)
        print(f"registered loan #{it['id']} '{a.name}' — {len(it['entries'])} monthly entries")
    elif a.cmd == "post":
        r = post_due(a.book, a.through)
        print(f"posted {r['posted']} subledger entries through {r['through']}")
        for d in r["detail"]:
            print(f"  {d['date']}  {d['item']} (period {d['period']})")
    elif a.cmd == "list":
        for it in _load(a.book):
            print(f"  #{it['id']} {it['type']:<16} {it['name']:<24} "
                  f"posted {it['posted_through_period']}/{len(it['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

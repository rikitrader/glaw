"""GLAW ledger monitor — continuous transaction anomaly / fraud scan.

Watches a ledger (`glaw-bank-ingest --format json`) and flags deterministic risk
patterns every period:
  - duplicate payment   same amount + payee on different dates (possible double-pay)
  - round-dollar        exact thousand-dollar outflow >= threshold
  - weekend entry       booking date on Saturday/Sunday
  - lone large payment  a payee seen once with a large outflow (new-vendor risk)

Informational by default (exit 0); --strict exits non-zero if anything is flagged.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _payee(r: dict) -> str:
    return (r.get("counterparty") or r.get("normalized_description")
            or r.get("description") or "").strip().upper()


def scan(rows: list[dict], *, round_threshold: Decimal = Decimal("5000"),
         lone_threshold: Decimal = Decimal("10000")) -> dict:
    flags: list[dict] = []
    payee_count: dict[str, int] = defaultdict(int)
    for r in rows:
        payee_count[_payee(r)] += 1

    seen: dict[tuple, list] = defaultdict(list)
    for r in rows:
        amt = _dec(r.get("amount"))
        payee = _payee(r)
        d = str(r.get("booking_date") or "")[:10]
        # duplicate payment: same |amount| + payee, different date
        key = (abs(amt), payee)
        seen[key].append(d)
        # round-dollar outflow
        if amt < 0 and abs(amt) >= round_threshold and (abs(amt) % Decimal("1000") == 0):
            flags.append({"reason": "round-dollar", "date": d, "amount": str(amt), "payee": payee})
        # weekend entry
        try:
            if date.fromisoformat(d).weekday() >= 5:
                flags.append({"reason": "weekend-entry", "date": d, "amount": str(amt), "payee": payee})
        except Exception:
            pass
        # lone large payment (new-vendor risk)
        if amt < 0 and abs(amt) >= lone_threshold and payee and payee_count[payee] == 1:
            flags.append({"reason": "lone-large-payment", "date": d, "amount": str(amt), "payee": payee})
    for (amt, payee), dates in seen.items():
        if payee and len(dates) > 1 and len(set(dates)) > 1:
            flags.append({"reason": "duplicate-payment", "amount": str(amt),
                          "payee": payee, "dates": sorted(set(dates))})
    # stable order
    flags.sort(key=lambda f: (f["reason"], f.get("date", ""), f.get("payee", "")))
    return {"transactions": len(rows), "flag_count": len(flags), "flags": flags,
            "clean": len(flags) == 0}


def render_text(s: dict) -> str:
    o = ["=" * 70, "LEDGER MONITOR — anomaly scan", "-" * 70,
         f"  transactions: {s['transactions']}   flags: {s['flag_count']}", "-" * 70]
    if s["clean"]:
        o.append("  ✅ no anomalies flagged")
    for f in s["flags"]:
        if f["reason"] == "duplicate-payment":
            o.append(f"  ⚠️  duplicate-payment   {f['amount']:>12}  {f['payee'][:30]:<30}  {','.join(f['dates'])}")
        else:
            o.append(f"  ⚠️  {f['reason']:<20}{f['amount']:>12}  {f['payee'][:30]:<30}  {f.get('date','')}")
    o.append("=" * 70)
    return "\n".join(o)


def _rows(payload) -> list[dict]:
    if isinstance(payload, dict) and "rows" in payload:
        return payload["rows"]
    if isinstance(payload, list):
        return payload
    raise SystemExit("ERROR: expected glaw-bank-ingest JSON ({'rows': [...]})")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-ledger-monitor")
    ap.add_argument("json", nargs="?", default="-", help="glaw-bank-ingest --format json (or '-')")
    ap.add_argument("--round-threshold", default="5000")
    ap.add_argument("--lone-threshold", default="10000")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if anything is flagged")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.json in (None, "-") else open(a.json, encoding="utf-8").read()
    s = scan(_rows(json.loads(raw)), round_threshold=Decimal(a.round_threshold),
             lone_threshold=Decimal(a.lone_threshold))
    print(json.dumps(s, indent=2, default=str) if a.format == "json" else render_text(s))
    return 1 if (a.strict and not s["clean"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())

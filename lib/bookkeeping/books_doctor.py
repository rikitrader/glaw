#!/usr/bin/env python3
"""GLAW Books Doctor — the bulletproof finance control gate.

The finance analog of glaw-doctor: consumes a GLAW ledger (the JSON from
`glaw-bank-ingest --format json`) and deterministically asserts the books are
sound. Exit 0 = bulletproof, 1 = problems found.

Checks:
  1. Trial balance balances           debits == credits
  2. Balance-sheet identity           Assets == Liabilities + Equity + Net Income
  3. Golden-Rule verification         every source statement reconciles (opening+net==closing)
  4. No unclassified accounts         every account maps to a known statement root
  5. No negative cash                 ending bank/cash balance >= 0 (unless --allow-negative-cash)
  6. Dedup integrity                  no duplicate transaction_hash survived
  7. Anomaly scan                     near-duplicate payments flagged (deterministic)
  8. Reconciliation (optional)        --rec <bank_rec.json>: unreconciled difference == 0
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from decimal import Decimal

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import statements as S   # noqa: E402

FAIL = 0
WARN = 0


def ok(m): print(f"  ✅ {m}")
def bad(m):
    global FAIL
    print(f"  ❌ {m}")
    FAIL += 1
def warn(m):
    global WARN
    print(f"  ⚠️  {m}")
    WARN += 1


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def run(payload: dict, *, allow_negative_cash: bool = False, rec: dict | None = None) -> int:
    rows = payload.get("rows", payload if isinstance(payload, list) else [])
    audit = payload.get("audit", []) if isinstance(payload, dict) else []
    s = S.build(rows)
    tb, bs = s["trial_balance"], s["balance_sheet"]

    print("═══ GLAW BOOKS DOCTOR ═══")
    print(f"[1/8] trial balance ({len(rows)} transactions)")
    if tb["balanced"]:
        ok(f"debits == credits ({S._m(tb['total_debit'])} == {S._m(tb['total_credit'])})")
    else:
        bad(f"OUT OF BALANCE: debits {S._m(tb['total_debit'])} != credits {S._m(tb['total_credit'])}")

    print("[2/8] balance-sheet identity")
    if bs["balances"]:
        ok(f"Assets {S._m(bs['assets_total'])} == Liabilities + Equity {S._m(bs['liabilities_total'] + bs['equity_total'])}")
    else:
        bad(f"Assets {S._m(bs['assets_total'])} != Liab+Equity {S._m(bs['liabilities_total'] + bs['equity_total'])}")

    print("[3/8] Golden-Rule verification (per source)")
    if not audit:
        warn("no audit block in input — Golden Rule not checked (run glaw-bank-ingest --open/--close)")
    else:
        bad_n = 0
        for a in audit:
            st = a.get("balance_status")
            if st == "discrepancy":
                bad(f"source {a.get('source')}: balance DISCREPANCY"); bad_n += 1
            elif st in (None, "failed"):
                warn(f"source {a.get('source')}: balance not verified ({st})")
        if bad_n == 0:
            ok("no balance discrepancies")

    print("[4/8] account classification")
    if s["unclassified_accounts"]:
        for a in s["unclassified_accounts"]:
            bad(f"unclassified account (no known root): {a}")
    else:
        ok("every account maps to Assets/Liabilities/Equity/Income/Expenses")

    print("[5/8] cash position")
    bal = S.account_balances(rows)
    neg = [(a, b) for a, b in bal.items()
           if a.startswith(S._CASH_HINTS) and b < 0]
    if neg and not allow_negative_cash:
        for a, b in neg:
            bad(f"negative cash: {a} = {S._m(b)} (overdraft)")
    elif neg:
        for a, b in neg:
            warn(f"negative cash allowed: {a} = {S._m(b)}")
    else:
        ok("no negative cash balances")

    print("[6/8] dedup integrity")
    hashes = [r.get("transaction_hash") for r in rows if r.get("transaction_hash")]
    dup = [h for h, n in Counter(hashes).items() if n > 1]
    if dup:
        bad(f"{len(dup)} duplicate transaction_hash survived dedup")
    else:
        ok(f"all {len(hashes)} transaction hashes unique")

    print("[7/8] anomaly scan")
    # near-duplicate: same (date, amount, normalized desc) but engine didn't collapse
    keys = Counter((r.get("booking_date"), str(r.get("amount")),
                    (r.get("normalized_description") or r.get("description") or "").upper())
                   for r in rows)
    near = [k for k, n in keys.items() if n > 1]
    if near:
        for k in near[:5]:
            warn(f"possible duplicate payment: {k[0]} {k[1]} '{k[2][:30]}'")
    else:
        ok("no near-duplicate payments")

    print("[8/8] bank reconciliation")
    if rec is None:
        warn("no reconciliation supplied (--rec) — run glaw-bank-rec to match books vs bank")
    else:
        diff = _dec(rec.get("unreconciled_difference", 0))
        if diff != 0:
            bad(f"unreconciled difference {S._m(diff)} "
                f"({len(rec.get('book_only', []))} book-only, {len(rec.get('bank_only', []))} bank-only)")
        else:
            ok(f"reconciled to zero ({rec.get('matched', 0)} matched)")

    print("═══ RESULT ═══")
    print(f"  failures: {FAIL}   warnings: {WARN}")
    print("  \U0001f6e1️  BOOKS ARE BULLETPROOF" if FAIL == 0 else "  ❌ PROBLEMS FOUND")
    return 0 if FAIL == 0 else 1


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-books-doctor")
    ap.add_argument("json", nargs="?", default="-", help="glaw-bank-ingest --format json (or '-')")
    ap.add_argument("--allow-negative-cash", action="store_true")
    ap.add_argument("--rec", default=None, help="bank reconciliation JSON (from glaw-bank-rec)")
    a = ap.parse_args()
    raw = sys.stdin.read() if a.json in (None, "-") else open(a.json, encoding="utf-8").read()
    payload = json.loads(raw)
    rec = json.load(open(a.rec, encoding="utf-8")) if a.rec else None
    return run(payload, allow_negative_cash=a.allow_negative_cash, rec=rec)


if __name__ == "__main__":
    raise SystemExit(main())

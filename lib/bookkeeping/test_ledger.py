#!/usr/bin/env python3
"""Tests for the GLAW general ledger — the book of record. Uses a temp GLAW_HOME so
it never touches real books. Proves the accounting is correct, not just that it runs."""
from __future__ import annotations

import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    import os
    d = tempfile.mkdtemp(prefix="glaw-gl-")
    os.environ["GLAW_HOME"] = d
    import importlib
    import ledger as L
    importlib.reload(L)
    return L, d


def test_balanced_enforcement():
    L, _ = _fresh()
    led = L.Ledger("t")
    # balanced entry posts
    r = led.post({"date": "2026-01-31", "memo": "rent",
                  "lines": [{"account": "Expenses:Rent", "debit": 2000},
                            {"account": "Assets:Bank:Checking", "credit": 2000}]})
    assert r["id"] == 1 and "entry_hash" in r
    # unbalanced entry is rejected
    try:
        led.post({"date": "2026-01-31", "lines": [{"account": "Expenses:Rent", "debit": 2000},
                                                  {"account": "Assets:Bank:Checking", "credit": 1500}]})
        raise AssertionError("unbalanced entry must be rejected")
    except L.LedgerError as e:
        assert "does not balance" in str(e)
    # single-leg rejected
    try:
        led.post({"date": "2026-01-31", "lines": [{"account": "Expenses:Rent", "debit": 100}]})
        raise AssertionError("one-line entry must be rejected")
    except L.LedgerError:
        pass
    print("  ✓ ledger: balanced double-entry enforced (unbalanced + single-leg rejected)")


def test_noncash_je_and_balances():
    L, _ = _fresh()
    led = L.Ledger("t")
    # the entry the OLD model could NOT express: non-cash depreciation (no bank leg)
    led.post({"date": "2026-01-31", "memo": "Jan depreciation", "source": "fixed-assets",
              "lines": [{"account": "Expenses:Depreciation", "debit": 1000},
                        {"account": "Assets:Accumulated Depreciation", "credit": 1000}]})
    bal = led.balances()
    assert bal["Expenses:Depreciation"] == Decimal("1000")
    assert bal["Assets:Accumulated Depreciation"] == Decimal("-1000")
    # trial balance: signed sum of ALL accounts is exactly zero (debits==credits)
    assert sum(bal.values()) == 0
    print("  ✓ ledger: posts non-cash adjusting entries (depreciation); TB sums to 0")


def test_as_of_and_gl():
    L, _ = _fresh()
    led = L.Ledger("t")
    led.post({"date": "2026-01-10", "lines": [{"account": "Assets:Bank:Checking", "debit": 500},
                                              {"account": "Income:Sales", "credit": 500}]})
    led.post({"date": "2026-02-10", "lines": [{"account": "Assets:Bank:Checking", "debit": 300},
                                              {"account": "Income:Sales", "credit": 300}]})
    assert led.balances("2026-01-31")["Assets:Bank:Checking"] == Decimal("500")  # as-of excludes Feb
    assert led.balances("2026-02-28")["Assets:Bank:Checking"] == Decimal("800")
    gl = led.gl("Assets:Bank:Checking")
    assert [r["balance"] for r in gl["rows"]] == [Decimal("500"), Decimal("800")]  # running balance
    assert gl["ending_balance"] == Decimal("800")
    print("  ✓ ledger: as-of balances + GL running balance")


def test_period_lock():
    L, _ = _fresh()
    led = L.Ledger("t")
    led.post({"date": "2026-01-15", "lines": [{"account": "Assets:Bank:Checking", "debit": 100},
                                              {"account": "Income:Sales", "credit": 100}]})
    led.lock("2026-01-31")
    try:
        led.post({"date": "2026-01-20", "lines": [{"account": "Assets:Bank:Checking", "debit": 50},
                                                  {"account": "Income:Sales", "credit": 50}]})
        raise AssertionError("posting into a locked period must be rejected")
    except L.LedgerError as e:
        assert "locked" in str(e)
    # open period still posts
    r = led.post({"date": "2026-02-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 50},
                                                  {"account": "Income:Sales", "credit": 50}]})
    assert r["id"] >= 2
    print("  ✓ ledger: locked period rejects back-dated entries, open period accepts")


def test_bank_import_dedupe():
    L, _ = _fresh()
    led = L.Ledger("t")
    rows = [{"booking_date": "2026-01-04", "amount": "500", "category": "Income:Sales",
             "transaction_hash": "h1", "description": "sale"},
            {"booking_date": "2026-01-05", "amount": "-200", "category": "Expenses:Fuel",
             "transaction_hash": "h2", "description": "fuel"}]
    r1 = led.import_bank(rows)
    assert r1["posted"] == 2
    r2 = led.import_bank(rows)   # re-import same → all dedup
    assert r2["posted"] == 0 and r2["skipped_duplicates"] == 2
    bal = led.balances()
    assert bal["Assets:Bank:Checking"] == Decimal("300")  # 500 - 200
    assert sum(bal.values()) == 0
    print("  ✓ ledger: bank import posts balanced JEs, idempotent (dedupe by hash)")


def test_year_end_close():
    L, _ = _fresh()
    led = L.Ledger("t")
    # revenue 1000, expense 300 in 2026 → net income 700 closes to retained earnings
    led.post({"date": "2026-06-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 1000},
                                              {"account": "Income:Sales", "credit": 1000}]})
    led.post({"date": "2026-06-15", "lines": [{"account": "Expenses:Rent", "debit": 300},
                                              {"account": "Assets:Bank:Checking", "credit": 300}]})
    res = led.close_year(2026)
    assert res["closed"] and res["net_income"] == Decimal("700"), res
    # after close: income & expense are zero; retained earnings holds 700 (credit balance)
    bal = led.balances()
    assert bal.get("Income:Sales", Decimal("0")) == 0
    assert bal.get("Expenses:Rent", Decimal("0")) == 0
    assert bal["Equity:RetainedEarnings"] == Decimal("-700")  # credit-normal
    assert sum(bal.values()) == 0  # still balanced
    # idempotency: re-closing the same year must NOT double-close (it would crash before the fix)
    res2 = led.close_year(2026)
    assert res2["closed"] is False, "re-closing an already-closed year must be a no-op, not a crash"
    assert bal == led.balances(), "second close must not change the books"
    print("  ✓ ledger: year-end close zeroes I/E → 700 to Retained Earnings; re-close is a safe no-op")


def test_statements_from_ledger():
    import statements as S
    L, _ = _fresh()
    led = L.Ledger("t")
    led.post({"date": "2026-01-04", "lines": [{"account": "Assets:Bank:Checking", "debit": 500000},
                                              {"account": "Equity:LP:Contributions", "credit": 500000}]})
    led.post({"date": "2026-01-22", "lines": [{"account": "Expenses:Legal", "debit": 8400},
                                              {"account": "Assets:Bank:Checking", "credit": 8400}]})
    s = S.build(postings=[{"account": p["account"], "amount": p["amount"]} for p in led.postings()])
    assert s["trial_balance"]["balanced"] and s["balance_sheet"]["balances"]
    print("  ✓ statements compute from the posted ledger (TB + BS balance)")


def main() -> int:
    test_balanced_enforcement()
    test_noncash_je_and_balances()
    test_as_of_and_gl()
    test_period_lock()
    test_bank_import_dedupe()
    test_year_end_close()
    test_statements_from_ledger()
    print("OK: general ledger tests passed (balanced JEs, non-cash entries, as-of, "
          "period lock, bank import, year-end close, statements-from-ledger)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

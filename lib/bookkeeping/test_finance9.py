#!/usr/bin/env python3
"""Smoke test for subledger auto-posting. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-sub-")
    import importlib
    import ledger as L
    importlib.reload(L)
    import subledger as SUB
    importlib.reload(SUB)
    return L, SUB


def test_register_and_post():
    L, SUB = _fresh()
    SUB.register_asset("co", "Truck", Decimal("36000"), 3, start="2026-01")       # 1,000/mo
    SUB.register_deferred("co", "SaaS", Decimal("12000"), 12, start="2026-01")    # 1,000/mo
    r = SUB.post_due("co", "2026-03")
    assert r["posted"] == 6, r["posted"]                                          # 3 depr + 3 rev
    bal = L.Ledger("co").balances()
    assert bal["Expenses:Depreciation"] == Decimal("3000")
    assert bal["Assets:Accumulated Depreciation"] == Decimal("-3000")
    assert bal["Income:Revenue"] == Decimal("-3000")                             # credit (recognized)
    assert bal["Liabilities:Deferred Revenue"] == Decimal("3000")               # debit (released)
    # idempotent
    assert SUB.post_due("co", "2026-03")["posted"] == 0
    # advance to year end: 9 more depr + 9 more rev
    r2 = SUB.post_due("co", "2026-12")
    assert r2["posted"] == 18, r2["posted"]
    bal2 = L.Ledger("co").balances()
    assert bal2["Expenses:Depreciation"] == Decimal("12000")                    # 12 months
    assert bal2["Income:Revenue"] == Decimal("-12000")                         # fully recognized
    assert sum(bal2.values()) == 0                                              # books stay balanced
    print("  ✓ subledger: 6 posted through Mar (idempotent), 18 more through Dec, books balanced")


def test_loan_amortization_posts():
    L, SUB = _fresh()
    # book the loan proceeds first (Dr Cash / Cr Loan); the subledger amortizes that liability
    L.Ledger("co").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 12000},
                                                         {"account": "Liabilities:Loan", "credit": 12000}]})
    SUB.register_loan("co", "Equip loan", Decimal("12000"), Decimal("6"), 12, start="2026-01")
    SUB.post_due("co", "2026-12")
    bal = L.Ledger("co").balances()
    # after 12 payments the loan is fully repaid (principal back to 0)
    assert bal.get("Liabilities:Loan", Decimal("0")) == 0, bal.get("Liabilities:Loan")
    assert bal["Expenses:Interest"] > 0                                         # interest expensed
    assert sum(bal.values()) == 0
    print("  ✓ subledger: loan amortizes to 0 over 12 payments, interest expensed, balanced")


def test_close_run_posts_subledgers():
    L, SUB = _fresh()
    import importlib
    import close_run as CR
    importlib.reload(CR)
    SUB.register_asset("co", "Truck", Decimal("36000"), 3, start="2026-01")
    # seed some cash so the close gate passes (no negative cash)
    L.Ledger("co").post({"date": "2026-01-05", "lines": [{"account": "Assets:Bank:Checking", "debit": 50000},
                                                         {"account": "Equity:Contributions", "credit": 50000}]})
    res = CR.run_close("co", period="2026-01", post_subledgers=True)
    assert res["gate_passed"] is True
    assert L.Ledger("co").balances()["Expenses:Depreciation"] == Decimal("1000")  # Jan depr auto-posted
    print("  ✓ close-run --post-subledgers: Jan depreciation auto-posted during the close")


def main() -> int:
    test_register_and_post()
    test_loan_amortization_posts()
    test_close_run_posts_subledgers()
    print("OK: subledger auto-posting smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

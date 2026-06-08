#!/usr/bin/env python3
"""PR B — book-to-tax (Schedule M-1) engine: derive permanent + temporary differences from the
posted GL. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-m1-")
    import importlib
    import ledger as L
    importlib.reload(L)
    return L


def _post(L, acct_dr, amt, acct_cr):
    L.Ledger("co").post({"date": "2026-06-01",
                         "lines": [{"account": acct_dr, "debit": amt},
                                   {"account": acct_cr, "credit": amt}]})


def test_permanent_and_temporary():
    L = _fresh()
    import book_to_tax as BT
    import importlib
    importlib.reload(BT)
    _post(L, "Assets:Bank:Checking", 500000, "Income:Sales")
    _post(L, "Expenses:Salaries", 200000, "Assets:Bank:Checking")
    _post(L, "Expenses:Meals", 20000, "Assets:Bank:Checking")          # 50% → 10k addback
    _post(L, "Expenses:Penalties", 5000, "Assets:Bank:Checking")       # 100% → 5k addback
    _post(L, "Expenses:Depreciation", 40000, "Assets:Accum-Deprec")    # book 40k
    d = BT.book_to_tax("co", BT.load_rules("default"), tax_depreciation=Decimal("70000"))
    assert d["permanent"] == Decimal("15000.00"), d["permanent"]       # 10k meals + 5k penalties
    assert d["temporary"] == Decimal("30000.00"), d["temporary"]       # 70k tax − 40k book → DTL
    print("  ✓ M-1: permanent 15k (meals 50% + penalties 100%), temporary 30k (MACRS → DTL)")


def test_accrual_is_a_dta():
    L = _fresh()
    import book_to_tax as BT
    import importlib
    importlib.reload(BT)
    _post(L, "Assets:Bank:Checking", 100000, "Income:Sales")
    _post(L, "Expenses:Accrued Bonus", 8000, "Liabilities:Accrued Payroll")   # book-deducted, not paid
    d = BT.book_to_tax("co", BT.load_rules("default"))
    # accrued-but-unpaid → taxable higher now → temporary NEGATIVE → deferred tax ASSET
    assert d["temporary"] == Decimal("-8000.00"), d["temporary"]
    print("  ✓ M-1: an accrued-but-unpaid expense → negative temporary diff (deferred tax ASSET)")


def test_tax_exempt_income_subtracts():
    L = _fresh()
    import book_to_tax as BT
    import importlib
    importlib.reload(BT)
    _post(L, "Assets:Bank:Checking", 100000, "Income:Sales")
    _post(L, "Assets:Bank:Checking", 3000, "Income:Tax-Exempt Interest")      # book income, not taxable
    d = BT.book_to_tax("co", BT.load_rules("default"))
    assert d["permanent"] == Decimal("-3000.00"), d["permanent"]      # subtract from taxable
    print("  ✓ M-1: tax-exempt interest → negative permanent diff (subtracts from taxable income)")


def main() -> int:
    test_permanent_and_temporary()
    test_accrual_is_a_dta()
    test_tax_exempt_income_subtracts()
    print("OK: book-to-tax M-1 engine (PR B) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke test for the Tier-2 reporting tools: comparative, amortize, narrative.
Uses a temp GLAW_HOME so it never touches real books."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _fresh_book():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-f3-")
    import importlib
    import ledger as L
    importlib.reload(L)
    led = L.Ledger("co")
    # Jan: sales 30k, rent 5k ; Feb: sales 42k, rent 5k
    led.post({"date": "2026-01-10", "lines": [{"account": "Assets:Bank:Checking", "debit": 30000},
                                              {"account": "Income:Sales", "credit": 30000}]})
    led.post({"date": "2026-01-12", "lines": [{"account": "Expenses:Rent", "debit": 5000},
                                              {"account": "Assets:Bank:Checking", "credit": 5000}]})
    led.post({"date": "2026-02-10", "lines": [{"account": "Assets:Bank:Checking", "debit": 42000},
                                              {"account": "Income:Sales", "credit": 42000}]})
    led.post({"date": "2026-02-12", "lines": [{"account": "Expenses:Rent", "debit": 5000},
                                              {"account": "Assets:Bank:Checking", "credit": 5000}]})
    return led


def test_comparative():
    _fresh_book()
    import importlib
    import comparative as C
    importlib.reload(C)
    c = C.comparative("co", "2026-02")
    assert c["net_income"]["current"] == Decimal("37000")   # 42k - 5k
    assert c["net_income"]["prior"] == Decimal("25000")     # 30k - 5k
    assert c["net_income"]["ytd"] == Decimal("62000")       # 72k - 10k
    sales = next(l for l in c["lines"] if l["account"] == "Income:Sales")
    assert sales["vs_prior"] == Decimal("12000")
    print("  ✓ comparative: current 37k / prior 25k / YTD 62k, Δprior sales +12k")


def test_amortize():
    import amortize as A
    loan = A.loan_schedule(Decimal("100000"), Decimal("6"), 12)
    assert loan["schedule"][-1]["balance"] == Decimal("0.00"), "loan must fully amortize"
    assert loan["total_principal"] == Decimal("100000.00")
    assert loan["monthly_payment"] > Decimal("8000")        # ~8,606.64
    pre = A.prepaid_schedule(Decimal("12000"), 12)
    assert sum(r["amount"] for r in pre["schedule"]) == Decimal("12000.00")
    assert pre["schedule"][-1]["remaining"] == Decimal("0.00")
    print("  ✓ amortize: loan clears to 0 (principal 100k), prepaid releases full 12k")


def test_narrative():
    _fresh_book()
    import importlib
    import narrative as N
    importlib.reload(N)
    out = N.generate("co", period="2026-02", entity="Test Co")
    assert "Test Co" in out
    assert "net income" in out.lower()
    assert "Notes to the Financial Statements" in out
    assert "Basis of presentation" in out
    assert "$62,000.00" in out and "$72,000.00" in out  # cumulative net income + revenue present
    print("  ✓ narrative: MD&A + notes generated from the ledger with real figures")


def main() -> int:
    test_comparative()
    test_amortize()
    test_narrative()
    print("OK: Tier-2 reporting smoke passed (comparative + amortize + narrative)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

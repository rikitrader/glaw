#!/usr/bin/env python3
"""PR C — deferred-tax roll-forward: book-vs-tax basis per asset → DTL/DTA balance + movement."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import deferred_tax as DT   # noqa: E402


def test_builds_dtl():
    items = [{"asset": "Truck", "book_basis": 100000, "tax_basis": 70000},   # +30k → DTL
             {"asset": "Equip", "book_basis": 50000, "tax_basis": 45000}]    # +5k
    d = DT.deferred_rollforward(items, "21")
    assert d["cumulative_temp_diff"] == Decimal("35000.00")
    assert d["closing_balance"] == Decimal("7350.00") and d["type"] == "DTL"
    assert d["movement"] == Decimal("7350.00")                              # from a zero opening
    print("  ✓ deferred: 2 assets → cumulative 35k temp, closing DTL 7,350, movement 7,350")


def test_reversal_shrinks_dtl():
    # period 2: opening DTL 7,350; Truck fully reverses (basis equal), Equip narrows to 2k
    items = [{"asset": "Truck", "book_basis": 70000, "tax_basis": 70000},
             {"asset": "Equip", "book_basis": 50000, "tax_basis": 48000}]   # +2k
    d = DT.deferred_rollforward(items, "21", prior="7350")
    assert d["closing_balance"] == Decimal("420.00")                       # 2k × 21%
    assert d["movement"] == Decimal("-6930.00")                            # 420 − 7350 (deferred benefit)
    assert d["period_temporary_diff"] == Decimal("-33000.00")             # movement ÷ rate → provision --temporary
    print("  ✓ deferred: reversal shrinks DTL to 420; movement −6,930; period temp diff feeds provision")


def test_dta_when_book_below_tax():
    items = [{"asset": "Warranty reserve", "book_basis": 0, "tax_basis": 8000}]   # book < tax → DTA
    d = DT.deferred_rollforward(items, "21")
    assert d["closing_balance"] == Decimal("-1680.00") and d["type"] == "DTA"
    print("  ✓ deferred: book basis below tax basis → deferred tax ASSET (−1,680)")


def main() -> int:
    test_builds_dtl()
    test_reversal_shrinks_dtl()
    test_dta_when_book_below_tax()
    print("OK: deferred-tax roll-forward (PR C) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

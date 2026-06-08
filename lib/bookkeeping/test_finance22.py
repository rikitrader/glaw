#!/usr/bin/env python3
"""PR1 — MACRS depreciation engine: tax depreciation + tax basis from an asset register, feeding
the book-to-tax M-1. Temp GLAW_HOME; no network."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import depreciation as D   # noqa: E402


def test_macrs_tables():
    d = D.depreciate({"asset": "M", "cost": 100000, "class": 5})
    deps = [r["depreciation"] for r in d["schedule"]]
    assert deps == ["20000.00", "32000.00", "19200.00", "11520.00", "11520.00", "5760.00"]
    assert sum(Decimal(x) for x in deps) == Decimal("100000.00")     # fully depreciated
    assert D.depreciate({"asset": "x", "cost": 100000, "class": 7})["schedule"][0]["depreciation"] == "14290.00"
    print("  ✓ MACRS: 5-yr & 7-yr half-year tables correct, 5-yr sums to cost")


def test_179_and_bonus():
    # §179 25k + 50% bonus on 100k 5-yr: 25k + 0.5×75k(37.5k) + 20%×37.5k(7.5k) = 70k in yr1
    d = D.depreciate({"asset": "y", "cost": 100000, "class": 5, "section179": 25000, "bonus_pct": 50})
    assert d["schedule"][0]["depreciation"] == "70000.00"
    print("  ✓ MACRS: §179 + bonus taken in year 1, then MACRS on the remaining basis")


def test_register_and_basis():
    assets = [{"asset": "M", "cost": 100000, "class": 5, "placed_in_service": 2026}]
    reg = D.register(assets)
    assert reg["tax_depreciation_by_year"]["2026"] == "20000.00"
    assert reg["tax_depreciation_by_year"]["2027"] == "32000.00"
    assert D.tax_basis(assets, 2026)["M"] == "80000.00"             # 100k − 20k
    assert D.tax_depreciation_for_year(assets, 2026) == Decimal("20000.00")
    print("  ✓ MACRS: register by calendar year + tax basis roll-down")


def test_real_property_straight_line():
    d = D.depreciate({"asset": "Bldg", "cost": 390000, "class": "39"})
    assert d["schedule"][0]["depreciation"] == "10000.00"          # 390k / 39 = 10k/yr SL
    print("  ✓ MACRS: 39-yr real property is straight-line")


def test_feeds_m1():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-macrs-")
    import importlib
    import ledger as L
    import book_to_tax as BT
    importlib.reload(L); importlib.reload(BT)
    L.Ledger("co").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 500000},
                                                        {"account": "Income:Sales", "credit": 500000}]})
    L.Ledger("co").post({"date": "2026-02-01", "lines": [{"account": "Expenses:Depreciation", "debit": 40000},
                                                        {"account": "Assets:Accum-Deprec", "credit": 40000}]})
    assets = [{"asset": "Line", "cost": 350000, "class": 5, "placed_in_service": 2026}]   # yr1 = 70k
    td = D.tax_depreciation_for_year(assets, 2026)
    m1 = BT.book_to_tax("co", BT.load_rules("default"), tax_depreciation=td)
    assert m1["temporary"] == Decimal("30000.00")                  # 70k MACRS − 40k book → DTL
    print("  ✓ MACRS: feeds the M-1 (70k tax − 40k book → 30k temporary, no manual input)")


def main() -> int:
    test_macrs_tables()
    test_179_and_bonus()
    test_register_and_basis()
    test_real_property_straight_line()
    test_feeds_m1()
    print("OK: MACRS depreciation engine (PR1) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

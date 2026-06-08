#!/usr/bin/env python3
"""PR3 — Schedule K-1 allocation + return-map wiring for pass-throughs. Temp GLAW_HOME."""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import k1 as K1   # noqa: E402


def test_basic_split_and_separately_stated():
    d = K1.allocate(100000, [{"owner": "Ann", "pct": 60}, {"owner": "Bob", "pct": 40}],
                    separately_stated={"interest_income": 9000})
    assert d["k1"]["Ann"]["ordinary_business_income"] == "60000.00"
    assert d["k1"]["Bob"]["ordinary_business_income"] == "40000.00"
    assert d["k1"]["Ann"]["interest_income"] == "5400.00" and d["k1"]["Bob"]["interest_income"] == "3600.00"
    assert d["ties_out"]
    print("  ✓ K-1: 60/40 split of ordinary income + separately-stated interest, ties out")


def test_rounding_residual_ties_out():
    d = K1.allocate(100000, [{"owner": "A", "pct": "33.34"}, {"owner": "B", "pct": "33.33"},
                             {"owner": "C", "pct": "33.33"}])
    shares = [Decimal(d["k1"][n]["ordinary_business_income"]) for n in ("A", "B", "C")]
    assert sum(shares) == Decimal("100000.00") and d["ties_out"]   # residual to the last owner
    print("  ✓ K-1: three-way split's rounding residual goes to the last owner, sums exactly")


def test_pct_must_sum_100():
    try:
        K1.allocate(100000, [{"owner": "A", "pct": 60}, {"owner": "B", "pct": 30}])
        raise AssertionError("must reject pct != 100")
    except ValueError:
        pass
    print("  ✓ K-1: rejects ownership percentages that don't sum to 100")


def test_wired_into_return_map():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-k1-")
    import importlib
    import ledger as L
    import return_map as RM
    importlib.reload(L); importlib.reload(RM)
    L.Ledger("p").post({"date": "2026-01-01", "lines": [{"account": "Assets:Bank:Checking", "debit": 300000},
                                                       {"account": "Income:Sales", "credit": 300000}]})
    L.Ledger("p").post({"date": "2026-02-01", "lines": [{"account": "Expenses:Salaries", "debit": 120000},
                                                       {"account": "Assets:Bank:Checking", "credit": 120000}]})
    d = RM.map_return("p", "1065", k1_owners=[{"owner": "Ann", "pct": 60}, {"owner": "Bob", "pct": 40}])
    assert Decimal(d["taxable_income"]) == Decimal("180000")
    assert d["k1"]["k1"]["Ann"]["ordinary_business_income"] == "108000.00"
    assert d["k1"]["k1"]["Bob"]["ordinary_business_income"] == "72000.00"
    print("  ✓ K-1: 1065 return-map allocates ordinary income to owners (180k → 108k/72k)")


def main() -> int:
    test_basic_split_and_separately_stated()
    test_rounding_residual_ties_out()
    test_pct_must_sum_100()
    test_wired_into_return_map()
    print("OK: Schedule K-1 allocation (PR3) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

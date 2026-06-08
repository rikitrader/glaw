#!/usr/bin/env python3
"""PR11 — multi-state apportionment (sales/payroll/property factors). No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import apportionment as AP   # noqa: E402

STATES = [{"state": "A", "sales": 600000, "payroll": 400000, "property": 200000},
          {"state": "B", "sales": 400000, "payroll": 600000, "property": 800000}]


def test_three_factor():
    d = AP.apportion(STATES, 1000000, method="three_factor")
    assert d["states"][0]["taxable_income"] == "400000.00"     # (0.6+0.4+0.2)/3 = 0.4
    assert d["states"][1]["taxable_income"] == "600000.00"
    assert d["total_apportioned"] == "1000000.00"
    print("  ✓ apportion: equal three-factor → A 40% (400k), B 60% (600k)")


def test_double_weighted_sales():
    d = AP.apportion(STATES, 1000000, method="double_sales")
    assert d["states"][0]["taxable_income"] == "450000.00"     # (2×0.6+0.4+0.2)/4 = 0.45
    print("  ✓ apportion: double-weighted sales → A 45% (450k)")


def test_single_sales_factor():
    d = AP.apportion(STATES, 1000000, method="single_sales")
    assert d["states"][0]["taxable_income"] == "600000.00"     # sales factor only
    print("  ✓ apportion: single-sales factor → A 60% (600k)")


def test_zero_denominator_factor_dropped():
    z = AP.apportion([{"state": "A", "sales": 600000, "payroll": 0, "property": 200000},
                      {"state": "B", "sales": 400000, "payroll": 0, "property": 800000}],
                     1000000, method="three_factor")
    assert z["states"][0]["taxable_income"] == "400000.00"     # (0.6+0.2)/2 = 0.4 (payroll dropped)
    print("  ✓ apportion: a zero-everywhere factor (payroll) is dropped, weights renormalize")


def main() -> int:
    test_three_factor(); test_double_weighted_sales(); test_single_sales_factor(); test_zero_denominator_factor_dropped()
    print("OK: multi-state apportionment (PR11) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

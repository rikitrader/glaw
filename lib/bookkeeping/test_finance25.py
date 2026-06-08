#!/usr/bin/env python3
"""PR4 — QBI §199A deduction across the threshold zones. No GL/network."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import qbi as Q   # noqa: E402


def test_below_threshold():
    d = Q.qbi_deduction(100000, 0, 0, 150000, filing_status="single")
    assert d["zone"] == "below-threshold" and d["qbi_deduction"] == "20000.00"
    print("  ✓ QBI: below threshold → clean 20% of QBI, no wage limit")


def test_above_threshold_wage_limited():
    high = Q.qbi_deduction(100000, 80000, 0, 250000, filing_status="single")
    assert high["zone"] == "above-phaseout" and high["qbi_deduction"] == "20000.00"   # wage limit 40k > 20k
    low = Q.qbi_deduction(100000, 20000, 0, 250000, filing_status="single")
    assert low["qbi_deduction"] == "10000.00"                                          # wage limit 10k caps
    print("  ✓ QBI: above phase-out → limited to max(50% W-2, 25% W-2 + 2.5% UBIA)")


def test_sstb_above_threshold_gets_nothing():
    d = Q.qbi_deduction(100000, 80000, 0, 250000, filing_status="single", sstb=True)
    assert d["qbi_deduction"] == "0.00"
    print("  ✓ QBI: an SSTB above the phase-out gets no deduction")


def test_income_cap_binds():
    d = Q.qbi_deduction(100000, 0, 0, 60000, filing_status="single")
    assert d["qbi_deduction"] == "12000.00"                                            # 20% of 60k TI
    print("  ✓ QBI: capped at 20% of (taxable income − net capital gains)")


def test_ubia_helps_low_wage():
    # low wages but large UBIA: 25% × 20k + 2.5% × 1,000,000 = 5k + 25k = 30k > 20k → full 20k
    d = Q.qbi_deduction(100000, 20000, 1000000, 250000, filing_status="single")
    assert d["qbi_deduction"] == "20000.00"
    print("  ✓ QBI: the 25% W-2 + 2.5% UBIA prong lifts a low-wage, asset-heavy business")


def main() -> int:
    test_below_threshold()
    test_above_threshold_wage_limited()
    test_sstb_above_threshold_gets_nothing()
    test_income_cap_binds()
    test_ubia_helps_low_wage()
    print("OK: QBI §199A deduction (PR4) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

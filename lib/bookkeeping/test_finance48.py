#!/usr/bin/env python3
"""W5 — international engines: GILTI, Subpart F, FDII, BEAT, §163(j), 5471/5472. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import gilti as G, subpart_f as SF, fdii as FD, beat as BE, sec163j as S163, intl_forms as IF  # noqa: E402


def test_gilti():
    g = G.gilti(tested_income=1000000, qbai=2000000, foreign_tax=100000)
    assert g["gilti_inclusion"] == "800000.00" and g["sec250_deduction"] == "400000.00"
    assert g["net_us_tax"] == "4000.00"
    print("  ✓ GILTI: tested income − NDTIR → §250 50% → 21% − 80% FTC")


def test_subpart_f():
    s = SF.subpart_f(gross_subpart_f=600000, total_gross_income=1000000, current_e_and_p=500000)
    assert s["subpart_f_income"] == "500000.00"      # E&P-limited
    assert SF.subpart_f(gross_subpart_f=30000, total_gross_income=1000000,
                        current_e_and_p=999999)["subpart_f_income"] == "0.00"   # de minimis
    assert SF.subpart_f(gross_subpart_f=800000, total_gross_income=1000000,
                        current_e_and_p=2000000)["subpart_f_income"] == "1000000.00"  # full inclusion
    print("  ✓ Subpart F: de minimis / full-inclusion / E&P-limit gates")


def test_fdii():
    f = FD.fdii(deduction_eligible_income=1000000, foreign_derived_dei=600000, qbai=500000)
    assert f["fdii"] == "570000.00" and f["sec250_deduction"] == "213750.00"
    print("  ✓ FDII: (DEI − 10% QBAI) × foreign ratio → 37.5% §250 deduction")


def test_beat():
    b = BE.beat(taxable_income=10000000, regular_tax=1000000, base_erosion_payments=5000000,
                total_deductions=10000000, avg_gross_receipts=600000000)
    assert b["applies"] is True and b["beat_due"] == "500000.00"
    assert BE.beat(taxable_income=10000000, regular_tax=1000000, base_erosion_payments=5000000,
                   total_deductions=10000000, avg_gross_receipts=100000000)["applies"] is False
    print("  ✓ BEAT: applies at ≥$500M GR + ≥3% base erosion; 10% MTI − regular tax")


def test_163j():
    j = S163.sec163j(business_interest_expense=500000, ati=1000000, business_interest_income=50000)
    assert j["deductible_interest"] == "350000.00" and j["disallowed_carryforward"] == "150000.00"
    assert S163.sec163j(business_interest_expense=500000, ati=0, exempt=True)["deductible_interest"] == "500000.00"
    print("  ✓ §163(j): 30% ATI + interest income limit; small-business exempt")


def test_intl_forms():
    i = IF.determine(us_person_owns_foreign_corp=True, ownership_pct=100, years_delinquent=3)
    assert i["required_5471"] is True and i["delinquency_penalty_exposure"] == "30000.00"
    print("  ✓ 5471/5472: filer determination + delinquency penalty exposure")


def main() -> int:
    test_gilti(); test_subpart_f(); test_fdii(); test_beat(); test_163j(); test_intl_forms()
    print("OK: international engines (W5) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

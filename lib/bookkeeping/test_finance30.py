#!/usr/bin/env python3
"""PR9 — payroll tax: FICA + additional Medicare + employer match + FUTA/SUTA + Form 941. No GL."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import payroll_tax as PT   # noqa: E402


def test_basic_fica_and_futa():
    t = PT.employee_taxes(10000, ytd_wages=0, year=2024)
    assert t["employee_ss"] == "620.00" and t["employee_medicare"] == "145.00"
    assert t["employer_ss"] == "620.00" and t["employer_medicare"] == "145.00"
    assert t["futa"] == "42.00"                              # 0.6% × 7,000
    print("  ✓ payroll: SS 6.2% + Medicare 1.45% (EE+ER) + FUTA 0.6% on first $7k")


def test_ss_wage_base_cap():
    t = PT.employee_taxes(10000, ytd_wages=165000, year=2024)
    assert t["employee_ss"] == "223.20"                     # only 3,600 under the 168,600 base
    assert t["futa"] == "0.00"                              # already over the $7k FUTA base
    print("  ✓ payroll: Social Security capped at the wage base; FUTA stops after $7k")


def test_additional_medicare():
    t = PT.employee_taxes(50000, ytd_wages=180000, year=2024)
    assert t["additional_medicare"] == "270.00"            # 0.9% on the 30k over 200k (employee only)
    print("  ✓ payroll: additional 0.9% Medicare on wages over $200k (employee only)")


def test_form_941_total():
    run = PT.payroll_run([{"name": "A", "gross": 10000, "fit_withheld": 1500},
                          {"name": "B", "gross": 10000, "fit_withheld": 1500}], year=2024)
    # FIT 3,000 + SS (4×620=2,480) + Medicare (4×145=580) = 6,060
    assert run["form_941_total"] == "6060.00"
    assert run["totals"]["ss"] == "2480.00" and run["totals"]["medicare"] == "580.00"
    print("  ✓ payroll: Form 941 = FIT withheld + total SS + total Medicare (6,060)")


def test_suta():
    t = PT.employee_taxes(10000, ytd_wages=0, suta_rate="3", suta_base="9000")
    assert t["suta"] == "270.00"                            # 3% × min(10k, 9k) = 270
    print("  ✓ payroll: SUTA at the state rate on the state wage base")


def main() -> int:
    test_basic_fica_and_futa()
    test_ss_wage_base_cap()
    test_additional_medicare()
    test_form_941_total()
    test_suta()
    print("OK: payroll tax (PR9) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

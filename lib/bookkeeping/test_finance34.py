#!/usr/bin/env python3
"""PR13 — Form 1040 + Schedule SE. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import form1040 as F   # noqa: E402


def test_schedule_se():
    se = F.schedule_se(100000)
    assert se["net_se_earnings"] == "92350.00"          # 100k × 92.35%
    assert se["se_tax"] == "14129.55"                   # 12.4% SS + 2.9% Medicare
    assert se["half_se_deduction"] == "7064.78"
    # SS portion caps at the wage base less W-2 SS wages
    capped = F.schedule_se(300000, w2_ss_wages=168600)
    assert capped["ss_portion"] == "0.00"               # no SS room left
    print("  ✓ 1040: Schedule SE = 92.35% × net, 12.4% SS (wage-base capped) + 2.9% Medicare")


def test_brackets():
    assert str(F.income_tax(50000, "single")) == "6053.00"
    assert str(F.income_tax(0, "single")) == "0.00"
    assert str(F.income_tax(50000, "mfj")) == "5536.00"   # 2320 + 12%×26800
    print("  ✓ 1040: progressive brackets (single 50k → 6,053; MFJ 50k → 5,536)")


def test_full_return():
    d = F.form_1040(sch_c_net=100000, filing_status="single")
    assert d["agi"] == "92935.22"                        # 100k − ½ SE tax
    assert d["taxable_income"] == "78335.22"             # AGI − 14,600 std
    assert d["total_tax"] == "26416.30"                  # income tax + SE tax
    print("  ✓ 1040: Sch C 100k → AGI 92,935.22, taxable 78,335.22, total tax 26,416.30")


def test_refund_path():
    d = F.form_1040(sch_c_net=100000, filing_status="single", withholding=30000)
    assert d["refund"] == "3583.70" and d["balance_due"] == "0.00"
    print("  ✓ 1040: withholding above total tax → refund")


def main() -> int:
    test_schedule_se(); test_brackets(); test_full_return(); test_refund_path()
    print("OK: Form 1040 + Schedule SE (PR13) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

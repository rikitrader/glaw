#!/usr/bin/env python3
"""PR6 — estimated tax: safe-harbor installments + Form 2220/2210 underpayment penalty. No GL."""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import estimated_tax as ET   # noqa: E402


def test_corp_safe_harbor():
    d = ET.safe_harbor(100000, 80000, entity="corp")
    assert d["required_annual_payment"] == "80000.00" and d["required_installment"] == "20000.00"
    # no prior-year tax → only the current-year option
    d2 = ET.safe_harbor(50000, 0, entity="corp")
    assert d2["required_annual_payment"] == "50000.00"
    print("  ✓ estimated: corp safe harbor = lesser of 100% current / 100% prior")


def test_individual_safe_harbor():
    hi = ET.safe_harbor(100000, 80000, entity="individual", high_income=True)
    assert hi["required_annual_payment"] == "88000.00"        # min(90k, 110%×80k)
    lo = ET.safe_harbor(100000, 80000, entity="individual", high_income=False)
    assert lo["required_annual_payment"] == "80000.00"        # min(90k, 100%×80k)
    print("  ✓ estimated: individual safe harbor 90% current vs 110%/100% prior")


def test_underpayment_penalty():
    up = ET.underpayment([15000, 15000, 15000, 15000], 20000, 8)
    assert up["quarters"][0]["shortfall"] == "5000.00"
    assert up["quarters"][0]["penalty"] == "400.00"           # 5000 × 8% × 365/365
    assert up["total_penalty"] == "1066.30"                   # declining days each quarter
    print("  ✓ estimated: underpayment penalty accrues per quarter on the shortfall")


def test_no_underpayment_when_paid():
    up = ET.underpayment([20000, 20000, 20000, 20000], 20000, 8)
    assert up["total_penalty"] == "0.00"
    print("  ✓ estimated: paying the required installment → no penalty")


def main() -> int:
    test_corp_safe_harbor()
    test_individual_safe_harbor()
    test_underpayment_penalty()
    test_no_underpayment_when_paid()
    print("OK: estimated tax (PR6) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

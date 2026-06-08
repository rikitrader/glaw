#!/usr/bin/env python3
"""W2 — back-filing + SFR replacement + installment agreement. Temp GLAW_HOME."""
from __future__ import annotations
import os, sys, tempfile
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_back_filing_multiyear():
    os.environ["GLAW_HOME"] = tempfile.mkdtemp(prefix="glaw-back-")
    import back_filing as BF
    d = BF.back_filing([{"year": 2021, "tax": 10000, "months_late": 24},
                        {"year": 2022, "tax": 10000, "months_late": 12},
                        {"year": 2023, "tax": 10000, "months_late": 3}])
    assert d["total_tax"] == "30000.00"
    assert Decimal(d["grand_total_due"]) > Decimal("35000")   # + penalties + interest
    assert len(d["years"]) == 3
    print("  ✓ back-filing: 3 delinquent years rolled to a grand total (tax 30k + pen + int)")


def test_sfr_replacement_saves():
    import sfr_replacement as SFR
    d = SFR.sfr_delta(gross_income=100000, filing_status="single", deductions=20000, credits=5000)
    assert Decimal(d["savings_from_replacing"]) > 0 and d["recommend_replace"]
    assert Decimal(d["sfr_liability"]) > Decimal(d["correct_liability"])
    print("  ✓ SFR: the correct return is lower than the IRS SFR → recommend replacing")


def test_installment_agreement():
    import installment_agreement as IA
    d = IA.installment(30000, term_months=72, interest_rate="8")
    assert d["streamlined_eligible"]
    assert Decimal(d["monthly_payment"]) > Decimal("500")
    assert Decimal(d["total_paid"]) > Decimal("30000")        # carry cost
    big = IA.installment(80000, term_months=72)
    assert not big["streamlined_eligible"]                    # over $50k
    print("  ✓ installment: streamlined eligibility (<=$50k) + amortized monthly payment")


def main() -> int:
    test_back_filing_multiyear(); test_sfr_replacement_saves(); test_installment_agreement()
    print("OK: back-filing / SFR / installment (W2) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

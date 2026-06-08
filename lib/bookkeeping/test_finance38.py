#!/usr/bin/env python3
"""W1 — penalty abatement (FTA + reasonable cause → Form 843). No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import penalty_abatement as A   # noqa: E402


def test_fta_clean_history():
    d = A.abatement(5000)
    assert d["fta"]["fta_eligible"] and "FTA" in d["recommended_basis"] and d["abatable_amount"] == "5000.00"
    print("  ✓ abatement: clean 3-year history → First-Time Abatement, full amount")


def test_fta_blocked_reasons():
    d = A.fta_eligibility(penalties_prior_3yr=True, all_returns_filed=False, paid_or_arranged=False)
    assert not d["fta_eligible"] and len(d["reasons_ineligible"]) == 3
    print("  ✓ abatement: FTA blocked when history/filing/payment conditions fail (3 reasons)")


def test_reasonable_cause_strong():
    d = A.abatement(5000, penalties_prior_3yr=True,
                    reasonable_cause_factors=["death_or_serious_illness", "reliance_on_tax_professional"])
    assert not d["fta"]["fta_eligible"]
    assert d["reasonable_cause"]["strength"] == "strong" and d["reasonable_cause"]["score"] == 55
    assert d["abatable_amount"] == "5000.00"
    print("  ✓ abatement: FTA out → strong reasonable cause (death + reliance = 55) abates")


def test_weak_cause_no_basis():
    d = A.abatement(5000, penalties_prior_3yr=True, reasonable_cause_factors=["first_time_inadvertent"])
    assert d["abatable_amount"] == "0.00" and "no clear basis" in d["recommended_basis"]
    print("  ✓ abatement: weak facts → no clear basis, gather more before requesting")


def main() -> int:
    test_fta_clean_history(); test_fta_blocked_reasons(); test_reasonable_cause_strong(); test_weak_cause_no_basis()
    print("OK: penalty abatement (W1) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

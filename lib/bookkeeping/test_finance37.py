#!/usr/bin/env python3
"""W1 — IRS transcript analysis (account TC reconstruction + wage-&-income). No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import transcript_analysis as T   # noqa: E402


def test_account_reconstruction():
    txns = [{"code": "150", "amount": 20000}, {"code": "806", "amount": -15000},
            {"code": "670", "amount": -3000}, {"code": "160", "amount": 500},
            {"code": "196", "amount": 200}]
    a = T.analyze_account(txns)
    assert a["tax_assessed"] == "20000.00"
    assert a["withholding_and_credits"] == "-15000.00"
    assert a["penalties"] == "500.00" and a["interest"] == "200.00"
    assert a["account_balance"] == "2700.00"            # 20000 + 500 + 200 − 15000 − 3000
    print("  ✓ transcript: account balance reconstructed from TC postings (2,700)")


def test_status_flags():
    a = T.analyze_account([{"code": "150", "amount": 5000}, {"code": "530", "amount": 0},
                           {"code": "582", "amount": 0}, {"code": "420", "amount": 0}])
    joined = " ".join(a["flags"])
    assert "Currently-Not-Collectible" in joined and "lien" in joined and "examination" in joined
    print("  ✓ transcript: flags CNC (530), lien (582), exam (420)")


def test_wage_income():
    wi = T.analyze_wage_income([{"type": "W-2", "amount": 60000}, {"type": "W-2", "amount": 20000},
                                {"type": "1099-NEC", "amount": 15000}])
    assert wi["total_reported_income"] == "95000.00" and wi["document_count"] == 3
    assert wi["by_document_type"]["W-2"] == "80000.00"
    print("  ✓ transcript: wage-&-income totals third-party-reported income (95,000)")


def main() -> int:
    test_account_reconstruction(); test_status_flags(); test_wage_income()
    print("OK: IRS transcript analysis (W1) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

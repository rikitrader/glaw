#!/usr/bin/env python3
"""PR7 — IRS penalty & interest (FTF/FTP + daily-compounded interest). No GL."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import penalties as PEN   # noqa: E402


def test_ftf_ftp_combined():
    p = PEN.penalties(10000, 3)
    assert p["failure_to_file"] == "1350.00" and p["ftf_rate_total_pct"] == "13.50"   # 4.5%×3
    assert p["failure_to_pay"] == "150.00" and p["ftp_rate_total_pct"] == "1.50"      # 0.5%×3
    assert p["total_penalty"] == "1500.00"
    print("  ✓ penalties: 3 months → FTF 4.5%/mo (reduced by FTP) + FTP 0.5%/mo")


def test_caps():
    p = PEN.penalties(10000, 12)
    assert p["ftf_rate_total_pct"] == "25.00"                  # FTF caps at 25%
    assert p["ftp_rate_total_pct"] == "6.00"                   # 0.5% × 12
    p2 = PEN.penalties(10000, 60)
    assert p2["ftp_rate_total_pct"] == "25.00"                 # FTP caps at 25% (50 months)
    print("  ✓ penalties: FTF caps at 25%, FTP caps at 25% (50 months)")


def test_interest_daily_compound():
    i = PEN.interest(10000, 8, 365)
    assert i["interest"] == "832.78"                           # 10k × ((1+.08/365)^365 − 1)
    s = PEN.interest(10000, 8, 365, compound="simple")
    assert s["interest"] == "800.00"
    print("  ✓ penalties: interest compounded daily (832.78) vs simple (800.00)")


def test_assess_total():
    d = PEN.assess(10000, 3, rate_pct="8", days=90)
    # penalties 1500; interest on (10000+1500) for 90 days daily
    assert d["penalties"]["total_penalty"] == "1500.00"
    assert d["total_due"] == str(__import__("decimal").Decimal(d["penalties"]["unpaid_tax"])
                                 + __import__("decimal").Decimal("1500.00")
                                 + __import__("decimal").Decimal(d["interest"]["interest"]))
    print("  ✓ penalties: assess() = unpaid + penalties + interest")


def main() -> int:
    test_ftf_ftp_combined()
    test_caps()
    test_interest_daily_compound()
    test_assess_total()
    print("OK: IRS penalty & interest (PR7) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

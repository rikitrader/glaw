#!/usr/bin/env python3
"""PR12 — tax credits: R&D §41, foreign tax credit, general business credit. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import credits as C   # noqa: E402


def test_rd_credit():
    assert C.rd_credit(500000, method="asc", prior_qre_avg=300000)["rd_credit"] == "49000.00"  # 14%×(500k−150k)
    assert C.rd_credit(500000, method="asc", prior_qre_avg=0)["rd_credit"] == "30000.00"         # 6%×500k
    assert C.rd_credit(500000, method="regular", base=200000)["rd_credit"] == "60000.00"         # 20%×300k
    assert C.rd_credit(500000, method="asc", prior_qre_avg=300000, reduced_280c=True)["rd_credit"] == "38710.00"
    print("  ✓ credits: R&D ASC 49k / no-prior 30k / regular 60k / §280C reduced 38,710")


def test_ftc_limitation():
    f = C.ftc(50000, 200000, 1000000, 210000)
    assert f["limitation"] == "42000.00" and f["ftc_allowed"] == "42000.00" and f["carryover"] == "8000.00"
    f2 = C.ftc(30000, 200000, 1000000, 210000)   # paid below the limit → all allowed
    assert f2["ftc_allowed"] == "30000.00" and f2["carryover"] == "0.00"
    print("  ✓ credits: FTC limited to US tax × (foreign ÷ total); excess carries over")


def test_general_business_credit():
    g = C.general_business_credit(100000, 200000, 150000)
    assert g["limitation"] == "50000.00" and g["gbc_allowed"] == "50000.00" and g["carryover"] == "50000.00"
    g2 = C.general_business_credit(20000, 200000, 0)   # no TMT → 25% over 25k floor
    assert g2["limitation"] == str(__import__("decimal").Decimal("200000") - __import__("decimal").Decimal("0.25") * __import__("decimal").Decimal("175000"))
    print("  ✓ credits: GBC capped at net tax − max(TMT, 25% over $25k); excess carries over")


def main() -> int:
    test_rd_credit(); test_ftc_limitation(); test_general_business_credit()
    print("OK: tax credits (PR12) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

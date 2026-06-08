#!/usr/bin/env python3
"""W3 — entity-specific engines: S-corp basis/AAA, partner basis, penalty taxes, 1041. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import scorp_basis as SB, scorp_aaa as AAA, partner_basis as PB, penalty_taxes as PT, form1041 as F41  # noqa: E402


def test_scorp_basis():
    d = SB.basis(beginning_stock=50000, income=30000, distributions=40000, loss=60000)
    assert d["loss_allowed"] == "40000.00" and d["loss_suspended"] == "20000.00" and d["ending_stock_basis"] == "0.00"
    # loss uses debt basis after stock
    d2 = SB.basis(beginning_stock=10000, beginning_debt=20000, loss=25000)
    assert d2["loss_allowed"] == "25000.00" and d2["ending_debt_basis"] == "5000.00"
    assert SB.basis(beginning_stock=10000, distributions=15000)["excess_distribution_capital_gain"] == "5000.00"
    print("  ✓ S-corp basis: loss limited to stock+debt; excess suspended; excess dist = cap gain")


def test_scorp_aaa():
    a = AAA.aaa_rollforward(beginning_aaa=20000, income=10000, distributions=40000,
                            accumulated_e_and_p=15000, stock_basis=100000)
    assert a["distribution_from_aaa_taxfree"] == "30000.00" and a["distribution_dividend_from_aep"] == "10000.00"
    assert a["ending_aaa"] == "0.00"
    print("  ✓ S-corp AAA: distribution ordered AAA (tax-free) → AE&P (dividend) → basis → gain")


def test_partner_basis():
    p = PB.outside_basis(beginning_basis=40000, income=20000, liability_increase=10000,
                         distributions=30000, loss=50000)
    assert p["loss_allowed"] == "40000.00" and p["loss_suspended"] == "10000.00"
    print("  ✓ partner basis: §704(d) limits loss to outside basis; liabilities increase basis")


def test_penalty_taxes():
    t = PT.accumulated_earnings_tax(500000)
    assert t["accumulated_earnings_credit"] == "250000.00" and t["accumulated_earnings_tax"] == "50000.00"
    assert PT.accumulated_earnings_tax(500000, is_psc=True)["accumulated_earnings_credit"] == "150000.00"  # PSC min credit is 150k
    assert PT.phc_tax(100000)["personal_holding_company_tax"] == "20000.00"
    print("  ✓ penalty taxes: accumulated-earnings §531 (250k credit, 20%) + PHC §541 (20%)")


def test_form1041():
    f = F41.form_1041(total_income=50000, deductions=5000, distributions=30000, entity_type="complex")
    assert f["distributable_net_income"] == "45000.00" and f["income_distribution_deduction"] == "30000.00"
    assert f["trust_taxable_income"] == "14900.00"   # 45k − 30k − 100 exemption
    print("  ✓ Form 1041: DNI caps the distribution deduction; trust taxable income after exemption")


def main() -> int:
    test_scorp_basis(); test_scorp_aaa(); test_partner_basis(); test_penalty_taxes(); test_form1041()
    print("OK: entity-specific engines (W3) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

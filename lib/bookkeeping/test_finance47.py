#!/usr/bin/env python3
"""W4 — state tax engines: state income tax, PTET, franchise/margin, combined, nexus, sourcing. No GL."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import state_income_tax as ST, ptet as PT, franchise_tax as FT  # noqa: E402
import combined_unitary as CU, income_nexus as NX, sourcing as SR  # noqa: E402


def test_state_income_tax():
    d = ST.state_tax(federal_taxable_income=1000000, additions=50000, subtractions=20000,
                     apportionment_pct="50", state_nol=100000, rate_pct="6", nol_limit_pct="80")
    assert d["state_taxable_income"] == "415000.00" and d["state_tax"] == "24900.00"
    print("  ✓ state income tax: FTI ± mods → apportioned → NOL → rate")


def test_ptet():
    p = PT.ptet(pass_through_income=1000000, ptet_rate_pct="9.3")
    assert p["ptet_tax"] == "93000.00" and p["owner_credit"] == "93000.00"
    assert p["federal_deduction_benefit"] == "34410.00"
    print("  ✓ PTET: entity-level tax + owner credit + federal SALT-cap-bypass benefit")


def test_franchise():
    assert FT.delaware_franchise(authorized_shares=10000, issued_shares=1000,
                                 total_gross_assets=1000000)["franchise_tax"] == "250.00"
    tx = FT.texas_margin(total_revenue=5000000, compensation=2000000)
    assert tx["taxable_margin"] == "1000000.00" and tx["franchise_tax"] == "7500.00"
    assert FT.texas_margin(total_revenue=2000000)["franchise_tax"] == "0.00"   # below threshold
    assert FT.california_minimum()["franchise_tax"] == "800.00"
    print("  ✓ franchise: DE (lesser method), TX margin (greatest deduction), CA $800 min")


def test_combined():
    c = CU.combined([{"income": 600000, "in_state_sales": 200000, "everywhere_sales": 600000},
                     {"income": 400000, "in_state_sales": 100000, "everywhere_sales": 400000}], rate_pct="6")
    assert c["combined_income"] == "1000000.00" and c["state_tax"] == "18000.00"
    print("  ✓ combined/unitary: pooled income × combined sales factor × rate")


def test_nexus():
    n = NX.nexus(in_state_receipts=1000000, sells_only_tangible_goods=True, only_solicitation=True)
    assert n["income_tax_nexus"] is False and n["pl_86_272_protected"] is True   # P.L. 86-272 shields
    assert NX.nexus(in_state_receipts=1000000, unprotected_activities=["services"])["income_tax_nexus"] is True
    print("  ✓ nexus: P.L. 86-272 shields tangible-goods solicitation; services → taxable")


def test_sourcing():
    s = SR.source_sales([{"amount": 100000, "market_state": "FL"}, {"amount": 50000, "market_state": "TX"}],
                        home_state="FL", nexus_states=["FL"])
    assert s["home_numerator"] == "150000.00"        # TX (no nexus) thrown back to FL
    assert s["sales_factor_pct"] == "100.0000"
    print("  ✓ sourcing: market-based + throwback (no-nexus sale → origin state)")


def main() -> int:
    test_state_income_tax(); test_ptet(); test_franchise(); test_combined(); test_nexus(); test_sourcing()
    print("OK: state tax engines (W4) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""W2 — offer in compromise (RCP) + collections (CNC/CDP) + TFRP (§6672). No GL."""
from __future__ import annotations
import sys
from decimal import Decimal
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def test_oic_rcp():
    import offer_in_compromise as OIC
    d = OIC.rcp([{"name": "House", "value": 300000, "loan": 250000},   # QSV 240k − 250k → 0 equity
                 {"name": "Car", "value": 20000, "loan": 0}],          # QSV 16k
                5000, 4500, offer_type="lump")                          # net 500 × 12
    assert d["net_realizable_equity"] == "16000.00"
    assert d["future_income_value"] == "6000.00"
    assert d["minimum_offer"] == "22000.00"
    periodic = OIC.rcp([{"name": "Car", "value": 20000, "loan": 0}], 5000, 4500, offer_type="periodic")
    assert periodic["future_income_value"] == "12000.00"               # ×24
    print("  ✓ OIC: RCP = net realizable equity (16k) + future income value (6k) = 22k minimum offer")


def test_collections():
    import irs_collections as COL
    assert COL.cnc_status(4000, 5000)["cnc_eligible"]                  # expenses > income
    assert not COL.cnc_status(6000, 4000)["cnc_eligible"]
    cdp = COL.cdp_deadline("2026-06-01", notice_type="levy")
    assert cdp["cdp_request_deadline"] == "2026-07-01" and cdp["form"] == "Form 12153"
    assert COL.status_as_of("2026-07-01", "2026-06-15") == "TIMELY"
    assert "LATE" in COL.status_as_of("2026-07-01", "2026-08-01")
    print("  ✓ collections: CNC when expenses ≥ income; CDP 30-day deadline + timely/late")


def test_tfrp():
    import trust_fund_recovery as TFRP
    liable = TFRP.tfrp(withheld_income_tax=30000, employee_fica=15000,
                       responsible_factors=["check_signing_authority", "controls_payroll"],
                       willful_factors=["knew_taxes_unpaid", "paid_other_creditors_instead"])
    assert liable["trust_fund_amount"] == "45000.00" and liable["personally_liable"]
    assert liable["tfrp_exposure"] == "45000.00"
    not_willful = TFRP.tfrp(withheld_income_tax=30000, employee_fica=15000,
                            responsible_factors=["check_signing_authority", "controls_payroll"], willful_factors=[])
    assert not not_willful["personally_liable"] and not_willful["tfrp_exposure"] == "0.00"
    print("  ✓ TFRP: trust-fund amount = withheld + employee FICA; liable only if responsible AND willful")


def main() -> int:
    test_oic_rcp(); test_collections(); test_tfrp()
    print("OK: OIC / collections / TFRP (W2) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

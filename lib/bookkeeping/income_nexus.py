"""GLAW state income-tax nexus — does the company have to file/pay income tax in a state?

Two independent tests:
- Public Law 86-272 (15 U.S.C. §381): a state may NOT impose a net-income tax if the company's only
  in-state activity is the SOLICITATION of orders for tangible personal property, approved and
  shipped from outside the state. ANY non-protected activity (services, repairs, in-state inventory,
  non-solicitation employees, and — per the MTC's 2021 guidance — many internet/website activities)
  destroys the protection. P.L. 86-272 does NOT protect against franchise/gross-receipts taxes.
- Economic nexus (post-Wayfair, applied to income tax by many states): in-state receipts above the
  state's threshold (commonly $500,000) create nexus regardless of physical presence.

Returns whether the state can tax the company's income, with the reason.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal

PL86272_PROTECTED = "protected by P.L. 86-272 (solicitation of orders for tangible goods only)"


def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def nexus(*, in_state_receipts="0", economic_threshold="500000", sells_only_tangible_goods=False,
          only_solicitation=False, has_physical_presence=False, unprotected_activities=None) -> dict:
    receipts = _dec(in_state_receipts)
    unprotected = list(unprotected_activities or [])
    pl_protected = (sells_only_tangible_goods and only_solicitation and not unprotected
                    and not has_physical_presence)
    economic = receipts >= _dec(economic_threshold)
    # nexus exists if there is physical presence or economic nexus, UNLESS P.L. 86-272 shields income tax
    has_nexus = (has_physical_presence or economic or bool(unprotected))
    income_taxable = has_nexus and not pl_protected
    if pl_protected:
        reason = PL86272_PROTECTED
    elif income_taxable:
        reason = ("economic nexus (receipts ≥ threshold)" if economic else
                  "physical presence / unprotected activity")
    else:
        reason = "no nexus (below threshold, no presence)"
    return {"in_state_receipts": str(receipts), "economic_nexus": economic,
            "pl_86_272_protected": pl_protected, "unprotected_activities": unprotected,
            "income_tax_nexus": income_taxable, "reason": reason}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "STATE INCOME-TAX NEXUS", "-" * 56,
        f"  economic nexus: {d['economic_nexus']}",
        f"  P.L. 86-272 protected: {d['pl_86_272_protected']}",
        f"  INCOME-TAX NEXUS: {d['income_tax_nexus']}  ({d['reason']})",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-income-nexus")
    ap.add_argument("--in-state-receipts", default="0")
    ap.add_argument("--economic-threshold", default="500000")
    ap.add_argument("--sells-only-tangible-goods", action="store_true")
    ap.add_argument("--only-solicitation", action="store_true")
    ap.add_argument("--has-physical-presence", action="store_true")
    ap.add_argument("--unprotected-activities", default=None, help="comma-separated")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = nexus(in_state_receipts=a.in_state_receipts, economic_threshold=a.economic_threshold,
              sells_only_tangible_goods=a.sells_only_tangible_goods, only_solicitation=a.only_solicitation,
              has_physical_presence=a.has_physical_presence,
              unprotected_activities=(a.unprotected_activities.split(",") if a.unprotected_activities else []))
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

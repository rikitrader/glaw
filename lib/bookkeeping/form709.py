#!/usr/bin/env python3
"""GLAW Form 709 (United States Gift (and GST) Tax Return) — annual-exclusion netting,
gift-splitting, the cumulative-gift computation, lifetime-exemption use, and the GST flag.

Flow (§2502): current-year gifts − per-donee annual exclusion − marital/charitable deductions
= taxable gifts this year. Gift tax is cumulative: tax = tentative tax on (this year + prior
taxable gifts) − tentative tax on (prior taxable gifts), then reduced by the unused unified
credit (the lifetime applicable exclusion converts to a credit on the §2001(c) schedule). No
tax is due until lifetime taxable gifts exceed the basic exclusion amount.

[VERIFY] Year-sensitive: annual exclusion = $18,000 (2024), $19,000 (2025) per donee; basic
exclusion amount = $13,610,000 (2024), $13,990,000 (2025). Gift-splitting (§2513) doubles the
annual exclusion and draws on both spouses' exemptions but requires consent on both returns.
GST allocation is flagged here, not computed — route to the strategy seat. DRAFT only.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

from form706 import tentative_tax, BEA  # reuse the §2001(c) schedule + BEA table

_CENT = Decimal("0.01")
# [VERIFY] per-donee annual exclusion by gift year.
ANNUAL_EXCLUSION = {"2024": Decimal("18000"), "2025": Decimal("19000")}


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def form_709(*, current_gifts="0", num_donees="1", marital_deduction="0",
             charitable_deduction="0", prior_taxable_gifts="0", prior_credit_used="0",
             split_gifts=False, gst_transfers="0", year="2025") -> dict:
    gifts = _dec(current_gifts)
    donees = int(_dec(num_donees))
    ann = ANNUAL_EXCLUSION.get(str(year), ANNUAL_EXCLUSION["2025"])
    if split_gifts:
        ann = ann * 2                                     # §2513 split doubles the exclusion
    exclusion = ann * max(0, donees)
    deductions = _dec(marital_deduction) + _dec(charitable_deduction)
    taxable_this_year = max(Decimal("0"), gifts - exclusion - deductions)

    prior = _dec(prior_taxable_gifts)
    cumulative = prior + taxable_this_year
    tax_on_current = max(Decimal("0"), tentative_tax(cumulative) - tentative_tax(prior))

    bea = BEA.get(str(year), BEA["2025"])
    total_credit = tentative_tax(bea)
    credit_available = max(Decimal("0"), total_credit - _dec(prior_credit_used))
    credit_applied = min(credit_available, tax_on_current)
    gift_tax_due = max(Decimal("0"), tax_on_current - credit_applied)
    exclusion_remaining = max(Decimal("0"), bea - prior - taxable_this_year)

    return {
        "gift_year": str(year),
        "current_year_gifts": str(_q(gifts)),
        "annual_exclusion_per_donee": str(_q(ann)),
        "gift_splitting": "yes" if split_gifts else "no",
        "total_annual_exclusion": str(_q(exclusion)),
        "deductions": str(_q(deductions)),
        "taxable_gifts_this_year": str(_q(taxable_this_year)),
        "prior_taxable_gifts": str(_q(prior)),
        "cumulative_taxable_gifts": str(_q(cumulative)),
        "tax_on_current_gifts": str(_q(tax_on_current)),
        "unified_credit_applied": str(_q(credit_applied)),
        "gift_tax_due": str(_q(gift_tax_due)),
        "applicable_exclusion_remaining": str(_q(exclusion_remaining)),
        "gst_transfers_flagged": str(_q(_dec(gst_transfers))),
        "_verify": "annual exclusion + BEA are year-sensitive; GST allocation/exemption is FLAGGED only — route §2632 allocation to /glaw-tax-strategy; gift-splitting needs spousal consent on both returns.",
    }


def render_text(d: dict) -> str:
    lines = [
        "=" * 60, f"FORM 709 (GIFT TAX) — DRAFT — gift year {d['gift_year']}", "-" * 60,
        f"  current-year gifts              {_dec(d['current_year_gifts']):>16,.2f}",
        f"  annual exclusion/donee (split={d['gift_splitting']}) {_dec(d['annual_exclusion_per_donee']):>9,.2f}",
        f"  less total annual exclusion     {_dec(d['total_annual_exclusion']):>16,.2f}",
        f"  less deductions                 {_dec(d['deductions']):>16,.2f}",
        f"  = taxable gifts this year       {_dec(d['taxable_gifts_this_year']):>16,.2f}",
        f"  + prior taxable gifts           {_dec(d['prior_taxable_gifts']):>16,.2f}",
        f"  = cumulative taxable gifts      {_dec(d['cumulative_taxable_gifts']):>16,.2f}",
        f"  tax on current gifts            {_dec(d['tax_on_current_gifts']):>16,.2f}",
        f"  less unified credit applied     {_dec(d['unified_credit_applied']):>16,.2f}",
        f"  = GIFT TAX DUE                  {_dec(d['gift_tax_due']):>16,.2f}",
        f"  applicable exclusion remaining  {_dec(d['applicable_exclusion_remaining']):>16,.2f}",
    ]
    if _dec(d["gst_transfers_flagged"]) > 0:
        lines.append(f"  ⚑ GST transfers flagged         {_dec(d['gst_transfers_flagged']):>16,.2f}")
    lines += ["=" * 60, f"  ⚠ VERIFY: {d['_verify']}"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-form709", description="Form 709 gift-tax DRAFT computation.")
    for f in ("current-gifts", "marital-deduction", "charitable-deduction",
              "prior-taxable-gifts", "prior-credit-used", "gst-transfers"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--num-donees", default="1")
    ap.add_argument("--split-gifts", action="store_true", help="§2513 gift-splitting election")
    ap.add_argument("--year", default="2025", help="gift year (drives exclusion + BEA) [VERIFY]")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = form_709(current_gifts=a.current_gifts, num_donees=a.num_donees,
                 marital_deduction=a.marital_deduction, charitable_deduction=a.charitable_deduction,
                 prior_taxable_gifts=a.prior_taxable_gifts, prior_credit_used=a.prior_credit_used,
                 split_gifts=a.split_gifts, gst_transfers=a.gst_transfers, year=a.year)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

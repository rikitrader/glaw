#!/usr/bin/env python3
"""GLAW Form 706 (United States Estate Tax Return) — taxable estate, tentative tax on the
§2001(c) unified rate schedule, the applicable (unified) credit, DSUE/portability, and the
net federal estate tax.

Flow (§2001): gross estate − deductions = taxable estate; + adjusted taxable gifts (post-1976,
not already in the gross estate) = the tax base; tentative tax on the base via the §2001(c)
schedule; − gift tax payable on the post-1976 gifts; − the applicable credit (basic exclusion
amount + any DSUE from a predeceased spouse, converted to credit) = net estate tax.

[VERIFY] Year-sensitive: the basic exclusion amount (BEA) is inflation-indexed — 2024 =
$13,610,000, 2025 = $13,990,000. Confirm the decedent's year-of-death BEA before filing. The
§2001(c) bracket table itself (top rate 40%) is stable post-2013 but VERIFY against the
year-of-death Form 706 instructions. Every figure here is a DRAFT for a licensed attorney/CPA
to verify against the appraisals and the year's instructions — nothing is filed off this output.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")

# §2001(c) unified rate schedule (over, tax-at-floor, marginal-rate-on-excess).
_BRACKETS = [
    (Decimal("0"),         Decimal("0"),       Decimal("0.18")),
    (Decimal("10000"),     Decimal("1800"),    Decimal("0.20")),
    (Decimal("20000"),     Decimal("3800"),    Decimal("0.22")),
    (Decimal("40000"),     Decimal("8200"),    Decimal("0.24")),
    (Decimal("60000"),     Decimal("13000"),   Decimal("0.26")),
    (Decimal("80000"),     Decimal("18200"),   Decimal("0.28")),
    (Decimal("100000"),    Decimal("23800"),   Decimal("0.30")),
    (Decimal("150000"),    Decimal("38800"),   Decimal("0.32")),
    (Decimal("250000"),    Decimal("70800"),   Decimal("0.34")),
    (Decimal("500000"),    Decimal("155800"),  Decimal("0.37")),
    (Decimal("750000"),    Decimal("248300"),  Decimal("0.39")),
    (Decimal("1000000"),   Decimal("345800"),  Decimal("0.40")),
]

# [VERIFY] basic exclusion amount by year of death.
BEA = {"2024": Decimal("13610000"), "2025": Decimal("13990000")}


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def tentative_tax(base: Decimal) -> Decimal:
    """§2001(c) tentative tax on a tax base."""
    base = max(Decimal("0"), base)
    over, tax, rate = _BRACKETS[0]
    for o, t, r in _BRACKETS:
        if base >= o:
            over, tax, rate = o, t, r
        else:
            break
    return tax + (base - over) * rate


def form_706(*, gross_estate="0", funeral_admin="0", debts_claims="0",
             marital_deduction="0", charitable_deduction="0", state_death_tax="0",
             adjusted_taxable_gifts="0", gift_tax_payable="0",
             dsue="0", year="2025") -> dict:
    gross = _dec(gross_estate)
    deductions = (_dec(funeral_admin) + _dec(debts_claims) + _dec(marital_deduction)
                  + _dec(charitable_deduction) + _dec(state_death_tax))
    taxable_estate = max(Decimal("0"), gross - deductions)
    base = taxable_estate + _dec(adjusted_taxable_gifts)
    tent = tentative_tax(base)
    tax_after_gift = max(Decimal("0"), tent - _dec(gift_tax_payable))

    bea = BEA.get(str(year), BEA["2025"])
    applicable_exclusion = bea + _dec(dsue)               # BEA + portability DSUE
    applicable_credit = tentative_tax(applicable_exclusion)
    net_estate_tax = max(Decimal("0"), tax_after_gift - applicable_credit)

    return {
        "year_of_death": str(year),
        "gross_estate": str(_q(gross)),
        "total_deductions": str(_q(deductions)),
        "taxable_estate": str(_q(taxable_estate)),
        "adjusted_taxable_gifts": str(_q(_dec(adjusted_taxable_gifts))),
        "tax_base": str(_q(base)),
        "tentative_tax": str(_q(tent)),
        "gift_tax_payable": str(_q(_dec(gift_tax_payable))),
        "tax_after_gift_tax": str(_q(tax_after_gift)),
        "basic_exclusion_amount": str(_q(bea)),
        "dsue_from_spouse": str(_q(_dec(dsue))),
        "applicable_exclusion_amount": str(_q(applicable_exclusion)),
        "applicable_credit_amount": str(_q(applicable_credit)),
        "net_estate_tax": str(_q(net_estate_tax)),
        "_verify": "BEA + §2001(c) schedule are year-sensitive — confirm against year-of-death Form 706 instructions; appraisals must support every Schedule A–I value.",
    }


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 60, f"FORM 706 (ESTATE TAX) — DRAFT — year of death {d['year_of_death']}", "-" * 60,
        f"  gross estate                    {_dec(d['gross_estate']):>16,.2f}",
        f"  less total deductions           {_dec(d['total_deductions']):>16,.2f}",
        f"  = taxable estate                {_dec(d['taxable_estate']):>16,.2f}",
        f"  + adjusted taxable gifts        {_dec(d['adjusted_taxable_gifts']):>16,.2f}",
        f"  = tax base                      {_dec(d['tax_base']):>16,.2f}",
        f"  tentative tax (§2001(c))        {_dec(d['tentative_tax']):>16,.2f}",
        f"  less gift tax payable           {_dec(d['gift_tax_payable']):>16,.2f}",
        f"  = tax after gift tax            {_dec(d['tax_after_gift_tax']):>16,.2f}",
        f"  applicable exclusion (BEA+DSUE) {_dec(d['applicable_exclusion_amount']):>16,.2f}",
        f"  less applicable credit          {_dec(d['applicable_credit_amount']):>16,.2f}",
        f"  = NET ESTATE TAX                {_dec(d['net_estate_tax']):>16,.2f}",
        "=" * 60,
        f"  ⚠ VERIFY: {d['_verify']}",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-form706", description="Form 706 estate-tax DRAFT computation.")
    for f in ("gross-estate", "funeral-admin", "debts-claims", "marital-deduction",
              "charitable-deduction", "state-death-tax", "adjusted-taxable-gifts",
              "gift-tax-payable", "dsue"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--year", default="2025", help="year of death (drives BEA) [VERIFY]")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = form_706(gross_estate=a.gross_estate, funeral_admin=a.funeral_admin,
                 debts_claims=a.debts_claims, marital_deduction=a.marital_deduction,
                 charitable_deduction=a.charitable_deduction, state_death_tax=a.state_death_tax,
                 adjusted_taxable_gifts=a.adjusted_taxable_gifts, gift_tax_payable=a.gift_tax_payable,
                 dsue=a.dsue, year=a.year)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

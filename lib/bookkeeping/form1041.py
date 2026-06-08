#!/usr/bin/env python3
"""GLAW Form 1041 (estates & trusts) — distributable net income (DNI), the income-distribution
deduction, and trust taxable income.

DNI (§643) caps the amount of income that carries out to beneficiaries and is the ceiling on the
trust's distribution deduction. DNI = trust taxable income (before the distribution deduction and
exemption) + tax-exempt interest − net capital gains allocable to corpus. The income-distribution
deduction = the lesser of DNI (net of tax-exempt income) or the amount actually distributed.
Trust taxable income = total income − deductions − distribution deduction − the exemption
($600 complex / $300 simple / $100 [VERIFY] qualified disability).
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
EXEMPTION = {"simple": Decimal("300"), "complex": Decimal("100"), "estate": Decimal("600")}


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def form_1041(*, total_income="0", deductions="0", tax_exempt_interest="0",
              capital_gains_to_corpus="0", distributions="0", entity_type="complex") -> dict:
    ti_before = _dec(total_income) - _dec(deductions)
    dni = ti_before + _dec(tax_exempt_interest) - _dec(capital_gains_to_corpus)
    distributable = max(Decimal("0"), dni - _dec(tax_exempt_interest))   # net of tax-exempt
    dist_deduction = min(distributable, _dec(distributions))
    exemption = EXEMPTION.get(entity_type, EXEMPTION["complex"])
    taxable = max(Decimal("0"), ti_before - dist_deduction - exemption)
    return {"distributable_net_income": str(_q(dni)),
            "income_distribution_deduction": str(_q(dist_deduction)),
            "exemption": str(_q(exemption)),
            "trust_taxable_income": str(_q(taxable))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "FORM 1041 (ESTATE / TRUST)", "-" * 56,
        f"  distributable net income (DNI) {_dec(d['distributable_net_income']):>11,.2f}",
        f"  income-distribution deduction  {_dec(d['income_distribution_deduction']):>11,.2f}",
        f"  exemption                      {_dec(d['exemption']):>11,.2f}",
        f"  TRUST TAXABLE INCOME           {_dec(d['trust_taxable_income']):>11,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-form1041")
    for f in ("total-income", "deductions", "tax-exempt-interest", "capital-gains-to-corpus", "distributions"):
        ap.add_argument(f"--{f}", default="0")
    ap.add_argument("--entity-type", default="complex", choices=list(EXEMPTION))
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = form_1041(total_income=a.total_income, deductions=a.deductions,
                  tax_exempt_interest=a.tax_exempt_interest, capital_gains_to_corpus=a.capital_gains_to_corpus,
                  distributions=a.distributions, entity_type=a.entity_type)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

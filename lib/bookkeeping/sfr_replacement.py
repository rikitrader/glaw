#!/usr/bin/env python3
"""GLAW Substitute-for-Return (SFR) replacement — when the IRS files a return for a non-filer
under IRC §6020(b), it uses the worst assumptions (single/MFS filing status, the standard
deduction only, no dependents, no itemized deductions, no business expenses, no credits), which
overstates the tax. Filing the taxpayer's own correct return replaces the SFR and almost always
reduces the liability. This computes the SFR-vs-correct delta and the resulting savings.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def sfr_delta(*, gross_income, sfr_tax=None, filing_status="single", deductions="0",
              business_expenses="0", credits="0", rate_pct=None, year=2024,
              correct_tax=None) -> dict:
    """If sfr_tax / correct_tax are supplied, use them directly; otherwise estimate via form1040
    (individual) for a quick delta. Returns the SFR liability, the correct liability, and savings."""
    import form1040 as F
    gi = _dec(gross_income)
    if sfr_tax is None:                                       # SFR: gross income, std deduction only
        sfr = F.form_1040(wages=str(gi), filing_status=filing_status, year=year)
        sfr_liab = _dec(sfr["total_tax"])
    else:
        sfr_liab = _dec(sfr_tax)
    if correct_tax is None:                                   # correct: income net of real deductions
        net = max(Decimal("0"), gi - _dec(business_expenses))
        correct = F.form_1040(wages=str(net), filing_status=filing_status,
                              qbi_deduction=str(_dec(deductions)), credits=str(_dec(credits)), year=year)
        correct_liab = _dec(correct["total_tax"])
    else:
        correct_liab = _dec(correct_tax)
    savings = _q(sfr_liab - correct_liab)
    return {"sfr_liability": str(_q(sfr_liab)), "correct_liability": str(_q(correct_liab)),
            "savings_from_replacing": str(savings),
            "recommend_replace": savings > 0}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "SFR REPLACEMENT (IRC §6020(b))", "-" * 56,
        f"  IRS SFR liability        {_dec(d['sfr_liability']):>16,.2f}",
        f"  correct-return liability {_dec(d['correct_liability']):>16,.2f}",
        f"  SAVINGS from replacing   {_dec(d['savings_from_replacing']):>16,.2f}",
        f"  recommend filing the replacement: {d['recommend_replace']}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-sfr")
    ap.add_argument("--gross-income", required=True)
    ap.add_argument("--filing-status", default="single", choices=["single", "mfj"])
    ap.add_argument("--deductions", default="0", help="QBI/itemized the SFR omitted")
    ap.add_argument("--business-expenses", default="0")
    ap.add_argument("--credits", default="0")
    ap.add_argument("--sfr-tax", default=None); ap.add_argument("--correct-tax", default=None)
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = sfr_delta(gross_income=a.gross_income, sfr_tax=a.sfr_tax, filing_status=a.filing_status,
                  deductions=a.deductions, business_expenses=a.business_expenses, credits=a.credits,
                  year=a.year, correct_tax=a.correct_tax)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GLAW IRS transcript analysis — reconstruct a taxpayer's account from IRS account-transcript
transaction codes and the wage-&-income transcript, so the firm knows exactly what the IRS has on
record before responding to an exam, filing a back return, or computing a collection alternative.

Account transcripts use IRS transaction codes (TC). The amounts are signed as the IRS posts them
(assessments positive, credits/payments negative), so the running balance is the sum of the
postings. This maps the common codes to categories and reconstructs the balance; the wage-&-income
side totals the income reported to the IRS by third parties (for SFR / under-reporter matching).
All code meanings below are the IRS's published TC definitions.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")
# IRS transaction-code → category (published TC meanings)
TC_CATEGORY = {
    "150": "tax_assessed", "290": "tax_assessed", "300": "tax_assessed",   # return / additional assessment
    "806": "withholding", "807": "withholding",
    "766": "credits", "768": "credits",                                    # refundable credits
    "610": "payments", "660": "payments", "670": "payments", "706": "payments", "640": "payments",
    "160": "penalties", "166": "penalties", "270": "penalties", "276": "penalties",
    "196": "interest", "336": "interest", "340": "interest",
    "420": "exam", "300_exam": "exam",
    "530": "status", "582": "lien", "971": "status", "420_status": "status",
}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def analyze_account(transactions: list[dict]) -> dict:
    by_cat: dict[str, Decimal] = defaultdict(Decimal)
    rows = []
    balance = Decimal("0")
    flags = []
    for t in transactions:
        code = str(t.get("code", "")).strip()
        amt = _dec(t.get("amount", 0))
        cat = TC_CATEGORY.get(code, "other")
        by_cat[cat] += amt
        balance += amt
        if code in ("530",):
            flags.append("TC 530 — account in Currently-Not-Collectible status")
        if code in ("582",):
            flags.append("TC 582 — federal tax lien filed")
        if code in ("420",):
            flags.append("TC 420 — examination opened")
        rows.append({"code": code, "category": cat, "amount": str(_q(amt)),
                     "description": t.get("description", "")})
    return {"by_category": {k: str(_q(v)) for k, v in by_cat.items()},
            "tax_assessed": str(_q(by_cat.get("tax_assessed", Decimal("0")))),
            "withholding_and_credits": str(_q(by_cat.get("withholding", Decimal("0")) + by_cat.get("credits", Decimal("0")))),
            "payments": str(_q(by_cat.get("payments", Decimal("0")))),
            "penalties": str(_q(by_cat.get("penalties", Decimal("0")))),
            "interest": str(_q(by_cat.get("interest", Decimal("0")))),
            "account_balance": str(_q(balance)), "transactions": rows, "flags": flags}


def analyze_wage_income(documents: list[dict]) -> dict:
    """Wage-&-income transcript: third-party-reported income (W-2/1099) the IRS already has."""
    by_type: dict[str, Decimal] = defaultdict(Decimal)
    total = Decimal("0")
    for d in documents:
        amt = _dec(d.get("amount", 0))
        by_type[d.get("type", "?")] += amt
        total += amt
    return {"by_document_type": {k: str(_q(v)) for k, v in by_type.items()},
            "total_reported_income": str(_q(total)), "document_count": len(documents)}


def render_text(d: dict) -> str:
    a = d.get("account")
    o = ["=" * 56, "IRS TRANSCRIPT ANALYSIS", "-" * 56]
    if a:
        o += [f"  tax assessed            {_dec(a['tax_assessed']):>16,.2f}",
              f"  withholding + credits   {_dec(a['withholding_and_credits']):>16,.2f}",
              f"  payments                {_dec(a['payments']):>16,.2f}",
              f"  penalties               {_dec(a['penalties']):>16,.2f}",
              f"  interest                {_dec(a['interest']):>16,.2f}",
              f"  ACCOUNT BALANCE         {_dec(a['account_balance']):>16,.2f}"]
        for f in a["flags"]:
            o.append(f"  ⚠️  {f}")
    if d.get("wage_income"):
        wi = d["wage_income"]
        o += ["-" * 56, f"  third-party income reported {_dec(wi['total_reported_income']):>12,.2f} "
              f"({wi['document_count']} docs)"]
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-transcript")
    ap.add_argument("--account", default=None, help="account-transcript JSON: [{code, amount, description}]")
    ap.add_argument("--wage-income", default=None, help="W&I JSON: [{type, amount, payer}]")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    out = {}
    if a.account:
        raw = sys.stdin.read() if a.account == "-" else Path(a.account).read_text(encoding="utf-8")
        out["account"] = analyze_account(json.loads(raw))
    if a.wage_income:
        out["wage_income"] = analyze_wage_income(json.loads(Path(a.wage_income).read_text(encoding="utf-8")))
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

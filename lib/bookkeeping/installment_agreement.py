#!/usr/bin/env python3
"""GLAW installment-agreement engine (Form 9465) — the monthly-payment plan to pay off an IRS
balance. A streamlined IA is available when the balance is at or under the streamlined limit
(generally $50,000 for individuals) and it is paid within 72 months or by the collection statute
expiration date (CSED), whichever is earlier. Interest plus the reduced 0.25 %/month failure-to-
pay penalty (while on an approved IA) accrue on the declining balance.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 40
_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def installment(balance, *, term_months: int = 72, interest_rate="8", ftp_on_ia_rate="3",
                streamlined_limit="50000") -> dict:
    bal = _dec(balance)
    n = max(1, int(term_months))
    # monthly cost of carry = annual (interest + reduced FTP) / 12
    annual = (_dec(interest_rate) + _dec(ftp_on_ia_rate)) / Decimal("100")
    r = annual / Decimal("12")
    if r == 0:
        payment = bal / n
    else:
        payment = bal * r / (Decimal("1") - (Decimal("1") + r) ** (-n))
    payment = _q(payment)
    total_paid = _q(payment * n)
    return {"balance": str(_q(bal)), "term_months": n,
            "streamlined_eligible": bal <= _dec(streamlined_limit) and n <= 72,
            "monthly_payment": str(payment), "total_paid": str(total_paid),
            "total_interest_and_penalty": str(_q(total_paid - bal)),
            "carry_rate_annual_pct": str(_q(annual * 100))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "INSTALLMENT AGREEMENT (Form 9465)", "-" * 56,
        f"  balance                  {_dec(d['balance']):>16,.2f}",
        f"  term                     {d['term_months']} months",
        f"  streamlined eligible: {d['streamlined_eligible']}",
        f"  monthly payment          {_dec(d['monthly_payment']):>16,.2f}",
        f"  total paid               {_dec(d['total_paid']):>16,.2f}",
        f"  interest + penalty       {_dec(d['total_interest_and_penalty']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-installment")
    ap.add_argument("--balance", required=True)
    ap.add_argument("--term-months", type=int, default=72)
    ap.add_argument("--interest-rate", default="8")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = installment(a.balance, term_months=a.term_months, interest_rate=a.interest_rate)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

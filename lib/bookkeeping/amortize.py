#!/usr/bin/env python3
"""GLAW amortization — loan and prepaid/deferral schedules → recurring journal entries.

  loan     amortize a loan: each payment splits into interest + principal; produces the
           per-period schedule and the entries (Dr interest expense + Dr loan payable /
           Cr cash). Standard equal-payment amortization.
  prepaid  straight-line release of a prepaid/deferred balance over N periods (Dr expense /
           Cr prepaid each period) — or deferred revenue (Dr deferred revenue / Cr revenue).
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def loan_schedule(principal: Decimal, annual_rate_pct: Decimal, n_payments: int) -> dict:
    r = (annual_rate_pct / Decimal("100")) / Decimal("12")    # monthly rate
    if r == 0:
        pmt = _q(principal / n_payments)
    else:
        # P * r / (1 - (1+r)^-n)
        factor = (Decimal(1) + r) ** (-n_payments)
        pmt = _q(principal * r / (Decimal(1) - factor))
    bal = principal
    rows, tot_int, tot_prin = [], Decimal("0"), Decimal("0")
    for i in range(1, n_payments + 1):
        interest = _q(bal * r)
        prin = pmt - interest
        if i == n_payments:                 # final payment clears the balance exactly
            prin = bal
            pmt_i = _q(prin + interest)
        else:
            pmt_i = pmt
        bal = _q(bal - prin)
        tot_int += interest
        tot_prin += prin
        rows.append({"period": i, "payment": _q(pmt_i), "interest": _q(interest),
                     "principal": _q(prin), "balance": bal})
    return {"type": "loan", "principal": _q(principal), "annual_rate_pct": annual_rate_pct,
            "payments": n_payments, "monthly_payment": pmt,
            "total_interest": _q(tot_int), "total_principal": _q(tot_prin), "schedule": rows}


def prepaid_schedule(amount: Decimal, n_periods: int, *, label: str = "prepaid") -> dict:
    per = _q(amount / n_periods)
    rows, accum = [], Decimal("0")
    for i in range(1, n_periods + 1):
        amt = per if i < n_periods else (amount - accum)   # true-up final period
        accum += amt
        rows.append({"period": i, "amount": _q(amt), "released_to_date": _q(accum),
                     "remaining": _q(amount - accum)})
    return {"type": label, "amount": _q(amount), "periods": n_periods,
            "per_period": per, "schedule": rows}


def render_loan(d: dict) -> str:
    o = ["=" * 64, f"LOAN AMORTIZATION  ({d['annual_rate_pct']}% / {d['payments']} payments)", "-" * 64,
         f"  principal {d['principal']:>12,.2f}   payment {d['monthly_payment']:>12,.2f}", "-" * 64,
         f"  {'#':>4}{'Payment':>14}{'Interest':>14}{'Principal':>14}{'Balance':>14}"]
    for r in d["schedule"]:
        o.append(f"  {r['period']:>4}{r['payment']:>14,.2f}{r['interest']:>14,.2f}"
                 f"{r['principal']:>14,.2f}{r['balance']:>14,.2f}")
    o.append("-" * 64)
    o.append(f"  total interest {d['total_interest']:>12,.2f}   total principal {d['total_principal']:>12,.2f}")
    o.append("=" * 64)
    return "\n".join(o)


def render_prepaid(d: dict) -> str:
    o = ["=" * 52, f"{d['type'].upper()} SCHEDULE  ({d['periods']} periods)", "-" * 52,
         f"  amount {d['amount']:>12,.2f}   per period {d['per_period']:>12,.2f}", "-" * 52,
         f"  {'#':>4}{'Amount':>14}{'To date':>14}{'Remaining':>14}"]
    for r in d["schedule"]:
        o.append(f"  {r['period']:>4}{r['amount']:>14,.2f}{r['released_to_date']:>14,.2f}{r['remaining']:>14,.2f}")
    o.append("=" * 52)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-amortize")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("loan")
    p.add_argument("--principal", required=True); p.add_argument("--rate", required=True, help="annual %%")
    p.add_argument("--payments", type=int, required=True, help="number of monthly payments")
    p.add_argument("--format", default="text", choices=["text", "json"])
    p = sub.add_parser("prepaid")
    p.add_argument("--amount", required=True); p.add_argument("--periods", type=int, required=True)
    p.add_argument("--label", default="prepaid"); p.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.cmd == "loan":
        d = loan_schedule(Decimal(a.principal), Decimal(a.rate), a.payments)
        print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_loan(d))
    else:
        d = prepaid_schedule(Decimal(a.amount), a.periods, label=a.label)
        print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_prepaid(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

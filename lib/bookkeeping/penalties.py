#!/usr/bin/env python3
"""GLAW IRS penalty & interest engine.

  Failure-to-file (FTF): 5 % of the unpaid tax for each month (or part) late, max 25 %.
  Failure-to-pay  (FTP): 0.5 % of the unpaid tax per month, max 25 %.
  When both apply in the same month the FTF is reduced by the FTP (so 4.5 % FTF + 0.5 % FTP =
  5 % combined) for the first five months; after that FTP continues alone up to its 25 % cap.
  Interest: the federal short-term rate + 3 %, compounded DAILY on the unpaid balance.
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


def penalties(unpaid_tax, months_late: int, *, combined: bool = True) -> dict:
    unpaid = _dec(unpaid_tax)
    ftf_cum = Decimal("0")
    ftp_cum = Decimal("0")
    for _ in range(max(int(months_late), 0)):
        ftp_rate = Decimal("0.005") if ftp_cum < Decimal("0.25") else Decimal("0")
        ftp_rate = min(ftp_rate, Decimal("0.25") - ftp_cum)
        if ftf_cum < Decimal("0.25"):
            ftf_rate = Decimal("0.05") - (ftp_rate if combined else Decimal("0"))
            ftf_rate = min(ftf_rate, Decimal("0.25") - ftf_cum)
            ftf_cum += ftf_rate
        ftp_cum += ftp_rate
    ftf_pen = _q(unpaid * ftf_cum)
    ftp_pen = _q(unpaid * ftp_cum)
    return {"unpaid_tax": str(_q(unpaid)), "months_late": int(months_late),
            "ftf_rate_total_pct": str(_q(ftf_cum * 100)), "failure_to_file": str(ftf_pen),
            "ftp_rate_total_pct": str(_q(ftp_cum * 100)), "failure_to_pay": str(ftp_pen),
            "total_penalty": str(_q(ftf_pen + ftp_pen))}


def interest(balance, rate_pct, days: int, *, compound: str = "daily") -> dict:
    bal = _dec(balance)
    r = _dec(rate_pct) / Decimal("100")
    if compound == "daily":
        factor = (Decimal("1") + r / Decimal("365")) ** int(days) - Decimal("1")
    else:                                                     # simple
        factor = r * Decimal(days) / Decimal("365")
    return {"balance": str(_q(bal)), "rate_pct": str(_dec(rate_pct)), "days": int(days),
            "compound": compound, "interest": str(_q(bal * factor))}


def assess(unpaid_tax, months_late, *, rate_pct="8", days=None, combined=True) -> dict:
    pen = penalties(unpaid_tax, months_late, combined=combined)
    days = days if days is not None else int(months_late) * 30
    intr = interest(_dec(pen["unpaid_tax"]) + _dec(pen["total_penalty"]), rate_pct, days)
    total = _q(_dec(pen["unpaid_tax"]) + _dec(pen["total_penalty"]) + _dec(intr["interest"]))
    return {"penalties": pen, "interest": intr, "total_due": str(total)}


def render_text(d: dict) -> str:
    p, i = d["penalties"], d["interest"]
    return "\n".join([
        "=" * 56, "IRS PENALTY & INTEREST", "-" * 56,
        f"  unpaid tax               {_dec(p['unpaid_tax']):>16,.2f}",
        f"  failure-to-file ({p['ftf_rate_total_pct']}%)  {_dec(p['failure_to_file']):>16,.2f}",
        f"  failure-to-pay  ({p['ftp_rate_total_pct']}%)  {_dec(p['failure_to_pay']):>16,.2f}",
        f"  interest ({i['rate_pct']}%, {i['days']}d, {i['compound']}) {_dec(i['interest']):>14,.2f}",
        "-" * 56,
        f"  TOTAL DUE                {_dec(d['total_due']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-penalties")
    ap.add_argument("--unpaid-tax", required=True)
    ap.add_argument("--months-late", type=int, required=True)
    ap.add_argument("--rate", default="8", help="interest rate %% (fed short-term + 3)")
    ap.add_argument("--days", type=int, default=None, help="days for interest (default months×30)")
    ap.add_argument("--no-combined", action="store_true", help="don't reduce FTF by FTP overlap")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = assess(a.unpaid_tax, a.months_late, rate_pct=a.rate, days=a.days, combined=not a.no_combined)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

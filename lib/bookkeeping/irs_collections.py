#!/usr/bin/env python3
"""GLAW IRS collections engine — Currently-Not-Collectible (CNC) status and the Collection Due
Process (CDP) deadline.

CNC (status 53): when allowable living expenses meet or exceed income, the taxpayer has no ability
to pay and collection is suspended (interest/penalties still accrue). CDP (IRC §6320 for a filed
Notice of Federal Tax Lien, §6330 for a levy): the taxpayer has 30 days from the notice to request
a hearing on Form 12153 to preserve Tax Court review; a late request gets only an equivalent
hearing (no Tax Court review).
"""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def cnc_status(monthly_income, allowable_expenses) -> dict:
    net = _q(_dec(monthly_income) - _dec(allowable_expenses))
    eligible = net <= 0
    return {"net_monthly": str(net), "cnc_eligible": eligible,
            "basis": "expenses ≥ income — no ability to pay (status 53)" if eligible
                     else "positive monthly ability to pay — pursue an installment agreement / OIC"}


def cdp_deadline(notice_date: str, *, notice_type: str = "lien") -> dict:
    nd = date.fromisoformat(notice_date[:10])
    deadline = nd + timedelta(days=30)
    authority = "IRC §6320 (NFTL)" if notice_type == "lien" else "IRC §6330 (levy)"
    return {"notice_type": notice_type, "notice_date": nd.isoformat(),
            "cdp_request_deadline": deadline.isoformat(), "form": "Form 12153",
            "authority": authority,
            "note": "a request after this date gets only an equivalent hearing (no Tax Court review)"}


def status_as_of(deadline: str, as_of: str) -> str:
    return "TIMELY" if date.fromisoformat(as_of[:10]) <= date.fromisoformat(deadline[:10]) else "LATE (equivalent hearing only)"


def render_text(d: dict) -> str:
    o = ["=" * 56, "IRS COLLECTIONS", "-" * 56]
    if "cnc" in d:
        c = d["cnc"]
        o += [f"  net monthly {_dec(c['net_monthly']):>16,.2f}   CNC eligible: {c['cnc_eligible']}",
              f"    {c['basis']}"]
    if "cdp" in d:
        c = d["cdp"]
        o += [f"  CDP ({c['authority']}): request by {c['cdp_request_deadline']} on {c['form']}",
              f"    {c['note']}"]
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-collections")
    ap.add_argument("--monthly-income", default=None)
    ap.add_argument("--allowable-expenses", default=None)
    ap.add_argument("--cdp-notice-date", default=None)
    ap.add_argument("--cdp-notice-type", default="lien", choices=["lien", "levy"])
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    out = {}
    if a.monthly_income is not None and a.allowable_expenses is not None:
        out["cnc"] = cnc_status(a.monthly_income, a.allowable_expenses)
    if a.cdp_notice_date:
        out["cdp"] = cdp_deadline(a.cdp_notice_date, notice_type=a.cdp_notice_type)
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

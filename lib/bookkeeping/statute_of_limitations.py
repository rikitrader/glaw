#!/usr/bin/env python3
"""GLAW statute-of-limitations engine — the assessment (§6501) and refund (§6511) clocks that
govern whether the IRS can still assess and whether the taxpayer can still claim a refund.

Assessment (§6501): the IRS generally has 3 years from the LATER of the return's filing date or
its due date. A substantial omission of gross income (> 25 %) extends it to 6 years; a false/
fraudulent return or a non-filed return leaves it OPEN indefinitely. Refund (§6511): a claim must
be filed within 3 years of filing the return or 2 years of paying the tax, whichever is later.
Dates are computed deterministically; a year of 365/366 days is handled by the date module.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta


def _d(s: str) -> date:
    return date.fromisoformat(s[:10])


def _plus_years(d: date, n: int) -> date:
    try:
        return d.replace(year=d.year + n)
    except ValueError:                       # Feb 29 → Feb 28
        return d.replace(year=d.year + n, day=28)


def assessment_sol(*, due_date: str, filed_date: str | None = None,
                   omission_over_25pct: bool = False, fraud: bool = False,
                   filed: bool = True) -> dict:
    if not filed or fraud:
        reason = "fraud — no statute" if fraud else "return never filed — no statute"
        return {"basis": reason, "years": None, "sol_open_indefinitely": True,
                "assessment_deadline": None}
    start = max(_d(due_date), _d(filed_date or due_date))     # the later of due / filed
    years = 6 if omission_over_25pct else 3
    deadline = _plus_years(start, years)
    return {"basis": ("6-year (>25% omission)" if omission_over_25pct else "3-year (general)"),
            "years": years, "clock_start": start.isoformat(),
            "assessment_deadline": deadline.isoformat(), "sol_open_indefinitely": False}


def refund_sol(*, filed_date: str, paid_date: str | None = None) -> dict:
    filed = _d(filed_date)
    three_from_filing = _plus_years(filed, 3)
    candidates = [("3 years from filing", three_from_filing)]
    if paid_date:
        candidates.append(("2 years from payment", _plus_years(_d(paid_date), 2)))
    label, deadline = max(candidates, key=lambda c: c[1])      # whichever is later
    return {"basis": label, "refund_deadline": deadline.isoformat()}


def status_as_of(deadline: str | None, as_of: str) -> str:
    if deadline is None:
        return "OPEN (no statute)"
    return "OPEN" if _d(as_of) <= _d(deadline) else "EXPIRED"


def render_text(d: dict) -> str:
    a = d["assessment"]
    o = ["=" * 56, "STATUTE OF LIMITATIONS", "-" * 56,
         f"  assessment basis: {a['basis']}",
         f"  assessment deadline: {a['assessment_deadline'] or 'none (open)'}"]
    if "assessment_status" in d:
        o.append(f"  assessment status (as of {d['as_of']}): {d['assessment_status']}")
    if "refund" in d:
        o += [f"  refund basis: {d['refund']['basis']}",
              f"  refund deadline: {d['refund']['refund_deadline']}"]
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-sol")
    ap.add_argument("--due-date", required=True, help="return due date (e.g. 2021-04-15)")
    ap.add_argument("--filed-date", default=None)
    ap.add_argument("--omission-over-25pct", action="store_true")
    ap.add_argument("--fraud", action="store_true")
    ap.add_argument("--not-filed", action="store_true")
    ap.add_argument("--paid-date", default=None)
    ap.add_argument("--as-of", default=None, help="evaluate OPEN/EXPIRED as of this date")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    assess = assessment_sol(due_date=a.due_date, filed_date=a.filed_date,
                            omission_over_25pct=a.omission_over_25pct, fraud=a.fraud,
                            filed=not a.not_filed)
    out = {"assessment": assess}
    if a.filed_date:
        out["refund"] = refund_sol(filed_date=a.filed_date, paid_date=a.paid_date)
    if a.as_of:
        out["as_of"] = a.as_of
        out["assessment_status"] = status_as_of(assess["assessment_deadline"], a.as_of)
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

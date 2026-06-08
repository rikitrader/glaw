#!/usr/bin/env python3
"""GLAW back-filing engine — for a multi-year non-filer, compute each delinquent year's tax (from
the posted general ledger via the return mapper, or a supplied figure) and roll the failure-to-
file / failure-to-pay penalties and interest across all years to a single grand total.
Reuses penalties.assess and return_map so the numbers tie to the books.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import penalties as PEN          # noqa: E402

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _year_tax(spec: dict, rate_pct: str) -> Decimal:
    if "tax" in spec:
        return _dec(spec["tax"])
    if spec.get("book"):                                       # derive from the GL
        import return_map as RM
        d = RM.map_return(spec["book"], spec.get("form", "1120"), as_of=spec.get("as_of"))
        return _q(_dec(d["taxable_income"]) * _dec(rate_pct) / Decimal("100"))
    return Decimal("0")


def back_filing(years: list[dict], *, rate_pct="21", interest_rate="8") -> dict:
    rows = []
    tot_tax = tot_pen = tot_int = Decimal("0")
    for y in years:
        tax = _q(_year_tax(y, rate_pct))
        paid = _dec(y.get("paid", 0))
        unpaid = max(Decimal("0"), tax - paid)
        months = int(y.get("months_late", 0))
        a = PEN.assess(unpaid, months, rate_pct=interest_rate, days=int(y.get("days", months * 30)))
        pen = _dec(a["penalties"]["total_penalty"])
        intr = _dec(a["interest"]["interest"])
        tot_tax += tax; tot_pen += pen; tot_int += intr
        rows.append({"year": y.get("year"), "tax": str(tax), "paid": str(_q(paid)),
                     "unpaid": str(_q(unpaid)), "months_late": months,
                     "penalties": str(_q(pen)), "interest": str(_q(intr)),
                     "total_due": str(_q(unpaid + pen + intr))})
    grand = _q(sum((_dec(r["total_due"]) for r in rows), Decimal("0")))
    return {"years": rows, "total_tax": str(_q(tot_tax)), "total_penalties": str(_q(tot_pen)),
            "total_interest": str(_q(tot_int)), "grand_total_due": str(grand)}


def render_text(d: dict) -> str:
    o = ["=" * 64, "BACK-FILING — multi-year delinquent returns", "-" * 64,
         f"  {'year':<6}{'tax':>12}{'unpaid':>12}{'penalties':>12}{'interest':>11}{'due':>11}"]
    for r in d["years"]:
        o.append(f"  {str(r['year']):<6}{_dec(r['tax']):>12,.0f}{_dec(r['unpaid']):>12,.0f}"
                 f"{_dec(r['penalties']):>12,.0f}{_dec(r['interest']):>11,.0f}{_dec(r['total_due']):>11,.0f}")
    o += ["-" * 64, f"  GRAND TOTAL DUE {_dec(d['grand_total_due']):>16,.2f}", "=" * 64]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-back-filing")
    ap.add_argument("years", help="JSON file/'-': [{year, tax|book, months_late, paid}]")
    ap.add_argument("--rate", default="21"); ap.add_argument("--interest-rate", default="8")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.years == "-" else Path(a.years).read_text(encoding="utf-8")
    d = back_filing(json.loads(raw), rate_pct=a.rate, interest_rate=a.interest_rate)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GLAW depreciation — asset register schedules (straight-line + MACRS GDS).

MACRS GDS half-year-convention percentages are the published IRS Pub 946 Table A-1
values (200% declining balance for 3/5/7/10-year, 150% for 15/20-year, switching to
straight-line). They are stored as constants and self-checked to sum to 100% at import
so a transcription error fails loudly rather than silently mis-depreciating.

§179 expensing and bonus depreciation are applied first (off the basis) when requested,
then the remaining basis is depreciated on the chosen schedule.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP

# IRS Pub 946, Table A-1 — MACRS GDS, half-year convention (percent of basis per year).
MACRS_HALF_YEAR: dict[int, list[str]] = {
    3:  ["33.33", "44.45", "14.81", "7.41"],
    5:  ["20.00", "32.00", "19.20", "11.52", "11.52", "5.76"],
    7:  ["14.29", "24.49", "17.49", "12.49", "8.93", "8.92", "8.93", "4.46"],
    10: ["10.00", "18.00", "14.40", "11.52", "9.22", "7.37", "6.55", "6.55", "6.56", "6.55", "3.28"],
    15: ["5.00", "9.50", "8.55", "7.70", "6.93", "6.23", "5.90", "5.90", "5.91", "5.90",
         "5.91", "5.90", "5.91", "5.90", "5.91", "2.95"],
    20: ["3.750", "7.219", "6.677", "6.177", "5.713", "5.285", "4.888", "4.522", "4.462",
         "4.461", "4.462", "4.461", "4.462", "4.461", "4.462", "4.461", "4.462", "4.461",
         "4.462", "4.461", "2.231"],
}

# Self-check: every class must sum to 100.00 (guards transcription errors).
for _life, _pcts in MACRS_HALF_YEAR.items():
    _s = sum(Decimal(p) for p in _pcts)
    if _s != Decimal("100.00") and _s != Decimal("100.000"):
        raise AssertionError(f"MACRS {_life}-year table sums to {_s}, not 100")

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def straight_line(cost: Decimal, salvage: Decimal, life_years: int) -> list[dict]:
    base = cost - salvage
    annual = _q(base / life_years)
    sched, accum = [], Decimal("0")
    for yr in range(1, life_years + 1):
        dep = annual if yr < life_years else (base - accum)   # true-up final year
        accum += dep
        sched.append({"year": yr, "depreciation": _q(dep), "accumulated": _q(accum),
                      "book_value": _q(cost - accum)})
    return sched


def macrs(cost: Decimal, life_years: int) -> list[dict]:
    if life_years not in MACRS_HALF_YEAR:
        raise SystemExit(f"ERROR: MACRS life {life_years} not supported "
                         f"(choose {sorted(MACRS_HALF_YEAR)}) — or use --method straight-line")
    sched, accum = [], Decimal("0")
    pcts = MACRS_HALF_YEAR[life_years]
    for i, p in enumerate(pcts, start=1):
        dep = _q(cost * Decimal(p) / Decimal("100"))
        if i == len(pcts):
            dep = _q(cost - accum)                # absorb rounding into final year
        accum += dep
        sched.append({"year": i, "rate_pct": p, "depreciation": _q(dep),
                      "accumulated": _q(accum), "book_value": _q(cost - accum)})
    return sched


def schedule(cost: Decimal, *, method: str, life_years: int, salvage: Decimal = Decimal("0"),
             section_179: Decimal = Decimal("0"), bonus_pct: Decimal = Decimal("0")) -> dict:
    s179 = min(section_179, cost)
    after_179 = cost - s179
    bonus = _q(after_179 * bonus_pct / Decimal("100"))
    basis = after_179 - bonus
    if method == "macrs":
        rows = macrs(basis, life_years)
    elif method in ("straight-line", "sl"):
        rows = straight_line(basis, salvage, life_years)
    else:
        raise SystemExit("ERROR: --method must be macrs or straight-line")
    total = s179 + bonus + sum(r["depreciation"] for r in rows)
    return {"cost": _q(cost), "section_179": _q(s179), "bonus": _q(bonus),
            "depreciable_basis": _q(basis), "method": method, "life_years": life_years,
            "schedule": rows, "total_depreciated": _q(total)}


def render_text(d: dict) -> str:
    o = ["=" * 64, f"DEPRECIATION  ({d['method']}, {d['life_years']}-year)", "-" * 64,
         f"  Cost                 {d['cost']:>14,.2f}"]
    if d["section_179"]:
        o.append(f"  §179 expense         {d['section_179']:>14,.2f}")
    if d["bonus"]:
        o.append(f"  Bonus                {d['bonus']:>14,.2f}")
    o.append(f"  Depreciable basis    {d['depreciable_basis']:>14,.2f}")
    o.append("-" * 64)
    o.append(f"  {'Year':<6}{'Depreciation':>16}{'Accumulated':>16}{'Book value':>16}")
    for r in d["schedule"]:
        o.append(f"  {r['year']:<6}{r['depreciation']:>16,.2f}{r['accumulated']:>16,.2f}"
                 f"{r['book_value']:>16,.2f}")
    o.append("-" * 64)
    o.append(f"  Total depreciated    {d['total_depreciated']:>14,.2f}")
    o.append("=" * 64)
    return "\n".join(o)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="glaw-depreciate")
    ap.add_argument("--cost", required=True, type=str)
    ap.add_argument("--method", default="macrs", choices=["macrs", "straight-line", "sl"])
    ap.add_argument("--life", type=int, required=True, help="recovery period in years")
    ap.add_argument("--salvage", default="0", help="salvage value (straight-line only)")
    ap.add_argument("--section-179", default="0")
    ap.add_argument("--bonus-pct", default="0", help="bonus depreciation %% (e.g. 60)")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = schedule(Decimal(a.cost), method=a.method, life_years=a.life,
                 salvage=Decimal(a.salvage), section_179=Decimal(a.section_179),
                 bonus_pct=Decimal(a.bonus_pct))
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

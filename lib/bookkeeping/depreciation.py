#!/usr/bin/env python3
"""GLAW MACRS depreciation engine — compute tax depreciation + tax basis from an asset register,
so the book-to-tax depreciation difference and the deferred-tax roll-forward become exact instead
of a hand-fed --tax-depreciation number.

Personal property uses the IRS MACRS half-year-convention tables (200 % declining balance for
3/5/7/10-year, 150 % for 15/20-year, switching to straight-line). Real property (27.5-yr
residential, 39-yr nonresidential) is straight-line. §179 expensing and bonus depreciation are
taken in the placed-in-service year, then MACRS runs on the remaining basis.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_CENT = Decimal("0.01")

# IRS MACRS half-year-convention percentage tables (per Pub. 946, Table A-1).
MACRS_HY = {
    3:  ["33.33", "44.45", "14.81", "7.41"],
    5:  ["20.00", "32.00", "19.20", "11.52", "11.52", "5.76"],
    7:  ["14.29", "24.49", "17.49", "12.49", "8.93", "8.92", "8.93", "4.46"],
    10: ["10.00", "18.00", "14.40", "11.52", "9.22", "7.37", "6.55", "6.55", "6.56", "6.55", "3.28"],
    15: ["5.00", "9.50", "8.55", "7.70", "6.93", "6.23", "5.90", "5.90", "5.91", "5.90",
         "5.91", "5.90", "5.91", "5.90", "5.91", "2.95"],
    20: ["3.750", "7.219", "6.677", "6.177", "5.713", "5.285", "4.888", "4.522", "4.462", "4.461",
         "4.462", "4.461", "4.462", "4.461", "4.462", "4.461", "4.462", "4.461", "4.462", "4.461", "2.231"],
}
REAL_PROPERTY = {Decimal("27.5"), Decimal("39")}   # straight-line


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def depreciate(asset: dict) -> dict:
    """One asset → {macrs_basis, section179, bonus, schedule:[{year_index, depreciation,
    accumulated, basis_remaining}]}. Year index 1 = placed-in-service year."""
    cost = _dec(asset["cost"])
    cls = _dec(asset["class"])
    s179 = min(_dec(asset.get("section179", 0)), cost)
    after179 = cost - s179
    bonus = _q(after179 * _dec(asset.get("bonus_pct", 0)) / Decimal("100"))
    macrs_basis = after179 - bonus

    sched = []
    accum = s179 + bonus
    if cls in REAL_PROPERTY:                                   # straight-line real property
        years = int(cls)
        annual = macrs_basis / cls
        first = _q(s179 + bonus + annual)
        sched.append({"year_index": 1, "depreciation": str(first)})
        accum = s179 + bonus + annual
        for i in range(2, years + 1):
            accum += annual
            sched.append({"year_index": i, "depreciation": str(_q(annual))})
    else:
        table = MACRS_HY.get(int(cls))
        if table is None:
            raise ValueError(f"unsupported MACRS class {cls}")
        for i, pct in enumerate(table, start=1):
            macrs_dep = _q(macrs_basis * _dec(pct) / Decimal("100"))
            dep = macrs_dep + (s179 + bonus if i == 1 else Decimal("0"))
            accum += macrs_dep
            sched.append({"year_index": i, "depreciation": str(_q(dep))})

    # accumulate + basis remaining
    run = Decimal("0")
    for row in sched:
        run += _dec(row["depreciation"])
        row["accumulated"] = str(_q(run))
        row["basis_remaining"] = str(_q(cost - run))
    return {"asset": asset.get("asset", "?"), "cost": str(_q(cost)), "class": str(cls),
            "section179": str(_q(s179)), "bonus": str(bonus), "macrs_basis": str(_q(macrs_basis)),
            "schedule": sched}


def register(assets: list[dict], placed_base_year: int | None = None) -> dict:
    """Whole register → per-asset schedules + total tax depreciation per CALENDAR year (using each
    asset's placed_in_service year) + each asset's tax basis at the latest year covered."""
    per_asset = [depreciate(a) for a in assets]
    by_year: dict[int, Decimal] = {}
    for a, sch in zip(assets, per_asset):
        pis = int(a.get("placed_in_service", placed_base_year or 1))
        for row in sch["schedule"]:
            yr = pis + row["year_index"] - 1
            by_year[yr] = by_year.get(yr, Decimal("0")) + _dec(row["depreciation"])
    return {"assets": per_asset,
            "tax_depreciation_by_year": {str(y): str(_q(v)) for y, v in sorted(by_year.items())}}


def tax_depreciation_for_year(assets: list[dict], year: int) -> Decimal:
    return _dec(register(assets)["tax_depreciation_by_year"].get(str(year), "0"))


def tax_basis(assets: list[dict], through_year: int) -> dict:
    """Each asset's remaining TAX basis at the end of through_year (for the deferred roll-forward)."""
    out = {}
    for a in assets:
        sch = depreciate(a)["schedule"]
        pis = int(a.get("placed_in_service", 1))
        basis = _dec(a["cost"])
        for row in sch:
            if pis + row["year_index"] - 1 <= through_year:
                basis = _dec(row["basis_remaining"])
        out[a.get("asset", "?")] = str(_q(basis))
    return out


def render_text(d: dict) -> str:
    o = ["=" * 60, "MACRS DEPRECIATION", "-" * 60]
    for a in d["assets"]:
        o.append(f"  {a['asset'][:24]:<26} cost {_dec(a['cost']):>12,.2f}  ({a['class']}-yr)")
        for row in a["schedule"]:
            o.append(f"      yr {row['year_index']:<2} {_dec(row['depreciation']):>12,.2f}"
                     f"   basis left {_dec(row['basis_remaining']):>12,.2f}")
    o.append("-" * 60)
    o.append("  tax depreciation by year:")
    for y, v in d["tax_depreciation_by_year"].items():
        o.append(f"    {y}  {_dec(v):>14,.2f}")
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-depreciate")
    ap.add_argument("assets", help="JSON file/'-': [{asset, cost, class, placed_in_service, section179, bonus_pct}]")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    raw = sys.stdin.read() if a.assets == "-" else Path(a.assets).read_text(encoding="utf-8")
    d = register(json.loads(raw))
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

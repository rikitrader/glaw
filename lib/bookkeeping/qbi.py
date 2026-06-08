#!/usr/bin/env python3
"""GLAW QBI §199A deduction — the 20 % qualified business income deduction for pass-throughs.

Below the taxable-income threshold: a clean 20 % of QBI (no wage limit, SSTB allowed). Above the
threshold + full phase-out: the deduction is limited to the greater of 50 % of W-2 wages, or
25 % of W-2 wages + 2.5 % of UBIA — and an SSTB gets nothing. In the phase-out range the wage
limit phases in (and the SSTB amounts phase out). The whole thing is finally capped at 20 % of
(taxable income − net capital gains). Thresholds default to 2024.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
THRESHOLDS = {  # year → (single threshold, single phase-out range, MFJ threshold, MFJ range)
    2024: (Decimal("191950"), Decimal("50000"), Decimal("383900"), Decimal("100000")),
    2025: (Decimal("197300"), Decimal("50000"), Decimal("394600"), Decimal("100000")),
}


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def qbi_deduction(qbi, w2_wages, ubia, taxable_income, *, filing_status: str = "single",
                  sstb: bool = False, net_capital_gains="0", year: int = 2024) -> dict:
    qbi, w2, ubia = _dec(qbi), _dec(w2_wages), _dec(ubia)
    ti, ncg = _dec(taxable_income), _dec(net_capital_gains)
    thr_s, rng_s, thr_m, rng_m = THRESHOLDS.get(year, THRESHOLDS[2024])
    threshold, prange = (thr_m, rng_m) if filing_status == "mfj" else (thr_s, rng_s)

    tentative = _q(qbi * Decimal("0.20"))
    income_cap = _q(max(ti - ncg, Decimal("0")) * Decimal("0.20"))
    wage_limit = max(w2 * Decimal("0.50"), w2 * Decimal("0.25") + ubia * Decimal("0.025"))

    zone = "below-threshold"
    if ti <= threshold:                                       # full 20 %, SSTB allowed
        qbi_component = tentative
    elif ti >= threshold + prange:                           # fully phased in
        zone = "above-phaseout"
        if sstb:
            qbi_component = Decimal("0")
        else:
            qbi_component = min(tentative, _q(wage_limit))
    else:                                                     # phase-out range
        zone = "phase-out"
        ratio = (ti - threshold) / prange                    # 0..1
        if sstb:
            appl = Decimal("1") - ratio                       # applicable % of QBI/wages allowed
            t2 = _q(qbi * appl * Decimal("0.20"))
            wl2 = max(w2 * appl * Decimal("0.50"), (w2 * appl * Decimal("0.25") + ubia * appl * Decimal("0.025")))
            qbi_component = min(t2, _q(wl2))
        else:
            if tentative <= wage_limit:
                qbi_component = tentative
            else:
                excess = tentative - wage_limit
                qbi_component = _q(tentative - excess * ratio)

    deduction = _q(min(qbi_component, income_cap))
    return {"zone": zone, "filing_status": filing_status, "sstb": sstb,
            "tentative_20pct_qbi": str(tentative), "wage_ubia_limit": str(_q(wage_limit)),
            "income_limit_20pct": str(income_cap), "qbi_component": str(_q(qbi_component)),
            "qbi_deduction": str(deduction), "threshold": str(threshold)}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "QBI §199A DEDUCTION", "-" * 56,
        f"  zone: {d['zone']}   filing: {d['filing_status']}   SSTB: {d['sstb']}",
        f"  20% of QBI (tentative)   {_dec(d['tentative_20pct_qbi']):>16,.2f}",
        f"  W-2/UBIA limit           {_dec(d['wage_ubia_limit']):>16,.2f}",
        f"  20% of taxable income    {_dec(d['income_limit_20pct']):>16,.2f}",
        "-" * 56,
        f"  QBI DEDUCTION            {_dec(d['qbi_deduction']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-qbi")
    ap.add_argument("--qbi", required=True)
    ap.add_argument("--w2-wages", default="0")
    ap.add_argument("--ubia", default="0")
    ap.add_argument("--taxable-income", required=True)
    ap.add_argument("--filing-status", default="single", choices=["single", "mfj"])
    ap.add_argument("--sstb", action="store_true")
    ap.add_argument("--net-capital-gains", default="0")
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = qbi_deduction(a.qbi, a.w2_wages, a.ubia, a.taxable_income, filing_status=a.filing_status,
                      sstb=a.sstb, net_capital_gains=a.net_capital_gains, year=a.year)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

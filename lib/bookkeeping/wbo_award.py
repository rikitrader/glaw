#!/usr/bin/env python3
"""GLAW IRS Whistleblower award model (IRC §7623) — classifies the claim as mandatory §7623(b)
or discretionary §7623(a), and estimates the award range from collected proceeds and a
positive/negative factor profile.

§7623(b) — MANDATORY award of **15%–30%** of collected proceeds when (i) the amounts in dispute
(tax, penalties, interest, additions) exceed **$2,000,000**, and (ii) for an individual taxpayer,
the taxpayer's gross income exceeds **$200,000** for at least one year at issue. The percentage
moves within 15–30% on the positive factors (significance, assistance, value to the IRS) and is
reduced for unreasonable delay / limited contribution.
§7623(a) — DISCRETIONARY award of **up to 15%** when the (b) thresholds are not met.
Reductions: a planner/initiator of the action may have the award reduced (§7623(b)(3)); a
whistleblower convicted of planning/initiating is **denied**.
The award is paid only on **collected proceeds** (not merely assessed) and is itself **taxable**.

[VERIFY] $2,000,000 / $200,000 thresholds and the 15–30% band against current §7623 + Pub. 5251.
This is an argument-range, not a guaranteed number — the Whistleblower Office decides.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
B_PROCEEDS_THRESHOLD = Decimal("2000000")
B_INCOME_THRESHOLD = Decimal("200000")
B_LOW, B_HIGH = Decimal("0.15"), Decimal("0.30")
A_MAX = Decimal("0.15")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def award(*, collected_proceeds="0", taxpayer_gross_income="0",
          positive_factors=0, negative_factors=0, planner=False, convicted=False) -> dict:
    proceeds = _dec(collected_proceeds)
    income = _dec(taxpayer_gross_income)
    pos, neg = max(0, int(positive_factors)), max(0, int(negative_factors))

    if convicted:
        return {"track": "DENIED", "reason": "§7623(b)(3) — convicted of planning/initiating the action",
                "collected_proceeds": str(_q(proceeds)),
                "award_low": "0.00", "award_high": "0.00",
                "_verify": "conviction bars any award; confirm posture before advising."}

    qualifies_b = proceeds > B_PROCEEDS_THRESHOLD and income > B_INCOME_THRESHOLD
    if qualifies_b:
        track = "§7623(b) mandatory (15–30%)"
        # net positive factors slide within the band (each net factor ≈ 1.5 pts, capped)
        net = pos - neg
        slide = max(Decimal("0"), min(Decimal("1"), (Decimal(net) + Decimal("3")) / Decimal("6")))
        low_pct, high_pct = B_LOW, B_HIGH
        likely_pct = B_LOW + (B_HIGH - B_LOW) * slide
        if planner:
            high_pct = high_pct * Decimal("0.5")          # §7623(b)(3) reduction (rough)
            likely_pct = min(likely_pct, high_pct)
    else:
        track = "§7623(a) discretionary (up to 15%)"
        low_pct, high_pct = Decimal("0"), A_MAX
        slide = max(Decimal("0"), min(Decimal("1"), (Decimal(pos - neg) + Decimal("3")) / Decimal("6")))
        likely_pct = A_MAX * slide

    return {
        "track": track,
        "qualifies_7623b": "yes" if qualifies_b else "no",
        "collected_proceeds": str(_q(proceeds)),
        "award_pct_low": str((low_pct * 100).quantize(Decimal("0.1"))),
        "award_pct_high": str((high_pct * 100).quantize(Decimal("0.1"))),
        "award_pct_likely": str((likely_pct * 100).quantize(Decimal("0.1"))),
        "award_low": str(_q(proceeds * low_pct)),
        "award_high": str(_q(proceeds * high_pct)),
        "award_likely": str(_q(proceeds * likely_pct)),
        "planner_reduction_applied": "yes" if planner else "no",
        "_verify": "thresholds + band are §7623-current [VERIFY]; award is on COLLECTED (not assessed) proceeds and is taxable; the Whistleblower Office sets the final percentage.",
    }


def render_text(d: dict) -> str:
    if d["track"] == "DENIED":
        return "\n".join(["=" * 60, "IRS WHISTLEBLOWER AWARD — DENIED", "-" * 60,
                          f"  {d['reason']}", "=" * 60, f"  ⚠ VERIFY: {d['_verify']}"])
    return "\n".join([
        "=" * 60, "IRS WHISTLEBLOWER AWARD (§7623) — ESTIMATE", "-" * 60,
        f"  track: {d['track']}   (qualifies §7623(b): {d['qualifies_7623b']})",
        f"  collected proceeds              {_dec(d['collected_proceeds']):>16,.2f}",
        f"  award % range                   {d['award_pct_low']}% – {d['award_pct_high']}%  (likely {d['award_pct_likely']}%)",
        f"  award $ low                     {_dec(d['award_low']):>16,.2f}",
        f"  award $ likely                  {_dec(d['award_likely']):>16,.2f}",
        f"  award $ high                    {_dec(d['award_high']):>16,.2f}",
        f"  planner reduction: {d['planner_reduction_applied']}",
        "=" * 60, f"  ⚠ VERIFY: {d['_verify']}",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-wbo-award", description="IRC §7623 whistleblower award-range estimate.")
    ap.add_argument("--collected-proceeds", default="0")
    ap.add_argument("--taxpayer-gross-income", default="0", help="taxpayer's gross income (§7623(b) individual test)")
    ap.add_argument("--positive-factors", type=int, default=0, help="count: significance, assistance, value to IRS, internal-compliance use")
    ap.add_argument("--negative-factors", type=int, default=0, help="count: unreasonable delay, limited contribution, culpability")
    ap.add_argument("--planner", action="store_true", help="whistleblower planned/initiated the action (§7623(b)(3))")
    ap.add_argument("--convicted", action="store_true", help="convicted of planning/initiating → denied")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = award(collected_proceeds=a.collected_proceeds, taxpayer_gross_income=a.taxpayer_gross_income,
              positive_factors=a.positive_factors, negative_factors=a.negative_factors,
              planner=a.planner, convicted=a.convicted)
    print(json.dumps(d, indent=2) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

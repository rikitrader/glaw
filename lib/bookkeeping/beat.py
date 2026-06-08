#!/usr/bin/env python3
"""GLAW BEAT — Base Erosion and Anti-Abuse Tax (§59A) — a minimum tax on large corporations that
strip U.S. income via deductible payments to foreign related parties.

Applies only if (a) average annual gross receipts ≥ $500M (3-yr) AND (b) the base-erosion percentage
≥ 3% (2% for banks/securities dealers). Then:
  Modified Taxable Income (MTI) = taxable income + base-erosion tax benefits (the add-back of
     deductible payments to foreign related parties)
  BEAT = (MTI × BEAT rate 10%) − regular tax liability (adjusted)
The taxpayer pays the BEAT only to the extent it exceeds the regular tax.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
_PCT = Decimal("0.01")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def beat(*, taxable_income, regular_tax, base_erosion_payments, total_deductions,
         avg_gross_receipts="0", beat_rate_pct="10") -> dict:
    gr = _dec(avg_gross_receipts)
    bep = _dec(base_erosion_payments)
    deds = _dec(total_deductions)
    be_pct = (bep / deds * 100) if deds > 0 else Decimal("0")
    applies = gr >= Decimal("500000000") and be_pct >= Decimal("3")
    mti = _dec(taxable_income) + bep
    tentative = mti * _dec(beat_rate_pct) / Decimal("100")
    beat_due = max(Decimal("0"), tentative - _dec(regular_tax)) if applies else Decimal("0")
    return {"applies": applies, "base_erosion_pct": str(_q(be_pct)),
            "modified_taxable_income": str(_q(mti)),
            "tentative_minimum_tax": str(_q(tentative)),
            "beat_due": str(_q(beat_due))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "BEAT (§59A base-erosion minimum tax)", "-" * 56,
        f"  applies: {d['applies']}  (base-erosion {d['base_erosion_pct']}%)",
        f"  modified taxable income  {_dec(d['modified_taxable_income']):>16,.2f}",
        f"  tentative min tax (10%)  {_dec(d['tentative_minimum_tax']):>16,.2f}",
        f"  BEAT DUE                 {_dec(d['beat_due']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-beat")
    ap.add_argument("--taxable-income", required=True); ap.add_argument("--regular-tax", required=True)
    ap.add_argument("--base-erosion-payments", required=True); ap.add_argument("--total-deductions", required=True)
    ap.add_argument("--avg-gross-receipts", default="0"); ap.add_argument("--beat-rate-pct", default="10")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = beat(taxable_income=a.taxable_income, regular_tax=a.regular_tax,
             base_erosion_payments=a.base_erosion_payments, total_deductions=a.total_deductions,
             avg_gross_receipts=a.avg_gross_receipts, beat_rate_pct=a.beat_rate_pct)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

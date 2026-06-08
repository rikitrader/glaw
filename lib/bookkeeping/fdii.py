#!/usr/bin/env python3
"""GLAW FDII — Foreign-Derived Intangible Income (§250) — a deduction that lowers the effective
rate on a domestic C-corp's foreign-derived income from intangibles.

  Deemed Intangible Income (DII) = Deduction-Eligible Income (DEI) − 10% × QBAI
  Foreign-derived ratio = Foreign-Derived DEI / DEI
  FDII = DII × foreign-derived ratio
  §250 deduction = 37.5% × FDII (through 2025; 21.875% thereafter)  →  effective ~13.125% rate
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d): return Decimal(str(d)).quantize(_CENT, rounding=ROUND_HALF_UP)
def _dec(v):
    try: return Decimal(str(v))
    except Exception: return Decimal("0")


def fdii(*, deduction_eligible_income, foreign_derived_dei, qbai="0", sec250_pct="37.5",
         corporate_rate_pct="21") -> dict:
    dei = _dec(deduction_eligible_income)
    dii = max(Decimal("0"), dei - _dec(qbai) * Decimal("0.10"))
    ratio = (_dec(foreign_derived_dei) / dei) if dei > 0 else Decimal("0")
    fdii_amt = dii * ratio
    sec250 = fdii_amt * _dec(sec250_pct) / Decimal("100")
    tax_on_fdii = (fdii_amt - sec250) * _dec(corporate_rate_pct) / Decimal("100")
    eff_rate = (tax_on_fdii / fdii_amt * 100) if fdii_amt > 0 else Decimal("0")
    return {"deemed_intangible_income": str(_q(dii)),
            "foreign_derived_ratio_pct": str(_q(ratio * 100)),
            "fdii": str(_q(fdii_amt)), "sec250_deduction": str(_q(sec250)),
            "effective_rate_pct": str(_q(eff_rate))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "FDII (§250 deduction)", "-" * 56,
        f"  deemed intangible income {_dec(d['deemed_intangible_income']):>16,.2f}",
        f"  FDII                     {_dec(d['fdii']):>16,.2f}",
        f"  §250 deduction (37.5%)   {_dec(d['sec250_deduction']):>16,.2f}",
        f"  effective rate on FDII    {_dec(d['effective_rate_pct']):>14}%",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-fdii")
    ap.add_argument("--deduction-eligible-income", required=True)
    ap.add_argument("--foreign-derived-dei", required=True); ap.add_argument("--qbai", default="0")
    ap.add_argument("--sec250-pct", default="37.5"); ap.add_argument("--corporate-rate-pct", default="21")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = fdii(deduction_eligible_income=a.deduction_eligible_income, foreign_derived_dei=a.foreign_derived_dei,
             qbai=a.qbai, sec250_pct=a.sec250_pct, corporate_rate_pct=a.corporate_rate_pct)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

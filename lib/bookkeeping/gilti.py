#!/usr/bin/env python3
"""GLAW GILTI — Global Intangible Low-Taxed Income (§951A) + the §250 deduction + §960 FTC.

A U.S. shareholder of a CFC includes its GILTI currently:
  GILTI = net CFC tested income − Net Deemed Tangible Income Return (NDTIR)
  NDTIR = 10% × QBAI − specified tested interest expense
The §250 deduction offsets 50% of GILTI (through 2025; 37.5% thereafter), and a §960 deemed-paid
foreign tax credit is allowed on 80% of the foreign tax on the tested income. Net U.S. tax = (GILTI
− §250 deduction) × 21% − the allowed FTC.
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


def gilti(*, tested_income, qbai="0", tested_interest_expense="0", foreign_tax="0",
          sec250_pct="50", corporate_rate_pct="21", ftc_haircut_pct="80") -> dict:
    ndtir = max(Decimal("0"), _dec(qbai) * Decimal("0.10") - _dec(tested_interest_expense))
    gilti_amt = max(Decimal("0"), _dec(tested_income) - ndtir)
    sec250 = gilti_amt * _dec(sec250_pct) / Decimal("100")
    taxable = gilti_amt - sec250
    pre_credit = taxable * _dec(corporate_rate_pct) / Decimal("100")
    ftc = _dec(foreign_tax) * _dec(ftc_haircut_pct) / Decimal("100")
    net_tax = max(Decimal("0"), pre_credit - ftc)
    return {"ndtir": str(_q(ndtir)), "gilti_inclusion": str(_q(gilti_amt)),
            "sec250_deduction": str(_q(sec250)), "gilti_taxable": str(_q(taxable)),
            "pre_credit_tax": str(_q(pre_credit)), "allowed_ftc": str(_q(ftc)),
            "net_us_tax": str(_q(net_tax))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "GILTI (§951A) + §250 + §960 FTC", "-" * 56,
        f"  NDTIR (10% QBAI − int)   {_dec(d['ndtir']):>16,.2f}",
        f"  GILTI inclusion          {_dec(d['gilti_inclusion']):>16,.2f}",
        f"  §250 deduction           {_dec(d['sec250_deduction']):>16,.2f}",
        f"  allowed FTC (80%)        {_dec(d['allowed_ftc']):>16,.2f}",
        f"  NET U.S. TAX             {_dec(d['net_us_tax']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-gilti")
    ap.add_argument("--tested-income", required=True); ap.add_argument("--qbai", default="0")
    ap.add_argument("--tested-interest-expense", default="0"); ap.add_argument("--foreign-tax", default="0")
    ap.add_argument("--sec250-pct", default="50"); ap.add_argument("--corporate-rate-pct", default="21")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = gilti(tested_income=a.tested_income, qbai=a.qbai, tested_interest_expense=a.tested_interest_expense,
              foreign_tax=a.foreign_tax, sec250_pct=a.sec250_pct, corporate_rate_pct=a.corporate_rate_pct)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

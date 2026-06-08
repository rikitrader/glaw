#!/usr/bin/env python3
"""GLAW pass-through entity tax (PTET) — the SALT-cap ($10,000) workaround blessed by IRS Notice
2020-75. The pass-through (S-corp/partnership) elects to pay an entity-level state tax on its
income; that tax is a fully deductible business expense federally (bypassing the $10k SALT cap),
and each owner takes a credit on their state return for their share of the PTET paid.

PTET = pass-through income × PTET rate. Owner credit = owner's ownership % × PTET paid. Federal
benefit ≈ PTET × owner's federal marginal rate (the deduction the owners would otherwise have lost).
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


def ptet(*, pass_through_income, ptet_rate_pct, owner_share_pct="100", federal_marginal_pct="37") -> dict:
    income = _dec(pass_through_income)
    ptet_tax = income * _dec(ptet_rate_pct) / Decimal("100")
    owner_credit = ptet_tax * _dec(owner_share_pct) / Decimal("100")
    federal_benefit = ptet_tax * _dec(federal_marginal_pct) / Decimal("100")
    return {"ptet_tax": str(_q(ptet_tax)),
            "owner_credit": str(_q(owner_credit)),
            "federal_deduction_benefit": str(_q(federal_benefit)),
            "note": "PTET is deductible federally (bypasses the $10k SALT cap); owners credit their "
                    "share on the state return — net of the state credit it is roughly SALT-cap neutral "
                    "with a federal deduction upside"}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "PASS-THROUGH ENTITY TAX (PTET — SALT-cap workaround)", "-" * 56,
        f"  entity-level PTET        {_dec(d['ptet_tax']):>16,.2f}",
        f"  owner credit (state)     {_dec(d['owner_credit']):>16,.2f}",
        f"  federal deduction benefit{_dec(d['federal_deduction_benefit']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-ptet")
    ap.add_argument("--pass-through-income", required=True)
    ap.add_argument("--ptet-rate-pct", required=True)
    ap.add_argument("--owner-share-pct", default="100")
    ap.add_argument("--federal-marginal-pct", default="37")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = ptet(pass_through_income=a.pass_through_income, ptet_rate_pct=a.ptet_rate_pct,
             owner_share_pct=a.owner_share_pct, federal_marginal_pct=a.federal_marginal_pct)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

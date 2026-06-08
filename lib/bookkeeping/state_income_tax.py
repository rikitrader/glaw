#!/usr/bin/env python3
"""GLAW state corporate/personal income tax — start from federal taxable income, apply state
modifications (additions + subtractions), apply the state NOL, apportion, and apply the state rate.

State taxable income = (federal taxable income + additions − subtractions) × apportionment − state NOL.
Common additions: state income taxes deducted federally, federal bonus depreciation / §168(k),
muni-bond interest from other states. Common subtractions: federal bonus-depreciation add-back
recovery, U.S.-obligation interest, the state's DRD. State NOLs follow state rules (many states do
NOT follow the federal 80% TCJA limit — supply the state's own cap if any).
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


def state_tax(*, federal_taxable_income, additions="0", subtractions="0", apportionment_pct="100",
              state_nol="0", rate_pct, nol_limit_pct="100", min_tax="0") -> dict:
    base = _dec(federal_taxable_income) + _dec(additions) - _dec(subtractions)
    apportioned = base * _dec(apportionment_pct) / Decimal("100")
    nol_cap = apportioned * _dec(nol_limit_pct) / Decimal("100")
    nol_used = max(Decimal("0"), min(_dec(state_nol), nol_cap if apportioned > 0 else Decimal("0")))
    state_ti = max(Decimal("0"), apportioned - nol_used)
    tax = state_ti * _dec(rate_pct) / Decimal("100")
    tax = max(tax, _dec(min_tax))
    return {"state_base": str(_q(base)), "apportioned_income": str(_q(apportioned)),
            "nol_used": str(_q(nol_used)), "nol_carryforward": str(_q(max(Decimal("0"), _dec(state_nol) - nol_used))),
            "state_taxable_income": str(_q(state_ti)), "state_tax": str(_q(tax))}


def render_text(d: dict) -> str:
    return "\n".join([
        "=" * 56, "STATE INCOME TAX", "-" * 56,
        f"  apportioned income       {_dec(d['apportioned_income']):>16,.2f}",
        f"  state NOL used           {_dec(d['nol_used']):>16,.2f}",
        f"  state taxable income     {_dec(d['state_taxable_income']):>16,.2f}",
        f"  STATE TAX                {_dec(d['state_tax']):>16,.2f}",
        "=" * 56,
    ])


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-state-tax")
    ap.add_argument("--federal-taxable-income", required=True)
    ap.add_argument("--additions", default="0"); ap.add_argument("--subtractions", default="0")
    ap.add_argument("--apportionment-pct", default="100"); ap.add_argument("--state-nol", default="0")
    ap.add_argument("--rate-pct", required=True); ap.add_argument("--nol-limit-pct", default="100")
    ap.add_argument("--min-tax", default="0")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    d = state_tax(federal_taxable_income=a.federal_taxable_income, additions=a.additions,
                  subtractions=a.subtractions, apportionment_pct=a.apportionment_pct, state_nol=a.state_nol,
                  rate_pct=a.rate_pct, nol_limit_pct=a.nol_limit_pct, min_tax=a.min_tax)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

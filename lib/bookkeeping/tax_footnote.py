#!/usr/bin/env python3
"""GLAW ASC 740 income-tax footnote — the statutory-to-effective rate reconciliation and the
FIN 48 (ASC 740-10) uncertain-tax-position rollforward.

Rate reconciliation: start at pretax income × the statutory rate, then layer in the tax effect of
each reconciling item (state taxes net of federal benefit, permanent differences, credits, …) to
arrive at the total provision and the effective tax rate.

Uncertain tax positions: the tabular rollforward of unrecognized tax benefits — beginning balance
+ additions for current- and prior-year positions − settlements − lapses of the statute = ending
balance (the two-step recognition/measurement is reflected in the amounts booked).
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
_PCT = Decimal("0.01")


def _q(d: Decimal, e=_CENT) -> Decimal:
    return d.quantize(e, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def rate_reconciliation(pretax_income, statutory_rate, *, items: list | None = None) -> dict:
    pretax = _dec(pretax_income)
    rate = _dec(statutory_rate) / Decimal("100")
    statutory_tax = _q(pretax * rate)
    rows = [{"label": "Tax at statutory rate", "amount": str(statutory_tax),
             "pct": str(_q(rate * 100, _PCT))}]
    total = statutory_tax
    for it in (items or []):
        amt = _q(_dec(it["amount"]))
        total += amt
        pct = _q(amt / pretax * 100, _PCT) if pretax else Decimal("0")
        rows.append({"label": it.get("label", "?"), "amount": str(amt), "pct": str(pct)})
    total = _q(total)
    etr = _q(total / pretax * 100, _PCT) if pretax else Decimal("0")
    rows.append({"label": "Provision / effective rate", "amount": str(total), "pct": str(etr)})
    return {"pretax_income": str(_q(pretax)), "statutory_rate_pct": str(_dec(statutory_rate)),
            "statutory_tax": str(statutory_tax), "total_provision": str(total),
            "effective_rate_pct": str(etr), "reconciliation": rows}


def utp_rollforward(beginning, *, additions_current="0", additions_prior="0",
                    reductions_prior="0", settlements="0", lapses="0") -> dict:
    beg = _dec(beginning)
    add_c, add_p = _dec(additions_current), _dec(additions_prior)
    red_p, settle, lapse = _dec(reductions_prior), _dec(settlements), _dec(lapses)
    ending = _q(beg + add_c + add_p - red_p - settle - lapse)
    return {"beginning_balance": str(_q(beg)),
            "additions_current_year": str(_q(add_c)), "additions_prior_years": str(_q(add_p)),
            "reductions_prior_years": str(_q(red_p)), "settlements": str(_q(settle)),
            "lapse_of_statute": str(_q(lapse)), "ending_balance": str(ending)}


def render_text(d: dict) -> str:
    o = ["=" * 60, "INCOME TAX FOOTNOTE (ASC 740)", "-" * 60]
    if "rate_reconciliation" in d:
        rr = d["rate_reconciliation"]
        o.append("  Effective tax rate reconciliation:")
        for r in rr["reconciliation"]:
            o.append(f"    {r['label'][:36]:<38}{_dec(r['amount']):>14,.2f}{_dec(r['pct']):>8,.2f}%")
    if "utp" in d:
        u = d["utp"]
        o += ["-" * 60, "  Unrecognized tax benefits (FIN 48) rollforward:",
              f"    beginning balance      {_dec(u['beginning_balance']):>16,.2f}",
              f"    additions (current yr) {_dec(u['additions_current_year']):>16,.2f}",
              f"    additions (prior yrs)  {_dec(u['additions_prior_years']):>16,.2f}",
              f"    settlements            {_dec(u['settlements']):>16,.2f}",
              f"    lapse of statute       {_dec(u['lapse_of_statute']):>16,.2f}",
              f"    ending balance         {_dec(u['ending_balance']):>16,.2f}"]
    o.append("=" * 60)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-tax-footnote")
    ap.add_argument("--pretax", default=None, help="pretax income (for the rate reconciliation)")
    ap.add_argument("--rate", default="21", help="statutory rate %%")
    ap.add_argument("--items", default=None, help="reconciling items JSON: [{label, amount}]")
    ap.add_argument("--utp", default=None, help="UTP rollforward JSON: {beginning, additions_current, ...}")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    out = {}
    if a.pretax is not None:
        items = json.loads(a.items) if a.items else None
        out["rate_reconciliation"] = rate_reconciliation(a.pretax, a.rate, items=items)
    if a.utp:
        out["utp"] = utp_rollforward(**json.loads(a.utp))
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

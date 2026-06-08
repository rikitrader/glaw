#!/usr/bin/env python3
"""GLAW estimated tax — required quarterly installments (safe harbor) + the Form 2220/2210
underpayment penalty.

Safe harbor (the smallest amount you can pay without penalty):
  corporation (1120-W): the lesser of 100 % of the current-year tax or 100 % of the prior-year
    tax (prior-year option only if the prior year was a full 12 months and showed a tax).
  individual (1040-ES): the lesser of 90 % of the current-year tax, or 110 % of the prior-year
    tax (100 % if prior-year AGI ≤ $150k).
The required annual payment is split into four equal installments. The underpayment penalty
accrues on each quarter's shortfall from its due date to the return due date.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
# default days each quarter's underpayment is outstanding (corp due dates → 15th day of 3rd month after year-end)
DEFAULT_DAYS = [365, 306, 212, 90]


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def safe_harbor(current_tax, prior_tax, *, entity: str = "corp", high_income: bool = False) -> dict:
    cur, prior = _dec(current_tax), _dec(prior_tax)
    if entity == "individual":
        cur_req = _q(cur * Decimal("0.90"))
        prior_factor = Decimal("1.10") if high_income else Decimal("1.00")
        prior_req = _q(prior * prior_factor) if prior > 0 else None
    else:                                                     # corporation
        cur_req = _q(cur)                                     # 100 % current
        prior_req = _q(prior) if prior > 0 else None          # 100 % prior (if it showed tax)
    required = min([x for x in (cur_req, prior_req) if x is not None])
    return {"entity": entity, "current_year_requirement": str(cur_req),
            "prior_year_requirement": str(prior_req) if prior_req is not None else None,
            "required_annual_payment": str(required),
            "required_installment": str(_q(required / 4))}


def underpayment(paid: list, required_installment, rate_pct, *, days: list | None = None) -> dict:
    req = _dec(required_installment)
    rate = _dec(rate_pct) / Decimal("100")
    days = days or DEFAULT_DAYS
    rows, total = [], Decimal("0")
    for i in range(4):
        p = _dec(paid[i]) if i < len(paid) else Decimal("0")
        short = max(req - p, Decimal("0"))
        pen = _q(short * rate * Decimal(days[i]) / Decimal("365"))
        total += pen
        rows.append({"quarter": i + 1, "required": str(req), "paid": str(_q(p)),
                     "shortfall": str(_q(short)), "days": days[i], "penalty": str(pen)})
    return {"rate_pct": str(_dec(rate_pct)), "quarters": rows, "total_penalty": str(_q(total))}


def estimate(current_tax, prior_tax, *, entity="corp", high_income=False,
             paid: list | None = None, rate_pct="8", days=None) -> dict:
    sh = safe_harbor(current_tax, prior_tax, entity=entity, high_income=high_income)
    out = {"safe_harbor": sh}
    if paid is not None:
        out["underpayment"] = underpayment(paid, sh["required_installment"], rate_pct, days=days)
    return out


def render_text(d: dict) -> str:
    sh = d["safe_harbor"]
    o = ["=" * 56, "ESTIMATED TAX", "-" * 56,
         f"  entity: {sh['entity']}",
         f"  required annual payment  {_dec(sh['required_annual_payment']):>16,.2f}",
         f"  per quarter              {_dec(sh['required_installment']):>16,.2f}"]
    if "underpayment" in d:
        up = d["underpayment"]
        o.append("-" * 56)
        o.append(f"  underpayment penalty @ {up['rate_pct']}%:")
        for q in up["quarters"]:
            o.append(f"    Q{q['quarter']} short {_dec(q['shortfall']):>12,.2f}  "
                     f"penalty {_dec(q['penalty']):>10,.2f}")
        o.append(f"  total penalty            {_dec(up['total_penalty']):>16,.2f}")
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-estimated-tax")
    ap.add_argument("--current-tax", required=True)
    ap.add_argument("--prior-tax", default="0")
    ap.add_argument("--entity", default="corp", choices=["corp", "individual"])
    ap.add_argument("--high-income", action="store_true", help="(individual) prior-year AGI > $150k → 110%")
    ap.add_argument("--paid", default=None, help="JSON list of 4 quarterly payments → underpayment penalty")
    ap.add_argument("--rate", default="8", help="IRS underpayment rate %%")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    paid = json.loads(a.paid) if a.paid else None
    d = estimate(a.current_tax, a.prior_tax, entity=a.entity, high_income=a.high_income,
                 paid=paid, rate_pct=a.rate)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

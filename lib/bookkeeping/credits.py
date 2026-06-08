#!/usr/bin/env python3
"""GLAW tax credits — R&D credit (§41), foreign tax credit limitation, and the general-business-
credit limitation/ordering.

R&D (§41): Alternative Simplified Credit = 14 % of (QRE − 50 % of the average QRE of the prior
  three years), or 6 % of QRE if there is no prior QRE; the regular method = 20 % of QRE over the
  base amount. A §280C reduced-credit election multiplies the credit by (1 − corporate rate).
Foreign tax credit (§904): limited to US tax × (foreign-source income ÷ total taxable income);
  the excess carries over.
General business credit (§38): allowed up to net income tax − the greater of the tentative
  minimum tax or 25 % of net regular tax over $25,000; the excess carries over.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def rd_credit(qre, *, method: str = "asc", prior_qre_avg="0", base="0",
              reduced_280c: bool = False, corp_rate="21") -> dict:
    qre = _dec(qre)
    if method == "regular":
        gross = max(Decimal("0"), qre - _dec(base)) * Decimal("0.20")
    else:                                                     # alternative simplified credit
        avg = _dec(prior_qre_avg)
        gross = (qre * Decimal("0.06")) if avg == 0 else max(Decimal("0"), qre - avg * Decimal("0.50")) * Decimal("0.14")
    credit = _q(gross)
    if reduced_280c:
        credit = _q(credit * (Decimal("1") - _dec(corp_rate) / Decimal("100")))
    return {"method": method, "qre": str(_q(qre)), "reduced_280c": reduced_280c,
            "rd_credit": str(credit)}


def ftc(foreign_taxes_paid, foreign_source_income, total_taxable_income, us_tax) -> dict:
    paid, fsi, tti, tax = _dec(foreign_taxes_paid), _dec(foreign_source_income), _dec(total_taxable_income), _dec(us_tax)
    limit = _q(tax * fsi / tti) if tti > 0 else Decimal("0")
    allowed = _q(min(paid, limit))
    return {"foreign_taxes_paid": str(_q(paid)), "limitation": str(limit),
            "ftc_allowed": str(allowed), "carryover": str(_q(paid - allowed))}


def general_business_credit(credit, net_income_tax, tentative_min_tax="0") -> dict:
    c, nit, tmt = _dec(credit), _dec(net_income_tax), _dec(tentative_min_tax)
    floor = max(tmt, Decimal("0.25") * max(Decimal("0"), nit - Decimal("25000")))
    limit = _q(max(Decimal("0"), nit - floor))
    allowed = _q(min(c, limit))
    return {"credit": str(_q(c)), "limitation": str(limit), "gbc_allowed": str(allowed),
            "carryover": str(_q(c - allowed))}


def render_text(d: dict) -> str:
    o = ["=" * 56, "TAX CREDITS", "-" * 56]
    if "rd" in d:
        o.append(f"  R&D credit ({d['rd']['method']})  {_dec(d['rd']['rd_credit']):>16,.2f}")
    if "ftc" in d:
        o.append(f"  foreign tax credit (limit {_dec(d['ftc']['limitation']):,.0f}) "
                 f"{_dec(d['ftc']['ftc_allowed']):>14,.2f}  carryover {_dec(d['ftc']['carryover']):,.2f}")
    if "gbc" in d:
        o.append(f"  general business credit (limit {_dec(d['gbc']['limitation']):,.0f}) "
                 f"{_dec(d['gbc']['gbc_allowed']):>10,.2f}  carryover {_dec(d['gbc']['carryover']):,.2f}")
    o.append("=" * 56)
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-credits")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rd"); r.add_argument("--qre", required=True); r.add_argument("--method", default="asc", choices=["asc", "regular"])
    r.add_argument("--prior-qre-avg", default="0"); r.add_argument("--base", default="0"); r.add_argument("--reduced-280c", action="store_true")
    f = sub.add_parser("ftc"); f.add_argument("--paid", required=True); f.add_argument("--foreign-income", required=True)
    f.add_argument("--total-income", required=True); f.add_argument("--us-tax", required=True)
    g = sub.add_parser("gbc"); g.add_argument("--credit", required=True); g.add_argument("--net-income-tax", required=True); g.add_argument("--tmt", default="0")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    if a.cmd == "rd":
        out = {"rd": rd_credit(a.qre, method=a.method, prior_qre_avg=a.prior_qre_avg, base=a.base, reduced_280c=a.reduced_280c)}
    elif a.cmd == "ftc":
        out = {"ftc": ftc(a.paid, a.foreign_income, a.total_income, a.us_tax)}
    else:
        out = {"gbc": general_business_credit(a.credit, a.net_income_tax, a.tmt)}
    print(json.dumps(out, indent=2, default=str) if a.format == "json" else render_text(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

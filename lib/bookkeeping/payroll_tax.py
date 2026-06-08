#!/usr/bin/env python3
"""GLAW payroll tax engine — FICA (Social Security + Medicare), additional Medicare, the employer
match, FUTA and SUTA, plus the quarterly Form 941 totals.

Per employee, given gross wages and year-to-date wages (so the wage-base caps apply correctly):
  Social Security 6.2 % employee + 6.2 % employer, up to the SS wage base.
  Medicare 1.45 % employee + 1.45 % employer, no cap.
  Additional Medicare 0.9 % on the employee's wages over $200,000 (employee only).
  FUTA 0.6 % (net of the state credit) on the first $7,000 of wages.
  SUTA at the state rate on the state wage base (both supplied).
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
SS_WAGE_BASE = {2024: Decimal("168600"), 2025: Decimal("176100")}
FUTA_BASE = Decimal("7000")
ADDL_MEDICARE_THRESHOLD = Decimal("200000")


def _q(d: Decimal) -> Decimal:
    return d.quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _capped(gross: Decimal, ytd: Decimal, base: Decimal) -> Decimal:
    return max(Decimal("0"), min(gross, base - ytd))


def employee_taxes(gross, *, ytd_wages="0", fit_withheld="0", year: int = 2024,
                   suta_rate="0", suta_base="7000") -> dict:
    g, ytd = _dec(gross), _dec(ytd_wages)
    ss_base = SS_WAGE_BASE.get(year, SS_WAGE_BASE[2024])
    ss_wages = _capped(g, ytd, ss_base)
    futa_wages = _capped(g, ytd, FUTA_BASE)
    suta_wages = _capped(g, ytd, _dec(suta_base))
    addl_wages = max(Decimal("0"), min(g, (ytd + g) - ADDL_MEDICARE_THRESHOLD)) if (ytd + g) > ADDL_MEDICARE_THRESHOLD else Decimal("0")

    ee_ss = _q(ss_wages * Decimal("0.062"))
    ee_med = _q(g * Decimal("0.0145"))
    ee_addl = _q(addl_wages * Decimal("0.009"))
    er_ss = _q(ss_wages * Decimal("0.062"))
    er_med = _q(g * Decimal("0.0145"))
    futa = _q(futa_wages * Decimal("0.006"))
    suta = _q(suta_wages * _dec(suta_rate) / Decimal("100"))
    return {"gross": str(_q(g)), "fit_withheld": str(_q(_dec(fit_withheld))),
            "employee_ss": str(ee_ss), "employee_medicare": str(ee_med),
            "additional_medicare": str(ee_addl),
            "employer_ss": str(er_ss), "employer_medicare": str(er_med),
            "futa": str(futa), "suta": str(suta),
            "employee_total": str(_q(ee_ss + ee_med + ee_addl + _dec(fit_withheld))),
            "employer_total": str(_q(er_ss + er_med + futa + suta))}


def payroll_run(employees: list[dict], *, year: int = 2024, suta_rate="0", suta_base="7000") -> dict:
    rows = []
    tot = {"gross": Decimal("0"), "fit_withheld": Decimal("0"), "ss": Decimal("0"),
           "medicare": Decimal("0"), "futa": Decimal("0"), "suta": Decimal("0")}
    for e in employees:
        t = employee_taxes(e["gross"], ytd_wages=e.get("ytd_wages", 0),
                           fit_withheld=e.get("fit_withheld", 0), year=year,
                           suta_rate=suta_rate, suta_base=suta_base)
        t["name"] = e.get("name", "?")
        rows.append(t)
        tot["gross"] += _dec(t["gross"])
        tot["fit_withheld"] += _dec(t["fit_withheld"])
        tot["ss"] += _dec(t["employee_ss"]) + _dec(t["employer_ss"])
        tot["medicare"] += _dec(t["employee_medicare"]) + _dec(t["employer_medicare"]) + _dec(t["additional_medicare"])
        tot["futa"] += _dec(t["futa"])
        tot["suta"] += _dec(t["suta"])
    # Form 941: FIT withheld + total SS + total Medicare
    form941 = _q(tot["fit_withheld"] + tot["ss"] + tot["medicare"])
    return {"employees": rows,
            "totals": {k: str(_q(v)) for k, v in tot.items()},
            "form_941_total": str(form941)}


def render_text(d: dict) -> str:
    o = ["=" * 64, "PAYROLL TAX", "-" * 64,
         f"  {'employee':<18}{'gross':>12}{'EE SS':>10}{'EE Med':>10}{'ER SS':>10}{'FUTA':>9}"]
    for e in d["employees"]:
        o.append(f"  {e['name'][:16]:<18}{_dec(e['gross']):>12,.0f}{_dec(e['employee_ss']):>10,.2f}"
                 f"{_dec(e['employee_medicare']):>10,.2f}{_dec(e['employer_ss']):>10,.2f}{_dec(e['futa']):>9,.2f}")
    t = d["totals"]
    o += ["-" * 64,
          f"  total SS (EE+ER) {_dec(t['ss']):>16,.2f}   total Medicare {_dec(t['medicare']):>14,.2f}",
          f"  FUTA {_dec(t['futa']):>12,.2f}   SUTA {_dec(t['suta']):>12,.2f}",
          f"  FORM 941 (FIT + SS + Medicare) {_dec(d['form_941_total']):>16,.2f}", "=" * 64]
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser(prog="glaw-payroll-tax")
    ap.add_argument("employees", help="JSON file/'-': [{name, gross, ytd_wages, fit_withheld}]")
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--suta-rate", default="0", help="state unemployment rate %%")
    ap.add_argument("--suta-base", default="7000")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    a = ap.parse_args()
    import sys
    from pathlib import Path
    raw = sys.stdin.read() if a.employees == "-" else Path(a.employees).read_text(encoding="utf-8")
    d = payroll_run(json.loads(raw), year=a.year, suta_rate=a.suta_rate, suta_base=a.suta_base)
    print(json.dumps(d, indent=2, default=str) if a.format == "json" else render_text(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

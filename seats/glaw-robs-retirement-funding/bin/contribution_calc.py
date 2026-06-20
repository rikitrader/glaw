#!/usr/bin/env python3
"""Solo-401(k) / ROBS contribution + optimal-salary calculator.

Zero dependency (stdlib only) so it runs identically under Codex or Claude Code.

Two modes:
  forward  --salary N          what can be contributed at this salary/age/entity
  reverse  --target max|<int>  the salary needed to hit a target combined contribution

Examples:
  python3 contribution_calc.py --salary 120000 --age 45 --entity ccorp
  python3 contribution_calc.py --target max --age 45 --entity ccorp
  python3 contribution_calc.py --salary 90000 --age 62 --entity soleprop

ALL DOLLAR FIGURES ARE 2026 DEFAULTS, FLAGGED VERIFY. Limits are inflation-indexed
annually — confirm against the current IRS notice before any client relies on output.
Not tax advice; attorney/CPA work-product.
"""
import argparse
import sys

# --- 2026 statutory figures (VERIFY against current IRS notice) -------------
FIGURES = {
    2026: {
        "employee_deferral": 24_500,   # §402(g) elective deferral limit
        "catchup_50": 8_000,           # age 50+ catch-up
        "catchup_60_63": 11_250,       # SECURE 2.0 super catch-up (150% of regular — VERIFY)
        "annual_additions": 72_000,    # §415(c) combined cap (employee + employer)
        "comp_cap": 360_000,           # §401(a)(17) compensation cap (VERIFY)
        "employer_rate_corp": 0.25,    # 25% of W-2 comp (C-corp / S-corp)
        "employer_rate_solep": 0.20,   # ~20% of net SE income (sole prop / single-member LLC)
        "roth_ira_limit": 7_000,       # Roth-IRA annual limit (VERIFY; may index up)
        "roth_ira_catchup": 1_000,     # IRA catch-up 50+
    }
}


def catchup(age, f):
    if 60 <= age <= 63:
        return f["catchup_60_63"]
    if age >= 50:
        return f["catchup_50"]
    return 0


def employer_rate(entity, f):
    return f["employer_rate_solep"] if entity == "soleprop" else f["employer_rate_corp"]


def forward(salary, age, entity, f):
    salary = min(salary, f["comp_cap"])
    rate = employer_rate(entity, f)
    employee = min(f["employee_deferral"], salary)
    cu = catchup(age, f)
    employer = round(salary * rate)
    base_cap = f["annual_additions"]
    # catch-up sits on top of the §415(c) cap
    base_combined = min(employee + employer, base_cap, salary)
    total = base_combined + cu  # catch-up sits on top of the §415(c) cap
    return {
        "salary_used": salary,
        "employee_deferral": employee,
        "catchup": cu,
        "employer": employer,
        "combined_base": base_combined,
        "combined_total": total,
        "roth_eligible": employee + cu,  # employee deferral (+catch-up) can be designated Roth
        "capped": (employee + employer) > base_cap,
    }


def salary_to_target(target, age, entity, f):
    """Solve for the minimum salary that reaches `target` combined (base, pre-catch-up)."""
    rate = employer_rate(entity, f)
    cap = f["annual_additions"]
    target = min(target, cap)
    # employee maxes at the deferral limit; remainder must come from employer = rate * salary
    needed_employer = max(0, target - f["employee_deferral"])
    salary = needed_employer / rate if rate else 0
    # salary must also at least cover the employee deferral portion of the target
    salary = max(salary, min(target, f["employee_deferral"]))
    return min(round(salary), f["comp_cap"])


def money(n):
    return f"${n:,.0f}"


def main(argv=None):
    p = argparse.ArgumentParser(description="Solo-401(k)/ROBS contribution + optimal-salary calculator")
    p.add_argument("--salary", type=float, help="W-2 salary (corp) or net SE income (sole prop)")
    p.add_argument("--target", help="'max' or an integer combined target for reverse solve")
    p.add_argument("--age", type=int, default=40)
    p.add_argument("--entity", choices=["ccorp", "scorp", "soleprop"], default="ccorp")
    p.add_argument("--year", type=int, default=2026)
    args = p.parse_args(argv)

    if args.year not in FIGURES:
        print(f"No figures loaded for {args.year}; using 2026 (VERIFY).", file=sys.stderr)
    f = FIGURES.get(args.year, FIGURES[2026])

    print(f"=== Solo-401(k)/ROBS contributions — {args.year} (figures VERIFY vs IRS notice) ===")
    print(f"entity={args.entity}  age={args.age}  employer rate={int(employer_rate(args.entity,f)*100)}%\n")

    if args.target is not None:
        target = f["annual_additions"] if args.target == "max" else int(args.target)
        s = salary_to_target(target, args.age, args.entity, f)
        r = forward(s, args.age, args.entity, f)
        print(f"To reach a combined {money(target)} (base, pre-catch-up):")
        print(f"  minimum salary needed : {money(s)}")
        print(f"  → employee deferral   : {money(r['employee_deferral'])}")
        print(f"  → employer ({int(employer_rate(args.entity,f)*100)}%)      : {money(r['employer'])}")
        print(f"  → combined (base)     : {money(r['combined_base'])}")
        if r["catchup"]:
            print(f"  → + age catch-up      : {money(r['catchup'])}  (combined w/ catch-up {money(r['combined_total'])})")
        print(f"  → of which Roth-eligible: {money(r['roth_eligible'])}")
        return 0

    if args.salary is None:
        p.error("provide --salary (forward) or --target (reverse)")
    r = forward(args.salary, args.age, args.entity, f)
    print(f"At {money(r['salary_used'])} compensation:")
    print(f"  employee deferral        : {money(r['employee_deferral'])}")
    print(f"  employer (nonelective)   : {money(r['employer'])}")
    print(f"  combined (base, §415(c)) : {money(r['combined_base'])}" + ("  [capped at §415(c)]" if r["capped"] else ""))
    if r["catchup"]:
        print(f"  age {args.age} catch-up        : {money(r['catchup'])}  (sits on top of the cap)")
        print(f"  TOTAL with catch-up      : {money(r['combined_total'])}")
    print(f"  of which Roth-eligible   : {money(r['roth_eligible'])}  (employee deferral + catch-up)")
    print(f"\n  Roth-IRA alt (separate)  : {money(f['roth_ira_limit'] + (f['roth_ira_catchup'] if args.age>=50 else 0))} (income phase-outs apply — VERIFY)")
    cap_salary = salary_to_target(f["annual_additions"], args.age, args.entity, f)
    print(f"  salary to max §415(c)    : {money(cap_salary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

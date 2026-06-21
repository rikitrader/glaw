#!/usr/bin/env python3
"""
GLAW qualified-plan compliance checker (stdlib only).

Subcommands:
  limits   --year YYYY                          show the indexed §415/§402(g)/§401(a)(17)/§416 limits (flagged VERIFY)
  coverage --nhce-benefiting N --nhce-total N --hce-benefiting N --hce-total N
                                                §410(b) ratio-percentage test vs the 70% line
  audit    --facts path/to/facts.json           run the 21-requirement qualification matrix

All dollar figures are inflation-indexed. Confirmed years carry real IRS figures; any other year falls back to the
latest confirmed year with a loud VERIFY banner — confirm against the current IRS COLA notice before reliance.
"""
import argparse, json, sys

# Confirmed IRS cost-of-living figures. Re-pull from the IRS COLA notice each year.
# Sources: IRS Notice 2023-75 (2024), IRS Notice 2024-80 (2025), IRS Notice 2025-67 / IR-2025-111 (2026).
LIMITS = {
    2024: {
        "elective_deferral_402g": 23000,
        "catchup_age50": 7500,
        "supercatchup_age60_63": None,        # SECURE 2.0 super catch-up effective 2025
        "dc_annual_additions_415c": 69000,
        "db_annual_benefit_415b": 275000,
        "compensation_limit_401a17": 345000,
        "key_employee_officer_416": 220000,
        "hce_compensation_414q": 155000,
        "cashout_threshold_411a11": 7000,
        "auto_rollover_threshold": 1000,
    },
    2025: {
        "elective_deferral_402g": 23500,
        "catchup_age50": 7500,
        "supercatchup_age60_63": 11250,
        "dc_annual_additions_415c": 70000,
        "db_annual_benefit_415b": 280000,
        "compensation_limit_401a17": 350000,
        "key_employee_officer_416": 230000,
        "hce_compensation_414q": 160000,
        "cashout_threshold_411a11": 7000,
        "auto_rollover_threshold": 1000,
    },
    2026: {
        "elective_deferral_402g": 24500,
        "catchup_age50": 8000,
        "supercatchup_age60_63": 11250,
        "dc_annual_additions_415c": 72000,
        "db_annual_benefit_415b": 290000,
        "compensation_limit_401a17": 360000,
        "key_employee_officer_416": 235000,
        "hce_compensation_414q": 160000,
        "cashout_threshold_411a11": 7000,
        "auto_rollover_threshold": 1000,
    },
}
LATEST_CONFIRMED = max(LIMITS)

LABELS = {
    "elective_deferral_402g": "§402(g) elective deferral limit",
    "catchup_age50": "Age-50 catch-up",
    "supercatchup_age60_63": "SECURE 2.0 super catch-up (ages 60-63)",
    "dc_annual_additions_415c": "§415(c) DC annual-additions limit",
    "db_annual_benefit_415b": "§415(b) DB annual-benefit limit",
    "compensation_limit_401a17": "§401(a)(17) compensation limit",
    "key_employee_officer_416": "§416 key-employee officer threshold",
    "hce_compensation_414q": "§414(q) HCE compensation threshold",
    "cashout_threshold_411a11": "§411(a)(11) involuntary cash-out threshold",
    "auto_rollover_threshold": "Automatic-rollover threshold",
}


def get_limits(year):
    if year in LIMITS:
        return LIMITS[year], False
    return LIMITS[LATEST_CONFIRMED], True


def cmd_limits(args):
    year = args.year
    lim, fellback = get_limits(year)
    print(f"\nIndexed qualified-plan limits — requested year {year}")
    if fellback:
        print(f"  !! {year} NOT in the confirmed table. Showing {LATEST_CONFIRMED} figures as a baseline.")
        print(f"  !! VERIFY against the current IRS COLA notice (irs.gov/retirement-plans/cola-increases).")
    else:
        print(f"  (confirmed IRS figures for {year} — still re-confirm before client reliance)")
    print("  " + "-" * 60)
    for k in LABELS:
        v = lim[k]
        shown = "n/a" if v is None else f"${v:,}"
        print(f"  {LABELS[k]:<48} {shown}")
    print("\n  ALL FIGURES: VERIFY against the live IRS notice. SECURE 2.0 RMD age = 73 (rising to 75) — VERIFY band.\n")


def cmd_coverage(args):
    hce_pct = (args.hce_benefiting / args.hce_total) if args.hce_total else 0.0
    nhce_pct = (args.nhce_benefiting / args.nhce_total) if args.nhce_total else 0.0
    ratio = (nhce_pct / hce_pct) if hce_pct else float("inf")
    passes = ratio >= 0.70
    print("\n§410(b) ratio-percentage test")
    print("  " + "-" * 50)
    print(f"  NHCE benefiting: {args.nhce_benefiting}/{args.nhce_total} = {nhce_pct:.1%}")
    print(f"  HCE  benefiting: {args.hce_benefiting}/{args.hce_total} = {hce_pct:.1%}")
    print(f"  Ratio (NHCE% / HCE%): {ratio:.1%}   (line = 70%)")
    print(f"  RESULT: {'PASS' if passes else 'FAIL'} the ratio-percentage test")
    if not passes:
        print("  -> If ratio-percentage fails, test the AVERAGE BENEFIT test (nondiscriminatory")
        print("     classification + avg benefit % >= 70%) before concluding a coverage failure.")
    print()


# The 21 requirements, each with a predicate over the facts dict.
# Each predicate returns (status, note): status in {"pass","fail","needinfo"}.
def _has(facts, key):
    return facts.get(key) not in (None, "", "unknown", "UNKNOWN")


REQUIREMENTS = [
    ("1.  Minimum participation §410(a)", "min_participation_ok"),
    ("2.  Operate per plan document", "operates_per_document"),
    ("3.  No cutback §411(d)(6)", "no_cutback_ok"),
    ("4.  ADP test §401(k)", "adp_test_pass"),
    ("5.  ACP test §401(m)", "acp_test_pass"),
    ("6.  Elective deferral limit §402(g)", "deferrals_within_402g"),
    ("7.  §415 limits", "within_415_limits"),
    ("8.  §401(a)(17) compensation limit", "comp_within_401a17"),
    ("9.  Top-heavy §416", "top_heavy_satisfied"),
    ("10. Vesting §411", "vesting_schedule_ok"),
    ("11. RMD §401(a)(9)", "rmds_current"),
    ("12. Distribution consent §411(a)(11)", "distribution_consent_ok"),
    ("13. J&S annuity §401(a)(11)/§417", "qjsa_qpsa_ok"),
    ("14. Direct rollover §401(a)(31)", "direct_rollover_offered"),
    ("15. Anti-alienation §401(a)(13)", "anti_alienation_ok"),
    ("16. Nondiscrimination §401(a)(4)", "nondiscrimination_pass"),
    ("17. Coverage §410(b)", "coverage_pass"),
    ("18. DB minimum participation §401(a)(26)", "db_min_participation_ok"),
    ("19. Minimum funding §412", "minimum_funding_met"),
    ("20. Exclusive benefit / trust §401(a)", "exclusive_benefit_ok"),
    ("21. Reporting & disclosure (5500/1099-R)", "reporting_current"),
]

# Requirements that only apply to certain plan types.
DB_ONLY = {"18. DB minimum participation §401(a)(26)", "19. Minimum funding §412"}
CODA_ONLY = {"4.  ADP test §401(k)", "5.  ACP test §401(m)"}


def cmd_audit(args):
    try:
        with open(args.facts) as f:
            facts = json.load(f)
    except FileNotFoundError:
        print(f"facts file not found: {args.facts}\n  Scaffold one with bin/qp_intake.py, then fill it.", file=sys.stderr)
        sys.exit(2)

    ptype = (facts.get("plan_type") or "").lower()
    is_db = ptype in ("db", "defined-benefit", "cash-balance", "money-purchase", "pension")
    is_coda = ptype in ("401k", "403b", "coda") or facts.get("has_elective_deferrals") is True

    rows, n_pass, n_fail, n_info = [], 0, 0, 0
    for label, key in REQUIREMENTS:
        if label in DB_ONLY and not is_db:
            rows.append((label, "n/a", "DC plan — DB-only requirement"))
            continue
        if label in CODA_ONLY and not is_coda:
            rows.append((label, "n/a", "no cash-or-deferred / match — test not triggered"))
            continue
        val = facts.get(key)
        if val is True:
            rows.append((label, "PASS", "")); n_pass += 1
        elif val is False:
            rows.append((label, "FAIL", facts.get(key + "_note", "asserted non-compliant"))); n_fail += 1
        else:
            rows.append((label, "NEEDINFO", "fact not provided")); n_info += 1

    icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "NEEDINFO": "[????]", "n/a": "[ -- ]"}
    print(f"\nQualified-plan 21-requirement matrix — {facts.get('matter_name','(unnamed matter)')}")
    print(f"  plan type: {ptype or 'unknown'} | participants: {facts.get('participants','?')} | "
          f"plan-year end: {facts.get('plan_year_end','?')}")
    print("  " + "=" * 64)
    for label, status, note in rows:
        line = f"  {icon.get(status,'[?]')} {label:<42}"
        if note:
            line += f"  {note}"
        print(line)
    print("  " + "=" * 64)
    verdict = "DEFECTS-FOUND" if n_fail else ("QUALIFIED (subject to verification)" if n_info == 0 else "INCOMPLETE")
    print(f"  PASS {n_pass}  |  FAIL {n_fail}  |  NEEDINFO {n_info}")
    print(f"  VERDICT: {verdict}")
    if n_fail:
        print("  -> Route each FAIL through the EPCRS decision tree (references/correction-and-determination.md)")
    print("  -> Mandatory: §4975 / exclusive-benefit screen + /glaw-adversarial before any filed position.\n")


def main():
    p = argparse.ArgumentParser(description="GLAW qualified-plan compliance checker")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("limits"); pl.add_argument("--year", type=int, default=LATEST_CONFIRMED); pl.set_defaults(fn=cmd_limits)

    pc = sub.add_parser("coverage")
    pc.add_argument("--nhce-benefiting", type=int, required=True)
    pc.add_argument("--nhce-total", type=int, required=True)
    pc.add_argument("--hce-benefiting", type=int, required=True)
    pc.add_argument("--hce-total", type=int, required=True)
    pc.set_defaults(fn=cmd_coverage)

    pa = sub.add_parser("audit"); pa.add_argument("--facts", required=True); pa.set_defaults(fn=cmd_audit)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

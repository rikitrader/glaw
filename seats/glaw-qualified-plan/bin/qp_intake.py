#!/usr/bin/env python3
"""
GLAW qualified-plan COUNCIL INTAKE (stdlib only).

Scaffolds the whole matter system + one working file per council seat from a short set of plan facts:
  ~/.glaw/matters/<slug>/
    matter.md                                  (charter — created if missing)
    intake.json                                (qualified-plan track)
    drafts/qualified-plan/
      00-COMPLIANCE-MATRIX.md                  (the 21-requirement matrix, seeded)
      facts.json                               (predicate skeleton for qp_compliance_check.py audit)
      forms-checklist.md                       (which IRS form each seat owns)
      seats/01-plan-document-qualification.md
      seats/02-coverage-nondiscrimination.md
      seats/03-limits-top-heavy.md
      seats/04-vesting-distributions.md
      seats/05-funding-trust-fiduciary.md
      seats/06-reporting-correction.md

Usage:
  python3 qp_intake.py --matter "Acme 401(k) Qualification Audit" \
      --plan-type 401k --sponsor "Acme Inc." --plan-year-end 12-31 \
      --participants 38 --last-restatement 2022-07-31

The agent never files; this only creates work-product scaffolding for attorney/CPA review.
"""
import argparse, json, os, re, datetime

SEATS = [
    ("01-plan-document-qualification", "Plan Document & Qualification Counsel",
     ["2. Operate per plan document", "3. No cutback §411(d)(6)", "20. Exclusive benefit / trust §401(a)",
      "Plan-language currency (PPA / SECURE 2.0 restatement cycle)", "Determination letter (Form 5300/5307/8717)"],
     ["operates_per_document", "no_cutback_ok", "exclusive_benefit_ok"],
     "5300, 5307, 8717"),
    ("02-coverage-nondiscrimination", "Coverage & Nondiscrimination Analyst",
     ["1. Minimum participation §410(a)", "4. ADP test §401(k)", "5. ACP test §401(m)",
      "16. Nondiscrimination §401(a)(4)", "17. Coverage §410(b)", "18. DB minimum participation §401(a)(26)"],
     ["min_participation_ok", "adp_test_pass", "acp_test_pass", "nondiscrimination_pass", "coverage_pass",
      "db_min_participation_ok"],
     "testing memos (run qp_compliance_check.py coverage)"),
    ("03-limits-top-heavy", "Contribution/Benefit Limits & Top-Heavy Analyst",
     ["6. Elective deferral limit §402(g)", "7. §415 limits", "8. §401(a)(17) compensation limit",
      "9. Top-heavy §416"],
     ["deferrals_within_402g", "within_415_limits", "comp_within_401a17", "top_heavy_satisfied"],
     "5330 (excess contributions §4979 / nondeductible §4972)"),
    ("04-vesting-distributions", "Vesting & Distributions Counsel",
     ["10. Vesting §411", "11. RMD §401(a)(9)", "12. Distribution consent §411(a)(11)",
      "13. J&S annuity §401(a)(11)/§417", "14. Direct rollover §401(a)(31)", "15. Anti-alienation §401(a)(13)"],
     ["vesting_schedule_ok", "rmds_current", "distribution_consent_ok", "qjsa_qpsa_ok",
      "direct_rollover_offered", "anti_alienation_ok"],
     "1099-R"),
    ("05-funding-trust-fiduciary", "Funding, Trust & Fiduciary Counsel",
     ["19. Minimum funding §412", "20. Exclusive benefit / trust §401(a)",
      "ERISA fiduciary duties (prudence, diversification, disclosure)", "§4975 prohibited-transaction screen"],
     ["minimum_funding_met", "exclusive_benefit_ok"],
     "5330 (§4975 prohibited transaction / §4971 funding)"),
    ("06-reporting-correction", "Reporting & Correction Specialist",
     ["21. Reporting & disclosure (Form 5500 / 5500-EZ, 1099-R, statements)",
      "EPCRS correction path (SCP / VCP Form 8950 / Audit CAP)", "Late-5500 relief (DFVCP)"],
     ["reporting_current"],
     "5500, 5500-EZ, 8950, 1099-R"),
]

# Full predicate skeleton for the checker (audit subcommand).
PREDICATE_KEYS = [
    "min_participation_ok", "operates_per_document", "no_cutback_ok", "adp_test_pass", "acp_test_pass",
    "deferrals_within_402g", "within_415_limits", "comp_within_401a17", "top_heavy_satisfied",
    "vesting_schedule_ok", "rmds_current", "distribution_consent_ok", "qjsa_qpsa_ok", "direct_rollover_offered",
    "anti_alienation_ok", "nondiscrimination_pass", "coverage_pass", "db_min_participation_ok",
    "minimum_funding_met", "exclusive_benefit_ok", "reporting_current",
]

UPL = ("> ATTORNEY/CPA WORK-PRODUCT — a licensed ERISA attorney + CPA / enrolled actuary must review, sign, and "
       "file. The agent never amends a plan, makes a corrective distribution, or transmits to the IRS or DOL.")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "qualified-plan-matter"


def now_iso():
    # stdlib UTC timestamp; deterministic enough for a charter
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write(path, content, force=False):
    if os.path.exists(path) and not force:
        return False
    with open(path, "w") as f:
        f.write(content)
    return True


def main():
    ap = argparse.ArgumentParser(description="GLAW qualified-plan council intake / scaffolder")
    ap.add_argument("--matter", required=True, help="matter name")
    ap.add_argument("--plan-type", default="401k",
                    help="401k | db | money-purchase | profit-sharing | 403b | sep | simple")
    ap.add_argument("--sponsor", default="")
    ap.add_argument("--plan-year-end", default="12-31", help="MM-DD")
    ap.add_argument("--participants", default="")
    ap.add_argument("--last-restatement", default="", help="YYYY-MM-DD of last plan document restatement")
    ap.add_argument("--root", default=os.environ.get("GLAW_HOME", os.path.expanduser("~/.glaw")))
    args = ap.parse_args()

    slug = slugify(args.matter)
    mdir = os.path.join(args.root, "matters", slug)
    qpdir = os.path.join(mdir, "drafts", "qualified-plan")
    seatdir = os.path.join(qpdir, "seats")
    os.makedirs(seatdir, exist_ok=True)
    ts = now_iso()

    # 1. matter.md (only if missing — don't clobber an existing charter)
    matter_md = f"""---
slug: {slug}
name: {args.matter}
type: tax
workflow_track: qualified-plan
status: open
opened: {ts}
---

# Matter: {args.matter}

## Parties
- (plan sponsor) {args.sponsor}
- (plan / trust)
- (TPA / recordkeeper / enrolled actuary)

## Goal / Relief sought
Qualification audit against the 21 §401(a) requirements + correction roadmap + filing packet.

## Conflicts check
- status: PENDING   # cleared | conflict | waived  (route to /glaw-ethics-conflicts)

## Engagement
- engagement letter: PENDING
"""
    created_matter = write(os.path.join(mdir, "matter.md"), matter_md)

    # 2. intake.json (qualified-plan track)
    intake = {
        "schema_version": 1,
        "matter_slug": slug,
        "matter_name": args.matter,
        "workflow_track": "qualified-plan",
        "status": "draft",
        "created_at": ts,
        "updated_at": ts,
        "universal": {
            "matter_name": args.matter, "workflow_track": "qualified-plan",
            "client_names": [], "parties": [args.sponsor] if args.sponsor else [],
            "jurisdiction": "federal (IRC §401(a) / ERISA); DOL EFAST2",
            "goal": "Qualification audit + correction roadmap + filing packet",
            "source_documents": [], "deadlines": [], "facts_timeline": [], "open_questions": [],
            "conflicts_parties": [args.sponsor] if args.sponsor else [],
            "authorized_scope": "review/analyze/draft only; no filing without human approval",
        },
        "track_specific": {
            "qualified_plan": {
                "plan_type": args.plan_type, "plan_sponsor": args.sponsor,
                "plan_year_end": args.plan_year_end, "participant_count": args.participants,
                "last_restatement_date": args.last_restatement,
                "hce_count": "", "key_employee_count": "", "is_top_heavy": "unknown",
                "transactions_under_review": "", "distributions_in_year": "", "tpa": "",
                "determination_letter_on_file": "unknown",
            }
        },
        "review": {"completed_by": "", "completed_at": "", "notes": ""},
    }
    write(os.path.join(mdir, "intake.json"), json.dumps(intake, indent=2), force=True)

    # 3. facts.json skeleton for the checker
    facts = {"matter_name": args.matter, "plan_type": args.plan_type, "sponsor": args.sponsor,
             "plan_year_end": args.plan_year_end, "participants": args.participants,
             "has_elective_deferrals": args.plan_type in ("401k", "403b")}
    for k in PREDICATE_KEYS:
        facts[k] = None
        facts[k + "_note"] = ""
    write(os.path.join(qpdir, "facts.json"), json.dumps(facts, indent=2), force=True)

    # 4. one working file per seat
    for fname, role, reqs, keys, forms in SEATS:
        body = [f"# {role}", "", f"**Matter:** {args.matter}  ", f"**Plan type:** {args.plan_type}  ",
                f"**Forms owned:** {forms}", "", "## Assigned requirements", ""]
        for r in reqs:
            body.append(f"- [ ] {r}")
        body += ["", "## Facts to confirm (then mirror into `../facts.json`)", ""]
        for k in keys:
            body.append(f"- `{k}`: __ (true/false) — evidence: __")
        body += ["", "## Findings", "", "_(✅ pass / 🟡 needs-info / ❌ fail — with the test applied and the "
                 "evidence relied on; for each ❌ cite the EPCRS correction path)_", "",
                 "## Adversarial flags (for /glaw-adversarial)", "", "- ", "", UPL, ""]
        write(os.path.join(seatdir, fname + ".md"), "\n".join(body), force=True)

    # 5. compliance matrix + forms checklist
    matrix = ["# Qualified-Plan 21-Requirement Compliance Matrix", "",
              f"**Matter:** {args.matter} | **Plan:** {args.plan_type} | **PYE:** {args.plan_year_end} | "
              f"**Participants:** {args.participants}", "",
              "Run `python3 bin/qp_compliance_check.py audit --facts drafts/qualified-plan/facts.json` to compute.",
              "", "| # | Requirement | Owning seat | Status |", "|---|---|---|---|"]
    seat_for = {}
    for fname, role, reqs, keys, forms in SEATS:
        for r in reqs:
            seat_for.setdefault(r.split(".")[0].strip(), role)
    REQ_ROWS = [
        ("1", "Minimum participation §410(a)", "Coverage & Nondiscrimination"),
        ("2", "Operate per plan document", "Plan Document & Qualification"),
        ("3", "No cutback §411(d)(6)", "Plan Document & Qualification"),
        ("4", "ADP test §401(k)", "Coverage & Nondiscrimination"),
        ("5", "ACP test §401(m)", "Coverage & Nondiscrimination"),
        ("6", "Elective deferral limit §402(g)", "Limits & Top-Heavy"),
        ("7", "§415 limits", "Limits & Top-Heavy"),
        ("8", "§401(a)(17) compensation limit", "Limits & Top-Heavy"),
        ("9", "Top-heavy §416", "Limits & Top-Heavy"),
        ("10", "Vesting §411", "Vesting & Distributions"),
        ("11", "RMD §401(a)(9)", "Vesting & Distributions"),
        ("12", "Distribution consent §411(a)(11)", "Vesting & Distributions"),
        ("13", "J&S annuity §401(a)(11)/§417", "Vesting & Distributions"),
        ("14", "Direct rollover §401(a)(31)", "Vesting & Distributions"),
        ("15", "Anti-alienation §401(a)(13)", "Vesting & Distributions"),
        ("16", "Nondiscrimination §401(a)(4)", "Coverage & Nondiscrimination"),
        ("17", "Coverage §410(b)", "Coverage & Nondiscrimination"),
        ("18", "DB minimum participation §401(a)(26)", "Coverage & Nondiscrimination"),
        ("19", "Minimum funding §412", "Funding, Trust & Fiduciary"),
        ("20", "Exclusive benefit / trust §401(a)", "Funding, Trust & Fiduciary"),
        ("21", "Reporting & disclosure", "Reporting & Correction"),
    ]
    for num, name, seat in REQ_ROWS:
        matrix.append(f"| {num} | {name} | {seat} | ☐ |")
    matrix += ["", UPL, ""]
    write(os.path.join(qpdir, "00-COMPLIANCE-MATRIX.md"), "\n".join(matrix), force=True)

    forms_md = ["# Forms checklist — qualified-plan matter", "",
                "Blank official PDFs live in `references/forms/`. The seat maps/drafts; attorney/CPA/EA signs & files.",
                "", "| Form | Purpose | Owning seat | Status |", "|---|---|---|---|",
                "| 5500 / 5500-EZ | Annual return (req. #21) | Reporting & Correction | ☐ |",
                "| 1099-R | Distributions / rollovers | Vesting & Distributions | ☐ |",
                "| 8950 | EPCRS VCP submission | Reporting & Correction | ☐ |",
                "| 5330 | §4975 / §4971 / §4972 / §4979 excise | Funding, Trust & Fiduciary | ☐ |",
                "| 5300 / 5307 + 8717 | Determination letter + user fee | Plan Document & Qualification | ☐ |",
                "| 5310 | Determination on termination | Plan Document & Qualification | ☐ |", "", UPL, ""]
    write(os.path.join(qpdir, "forms-checklist.md"), "\n".join(forms_md), force=True)

    # 6. summary
    print(f"\n✓ Qualified-plan council scaffolded for: {args.matter}")
    print(f"  matter dir : {mdir}  ({'created matter.md' if created_matter else 'matter.md existed — kept'})")
    print(f"  council    : {qpdir}")
    print(f"  seat files : {len(SEATS)} created under seats/")
    for fname, role, *_ in SEATS:
        print(f"     - {fname}.md  ({role})")
    print("\nNext:")
    print("  1) Fill drafts/qualified-plan/facts.json (true/false per requirement) from the plan documents.")
    print("  2) python3 bin/qp_compliance_check.py limits --year <YEAR>")
    print("  3) python3 bin/qp_compliance_check.py audit --facts " + os.path.join(qpdir, "facts.json"))
    print("  4) Route conflicts -> /glaw-ethics-conflicts ; then strategy -> /glaw-qualified-plan dossier.")
    print("  5) Mandatory: /glaw-adversarial before any filed position.\n")


if __name__ == "__main__":
    main()

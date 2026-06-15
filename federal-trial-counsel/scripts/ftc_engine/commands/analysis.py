"""Analysis commands: analyze, suggest, risk, sol, draft."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

from ._shared import _load_case, _risk_bar


def cmd_analyze(args):
    """Full case analysis: suggest claims, score risk, check SOL, generate draft."""
    from ..suggest import suggest_claims
    from ..risk import calculate_mtd_risk
    from ..sol import calculate_sol
    from ..drafter import analyze_jurisdiction, generate_complaint

    case_data = _load_case(args.input)

    print("=" * 70)
    print("         FEDERAL TRIAL COUNSEL - CASE ANALYSIS")
    print("=" * 70)

    # 1. Jurisdiction
    jx = analyze_jurisdiction(case_data)
    print(f"\n## Jurisdiction")
    print(f"   Basis:     {jx.basis}")
    print(f"   Satisfied: {jx.satisfied}")
    print(f"   Analysis:  {jx.analysis}")
    print(f"   Venue:     {jx.venue_analysis}")
    print(f"   Standing:  injury={jx.standing_injury} causation={jx.standing_causation} redress={jx.standing_redressability}")

    # 2. Claim suggestions
    suggestions = suggest_claims(case_data)
    print(f"\n## Suggested Claims ({len(suggestions)})")
    for s in suggestions:
        flag = " [SHOWSTOPPERS]" if s.showstoppers else ""
        print(f"   [{s.match_score:3d}] {s.claim_key}{flag}")
        print(f"         {s.claim_name}")
        for r in s.reasons[:3]:
            print(f"         + {r}")
        for ss in s.showstoppers:
            print(f"         ! {ss}")

    # 3. Risk scoring
    claims = case_data.get("claims_requested", [])
    if not claims or claims == ["auto_suggest"]:
        claims = [s.claim_key for s in suggestions[:3] if not s.showstoppers]

    print(f"\n## MTD Risk Scores")
    for ck in claims:
        risk = calculate_mtd_risk(case_data, ck)
        bar = _risk_bar(risk.overall_score)
        print(f"   {ck}")
        print(f"     Score: {risk.overall_score}/100 [{risk.risk_level.upper()}] {bar}")
        for v in risk.top_vulnerabilities[:3]:
            print(f"     ! {v}")
        for f in risk.prioritized_fixes[:2]:
            print(f"     > {f}")

    # 4. SOL
    injury_date = case_data.get("limitations", {}).get("key_dates", {}).get("injury_date")
    if injury_date:
        print(f"\n## Statute of Limitations (injury: {injury_date})")
        for ck in claims:
            try:
                sol = calculate_sol(ck, injury_date)
                icon = {"safe": "OK", "urgent": "!!", "expired": "XX"}.get(sol.status, "??")
                print(f"   [{icon}] {ck}: {sol.days_remaining}d remaining (deadline: {sol.deadline})")
            except Exception as e:
                print(f"   [??] {ck}: {e}")

    # 5. Draft to file if output specified
    if args.output:
        complaint = generate_complaint(case_data)
        out_path = Path(args.output)
        out_path.mkdir(parents=True, exist_ok=True)

        (out_path / "complaint_draft.md").write_text(complaint)
        print(f"\n## Draft written to {out_path / 'complaint_draft.md'}")

        # Also write JSON report
        report = {
            "jurisdiction": {"basis": jx.basis, "satisfied": jx.satisfied, "analysis": jx.analysis},
            "suggestions": [{"key": s.claim_key, "score": s.match_score, "reasons": s.reasons, "showstoppers": s.showstoppers} for s in suggestions],
            "risk_scores": {ck: {"score": (r := calculate_mtd_risk(case_data, ck)).overall_score, "level": r.risk_level} for ck in claims},
            "generated": str(date.today()),
        }
        (out_path / "analysis_report.json").write_text(json.dumps(report, indent=2, default=str))
        print(f"   Report written to {out_path / 'analysis_report.json'}")

    print("\n" + "=" * 70)

    # 6. Post-generation questions
    if getattr(args, "questions", False):
        from ..questions import generate_questions, format_questions

        suggestion_dicts = [{"key": s.claim_key, "score": s.match_score, "showstoppers": s.showstoppers} for s in suggestions]
        risk_dict = {ck: {"score": calculate_mtd_risk(case_data, ck).overall_score, "level": calculate_mtd_risk(case_data, ck).risk_level} for ck in claims}

        sol_dicts = None
        if injury_date:
            sol_dicts = []
            for ck in claims:
                try:
                    sol = calculate_sol(ck, injury_date)
                    sol_dicts.append({"claim_key": ck, "status": sol.status, "days_remaining": sol.days_remaining})
                except Exception:
                    pass

        qs = generate_questions(case_data, doc_type="analyze", suggestions=suggestion_dicts, risk_scores=risk_dict, sol_results=sol_dicts)
        print(format_questions(qs, verbose=getattr(args, "verbose", False)))


def cmd_suggest(args):
    """Auto-suggest claims based on case facts."""
    from ..suggest import suggest_claims
    case_data = _load_case(args.input)
    suggestions = suggest_claims(case_data, args.max if args.max is not None else 10)

    print(f"{'Score':>5}  {'Claim Key':<45} {'Name'}")
    print("-" * 100)
    for s in suggestions:
        flag = " *" if s.showstoppers else ""
        print(f"{s.match_score:>5}  {s.claim_key:<45} {s.claim_name}{flag}")
        if args.verbose:
            for r in s.reasons:
                print(f"       + {r}")
            for ss in s.showstoppers:
                print(f"       ! {ss}")


def cmd_risk(args):
    """MTD risk scoring."""
    from ..risk import calculate_mtd_risk
    case_data = _load_case(args.input)
    claims = args.claims.split(",") if args.claims else case_data.get("claims_requested", [])

    for ck in claims:
        ck = ck.strip()
        risk = calculate_mtd_risk(case_data, ck)
        bar = _risk_bar(risk.overall_score)
        print(f"\n## {ck}")
        print(f"   Overall: {risk.overall_score}/100 [{risk.risk_level.upper()}] {bar}")
        print(f"   Factors:")
        for f in risk.factors:
            fbar = _risk_bar(f.score)
            print(f"     {f.category:<15} {f.score:>3}/100 {fbar} {f.issue}")
        if risk.prioritized_fixes:
            print(f"   Fixes:")
            for fix in risk.prioritized_fixes:
                print(f"     > {fix}")


def cmd_sol(args):
    """Statute of limitations calculator."""
    from ..sol import calculate_sol, calculate_all_sol
    claims = args.claims.split(",")
    try:
        results = calculate_all_sol([c.strip() for c in claims], args.date)
    except Exception as e:
        print(f"Error calculating SOL: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"{'Status':<8} {'Claim':<45} {'Deadline':<12} {'Remaining':>10}")
    print("-" * 80)
    for r in results:
        icon = {"safe": "OK", "urgent": "URGENT", "expired": "EXPIRED"}.get(r.status, "UNKNOWN")
        print(f"{icon:<8} {r.claim_key:<45} {r.deadline} {r.days_remaining:>7}d")
        if args.verbose:
            for note in r.tolling_notes[:2]:
                print(f"         * {note}")


def cmd_draft(args):
    """Generate complaint skeleton."""
    from ..drafter import generate_complaint
    case_data = _load_case(args.input)
    complaint = generate_complaint(case_data)

    if args.output:
        out_path = Path(args.output)
        # Treat as directory if path ends with separator, already a dir, or has no file extension
        is_dir = (
            args.output.endswith("/")
            or (out_path.exists() and out_path.is_dir())
            or out_path.suffix == ""
        )
        if is_dir:
            out_path.mkdir(parents=True, exist_ok=True)
            target = out_path / "complaint.md"
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            target = out_path
        target.write_text(complaint)
        print(f"Complaint written to {target}")
    else:
        print(complaint)

    if getattr(args, "questions", False):
        from ..questions import generate_questions, format_questions
        qs = generate_questions(case_data, doc_type="draft")
        print(format_questions(qs, verbose=getattr(args, "verbose", False)))

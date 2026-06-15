"""
Analysis-flavored MCP handlers.

Tools handled here:
  - ftc_analyze    : full case analysis (jurisdiction + claims + risk + SOL)
  - ftc_suggest    : claim suggestion ranking
  - ftc_risk       : MTD risk scoring per claim
  - ftc_sol        : statute-of-limitations calculator
  - ftc_monitor    : Rule 11 viability monitor
  - ftc_questions  : post-analysis verification questions
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


def handle_ftc_analyze(args: dict) -> dict:
    from ..suggest import suggest_claims
    from ..risk import calculate_mtd_risk
    from ..sol import calculate_sol
    from ..drafter import analyze_jurisdiction, generate_complaint

    case_data = args["case_data"]
    jx = analyze_jurisdiction(case_data)
    suggestions = suggest_claims(case_data)

    claims = case_data.get("claims_requested", [])
    if not claims or claims == ["auto_suggest"]:
        claims = [s.claim_key for s in suggestions[:3] if not s.showstoppers]

    risk_scores = {}
    for ck in claims:
        r = calculate_mtd_risk(case_data, ck)
        risk_scores[ck] = {"score": r.overall_score, "level": r.risk_level, "top_vulnerabilities": r.top_vulnerabilities[:3], "fixes": r.prioritized_fixes[:2]}

    sol_results = {}
    injury_date = case_data.get("limitations", {}).get("key_dates", {}).get("injury_date")
    if injury_date:
        for ck in claims:
            try:
                sol = calculate_sol(ck, injury_date)
                sol_results[ck] = {"status": sol.status, "deadline": str(sol.deadline), "days_remaining": sol.days_remaining}
            except Exception as e:
                sol_results[ck] = {"error": str(e)}

    result = {
        "jurisdiction": {"basis": jx.basis, "satisfied": jx.satisfied, "analysis": jx.analysis, "venue": jx.venue_analysis},
        "suggestions": [{"key": s.claim_key, "name": s.claim_name, "score": s.match_score, "reasons": s.reasons[:3], "showstoppers": s.showstoppers} for s in suggestions],
        "risk_scores": risk_scores,
        "sol": sol_results,
        "claims_analyzed": claims,
        "generated": str(date.today()),
    }

    if args.get("output_dir"):
        out = Path(args["output_dir"])
        out.mkdir(parents=True, exist_ok=True)
        complaint = generate_complaint(case_data)
        (out / "complaint_draft.md").write_text(complaint)
        (out / "analysis_report.json").write_text(json.dumps(result, indent=2, default=str))
        result["files_written"] = [str(out / "complaint_draft.md"), str(out / "analysis_report.json")]

    return result


def handle_ftc_suggest(args: dict) -> dict:
    from ..suggest import suggest_claims
    suggestions = suggest_claims(args["case_data"], args.get("max_results", 10))
    return {
        "suggestions": [
            {"key": s.claim_key, "name": s.claim_name, "score": s.match_score, "reasons": s.reasons, "showstoppers": s.showstoppers}
            for s in suggestions
        ],
        "count": len(suggestions),
    }


def handle_ftc_risk(args: dict) -> dict:
    from ..risk import calculate_mtd_risk
    results = {}
    for ck in args["claims"]:
        r = calculate_mtd_risk(args["case_data"], ck)
        results[ck] = {
            "overall_score": r.overall_score,
            "risk_level": r.risk_level,
            "factors": [{"category": f.category, "score": f.score, "issue": f.issue} for f in r.factors],
            "top_vulnerabilities": r.top_vulnerabilities,
            "prioritized_fixes": r.prioritized_fixes,
        }
    return {"risk_scores": results}


def handle_ftc_sol(args: dict) -> dict:
    from ..sol import calculate_all_sol
    results = calculate_all_sol(args["claims"], args["injury_date"])
    return {
        "results": [
            {"claim_key": r.claim_key, "status": r.status, "deadline": str(r.deadline), "days_remaining": r.days_remaining, "tolling_notes": r.tolling_notes}
            for r in results
        ],
    }


def handle_ftc_monitor(args: dict) -> dict:
    from ..rule11_monitor import generate_monitor_report, format_monitor_report
    report = generate_monitor_report(
        args["case_data"],
        claim_keys=args.get("claim_keys"),
        mode=args.get("mode", "offline"),
    )
    return {
        "report": format_monitor_report(report, verbose=True),
        "compliance": report.overall_compliance,
        "critical_flags": report.critical_flags,
        "claims_checked": report.claims_checked,
    }


def handle_ftc_questions(args: dict) -> dict:
    from ..questions import generate_questions, format_questions
    qs = generate_questions(args["case_data"], doc_type=args.get("doc_type", "analyze"))
    return {"questions": format_questions(qs, verbose=args.get("verbose", False)), "total": len(qs.questions)}

"""
Case-management MCP handlers.

Tools handled here:
  - ftc_cases         : list saved cases
  - ftc_analyze_docs  : run the doc analyzer pipeline on a case's intake_docs/
"""
from __future__ import annotations


def handle_ftc_cases(args: dict) -> dict:
    from ..case_manager import list_cases
    cases = list_cases()
    return {
        "cases": [
            {"case_number": c.case_number, "name": c.case_name, "status": c.status, "step": c.current_step, "modified": c.last_modified}
            for c in cases
        ],
        "total": len(cases),
    }


def handle_ftc_analyze_docs(args: dict) -> dict:
    from ..doc_analyzer import analyze_intake_docs, format_analysis_report
    report = analyze_intake_docs(args["case_number"])
    return {"report": format_analysis_report(report)}

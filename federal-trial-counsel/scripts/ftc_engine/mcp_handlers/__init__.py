"""
MCP tool handlers — one function per tool, grouped by theme.

Themed modules:
  - analysis.py  : ftc_analyze, ftc_suggest, ftc_risk, ftc_sol, ftc_monitor, ftc_questions
  - docs.py      : ftc_draft, ftc_export, ftc_template_list, ftc_deposition, ftc_exhibits,
                   ftc_pacer, ftc_calendar
  - reference.py : ftc_claims, ftc_info, ftc_district, ftc_district_list, ftc_doctor
  - case.py      : ftc_cases, ftc_analyze_docs

The server (mcp_server.py) imports the registry below to dispatch incoming
tools/call requests. Adding a tool means: write a handler in one of these
modules, then add it to TOOL_HANDLERS.
"""
from __future__ import annotations

from .analysis import (
    handle_ftc_analyze,
    handle_ftc_suggest,
    handle_ftc_risk,
    handle_ftc_sol,
    handle_ftc_monitor,
    handle_ftc_questions,
)
from .docs import (
    handle_ftc_draft,
    handle_ftc_export,
    handle_ftc_template_list,
    handle_ftc_deposition,
    handle_ftc_exhibits,
    handle_ftc_pacer,
    handle_ftc_calendar,
)
from .reference import (
    handle_ftc_claims,
    handle_ftc_info,
    handle_ftc_district,
    handle_ftc_district_list,
    handle_ftc_doctor,
)
from .case import (
    handle_ftc_cases,
    handle_ftc_analyze_docs,
)


TOOL_HANDLERS = {
    "ftc_analyze": handle_ftc_analyze,
    "ftc_suggest": handle_ftc_suggest,
    "ftc_risk": handle_ftc_risk,
    "ftc_sol": handle_ftc_sol,
    "ftc_draft": handle_ftc_draft,
    "ftc_claims": handle_ftc_claims,
    "ftc_info": handle_ftc_info,
    "ftc_district": handle_ftc_district,
    "ftc_district_list": handle_ftc_district_list,
    "ftc_deposition": handle_ftc_deposition,
    "ftc_exhibits": handle_ftc_exhibits,
    "ftc_pacer": handle_ftc_pacer,
    "ftc_monitor": handle_ftc_monitor,
    "ftc_calendar": handle_ftc_calendar,
    "ftc_questions": handle_ftc_questions,
    "ftc_export": handle_ftc_export,
    "ftc_cases": handle_ftc_cases,
    "ftc_analyze_docs": handle_ftc_analyze_docs,
    "ftc_doctor": handle_ftc_doctor,
    "ftc_template_list": handle_ftc_template_list,
}


__all__ = [
    "TOOL_HANDLERS",
    "handle_ftc_analyze",
    "handle_ftc_suggest",
    "handle_ftc_risk",
    "handle_ftc_sol",
    "handle_ftc_draft",
    "handle_ftc_claims",
    "handle_ftc_info",
    "handle_ftc_district",
    "handle_ftc_district_list",
    "handle_ftc_deposition",
    "handle_ftc_exhibits",
    "handle_ftc_pacer",
    "handle_ftc_monitor",
    "handle_ftc_calendar",
    "handle_ftc_questions",
    "handle_ftc_export",
    "handle_ftc_cases",
    "handle_ftc_analyze_docs",
    "handle_ftc_doctor",
    "handle_ftc_template_list",
]

"""CLI command handlers for ftc_engine, split by concern.

Each sub-module exposes `cmd_*` functions that match the dispatch table in
``ftc_engine.cli``. Shared helpers live in ``_shared``.
"""

from .analysis import cmd_analyze, cmd_suggest, cmd_risk, cmd_sol, cmd_draft
from .case import cmd_new, cmd_open, cmd_cases, cmd_analyze_docs
from .docs import cmd_export, cmd_exhibits, cmd_deposition, cmd_pacer, cmd_calendar
from .meta import cmd_claims, cmd_info, cmd_district, cmd_monitor, cmd_setup, cmd_doctor

__all__ = [
    "cmd_analyze",
    "cmd_suggest",
    "cmd_risk",
    "cmd_sol",
    "cmd_draft",
    "cmd_new",
    "cmd_open",
    "cmd_cases",
    "cmd_analyze_docs",
    "cmd_export",
    "cmd_exhibits",
    "cmd_deposition",
    "cmd_pacer",
    "cmd_calendar",
    "cmd_claims",
    "cmd_info",
    "cmd_district",
    "cmd_monitor",
    "cmd_setup",
    "cmd_doctor",
]

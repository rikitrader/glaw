#!/usr/bin/env python3
"""
Federal Trial Counsel - Local Execution CLI

Achieves 90-99% token reduction by running case analysis, claim suggestion,
risk scoring, SOL calculation, and document generation locally in Python.

Usage:
  python3 -m ftc_engine.cli <command> [options]

Commands:
  analyze    - Full case analysis from JSON input
  suggest    - Auto-suggest claims from case facts
  risk       - MTD risk scoring for specific claims
  sol        - Statute of limitations calculator
  draft      - Generate complaint skeleton
  export     - Export to court-formatted .docx (Word/Google Docs/PDF)
  claims     - List all available federal claims
  info       - Show claim metadata
  district   - Manage district configuration
  deposition - Generate deposition question outlines
  exhibits   - Generate exhibit index with authentication checklist
  pacer      - Generate PACER/ECF filing package (JS-44, summons, disclosure)
  monitor    - Rule 11 duty monitor — claim viability report
  calendar   - Generate case filing calendar / document map
  new        - Interactive case wizard (new or existing case)
  open       - Open/resume an existing case
  cases      - List all saved cases
  analyze-docs - Analyze intake documents for a case
  setup      - Configure local state; no packages are installed
  doctor     - Diagnostic health check

Flags:
  -q, --questions  Show post-generation verification questions
  -v, --verbose    Show detailed context for each question
"""
from __future__ import annotations
import argparse
import sys

from .commands import (
    cmd_analyze,
    cmd_suggest,
    cmd_risk,
    cmd_sol,
    cmd_draft,
    cmd_export,
    cmd_claims,
    cmd_info,
    cmd_district,
    cmd_deposition,
    cmd_exhibits,
    cmd_pacer,
    cmd_monitor,
    cmd_calendar,
    cmd_new,
    cmd_open,
    cmd_cases,
    cmd_analyze_docs,
    cmd_setup,
    cmd_doctor,
)


def main():
    parser = argparse.ArgumentParser(
        prog="ftc",
        description="Federal Trial Counsel - Local Execution Engine",
    )
    sub = parser.add_subparsers(dest="command", help="Command")

    # analyze
    p = sub.add_parser("analyze", help="Full case analysis")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-o", "--output", help="Output directory")
    p.add_argument("-q", "--questions", action="store_true", help="Show post-generation verification questions")
    p.add_argument("-v", "--verbose", action="store_true", help="Show detailed context for questions")

    # suggest
    p = sub.add_parser("suggest", help="Auto-suggest claims")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-m", "--max", type=int, default=10, help="Max results")
    p.add_argument("-v", "--verbose", action="store_true")

    # risk
    p = sub.add_parser("risk", help="MTD risk scoring")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-c", "--claims", help="Comma-separated claim keys")

    # sol
    p = sub.add_parser("sol", help="Statute of limitations")
    p.add_argument("-c", "--claims", required=True, help="Comma-separated claim keys")
    p.add_argument("-d", "--date", required=True, help="Injury date (YYYY-MM-DD)")
    p.add_argument("-v", "--verbose", action="store_true")

    # draft
    p = sub.add_parser("draft", help="Generate complaint")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-o", "--output", help="Output file path")
    p.add_argument("-q", "--questions", action="store_true", help="Show post-generation verification questions")
    p.add_argument("-v", "--verbose", action="store_true", help="Show detailed context for questions")

    # claims
    sub.add_parser("claims", help="List all claims")

    # export
    p = sub.add_parser("export", help="Export to .docx (Word/Google Docs/PDF)")
    p.add_argument("--draft", action="store_true", help="Export generated complaint draft")
    p.add_argument("-t", "--template", help="Template path (e.g. motions/motion_to_dismiss)")
    p.add_argument("--text", help="Path to markdown/text file to convert")
    p.add_argument("-i", "--input", help="Case JSON file (for placeholder filling)")
    p.add_argument("-o", "--output", help="Output .docx file path")
    p.add_argument("--list-templates", action="store_true", help="List all available templates")
    p.add_argument("-q", "--questions", action="store_true", help="Show post-generation verification questions")
    p.add_argument("-v", "--verbose", action="store_true", help="Show detailed context for questions")

    # info
    p = sub.add_parser("info", help="Claim metadata")
    p.add_argument("claim", help="Claim key")

    # district
    p = sub.add_parser("district", help="Manage district configuration")
    p.add_argument("action", choices=["list", "current", "set", "info"], help="Action")
    p.add_argument("code", nargs="?", help="District code (e.g., sdfl, ndcal)")
    p.add_argument("--division", help="Division within district")

    # deposition
    p = sub.add_parser("deposition", help="Generate deposition question outline")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-w", "--witness", required=True, help="Witness name")
    p.add_argument("--type", choices=["direct", "cross"], default="cross", help="Exam type")
    p.add_argument("-c", "--claims", help="Comma-separated claim keys")
    p.add_argument("-m", "--max", type=int, default=50, help="Max questions")
    p.add_argument("-o", "--output", help="Output file path")
    p.add_argument("-v", "--verbose", action="store_true")

    # exhibits
    p = sub.add_parser("exhibits", help="Generate exhibit index")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("--scan", help="Directory to scan for documents")
    p.add_argument("--numbering", choices=["alpha", "numeric", "bates"], default="alpha")
    p.add_argument("--prefix", help="Bates prefix (e.g., SMITH)")
    p.add_argument("--format", choices=["table", "detailed"], default="table")
    p.add_argument("-o", "--output", help="Output file path")

    # pacer
    p = sub.add_parser("pacer", help="Generate PACER/ECF filing package")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("--all", action="store_true", help="Generate complete filing package")
    p.add_argument("--js44", action="store_true", help="Generate JS-44 only")
    p.add_argument("--summons", action="store_true", help="Generate summonses only")
    p.add_argument("--disclosure", action="store_true", help="Generate corporate disclosures only")
    p.add_argument("-o", "--output", help="Output directory")

    # monitor
    p = sub.add_parser("monitor", help="Rule 11 duty monitor — claim viability")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("-c", "--claims", help="Comma-separated claim keys")
    p.add_argument("--mode", choices=["offline", "online"], default="offline")
    p.add_argument("-o", "--output", help="Output report file")
    p.add_argument("-v", "--verbose", action="store_true")

    # calendar
    p = sub.add_parser("calendar", help="Generate case filing calendar / document map")
    p.add_argument("-i", "--input", required=True, help="Case JSON file")
    p.add_argument("--filing-date", help="Filing date (YYYY-MM-DD, default: today)")
    p.add_argument("--district", help="District code for timing rules")
    p.add_argument("--format", choices=["table", "detailed"], default="table")
    p.add_argument("-o", "--output", help="Output file path")

    # new (wizard)
    p = sub.add_parser("new", help="Interactive case wizard")
    p.add_argument("-o", "--output", help="Override output directory")

    # open (resume)
    p = sub.add_parser("open", help="Open/resume existing case")
    p.add_argument("case_number", help="Case number (e.g., 6:24-cv-01234-ABC-DEF)")
    p.add_argument("--step", help="Jump to specific step")

    # cases (list)
    sub.add_parser("cases", help="List all saved cases")

    # analyze-docs
    p = sub.add_parser("analyze-docs", help="Analyze intake documents for a case")
    p.add_argument("case_number", help="Case number to analyze")

    # setup
    sub.add_parser("setup", help="Configure local state; no packages are installed")

    # doctor
    sub.add_parser("doctor", help="Diagnostic health check")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "analyze": cmd_analyze,
        "suggest": cmd_suggest,
        "risk": cmd_risk,
        "sol": cmd_sol,
        "draft": cmd_draft,
        "export": cmd_export,
        "claims": cmd_claims,
        "info": cmd_info,
        "district": cmd_district,
        "deposition": cmd_deposition,
        "exhibits": cmd_exhibits,
        "pacer": cmd_pacer,
        "monitor": cmd_monitor,
        "calendar": cmd_calendar,
        "new": cmd_new,
        "open": cmd_open,
        "cases": cmd_cases,
        "analyze-docs": cmd_analyze_docs,
        "setup": cmd_setup,
        "doctor": cmd_doctor,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()

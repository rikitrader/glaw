"""Case management commands: new, open, cases, analyze-docs."""
from __future__ import annotations

import sys


def cmd_new(args):
    """Interactive case wizard — new or existing case."""
    from ..wizard import start_wizard
    start_wizard()


def cmd_open(args):
    """Open/resume an existing case."""
    from ..case_manager import open_case, get_workflow_map
    from ..wizard import run_case_wizard
    try:
        state, case_data = open_case(args.case_number)
    except FileNotFoundError:
        print(f"Error: Case not found: {args.case_number}", file=sys.stderr)
        sys.exit(1)

    if args.step:
        # Jump to specific step
        if args.step in state.completed_steps:
            state.completed_steps.remove(args.step)
        state.current_step = args.step
        if args.step not in state.pending_steps:
            state.pending_steps.append(args.step)
        from ..case_manager import save_state
        save_state(state)

    print(get_workflow_map(state))
    if state.current_step != "done":
        run_case_wizard(state, case_data)
    else:
        print("\n  All steps complete. Use --step to revisit a section.\n")


def cmd_cases(args):
    """List all saved cases."""
    from ..case_manager import list_cases
    cases = list_cases()
    if not cases:
        print("  No saved cases found. Run 'python3 -m ftc_engine new' to start one.")
        return

    print("=" * 70)
    print("  SAVED CASES")
    print("=" * 70)
    for c in cases:
        print(f"  {c.case_number}")
        print(f"    Name:     {c.case_name}")
        print(f"    Status:   {c.status}")
        print(f"    Step:     {c.current_step}")
        print(f"    Modified: {c.last_modified}")
        print()


def cmd_analyze_docs(args):
    """Analyze documents in a case's intake folder."""
    from ..doc_analyzer import analyze_intake_docs, format_analysis_report
    report = analyze_intake_docs(args.case_number)
    print(format_analysis_report(report))

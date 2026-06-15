"""
Interactive Case Wizard — Step-by-step intake for new and existing federal cases.

Guides users through a 12-step workflow:
  court → plaintiffs → defendants → facts → claims → relief →
  exhaustion → limitations → goals → review → documents → generate

Usage:
  python3 -m ftc_engine.cli new       # Launch interactive wizard
  python3 -m ftc_engine.cli open X    # Resume existing case
  python3 -m ftc_engine.cli cases     # List all saved cases

Module layout:
  wizard_ui.py     — input/choice/date/yes-no prompts, banners, table printer
  wizard_state.py  — document catalog, availability filter, auto-populate merge
  wizard_steps.py  — the 12 collector functions + STEP_COLLECTORS map
  wizard.py        — start_wizard() / run_case_wizard() orchestration
"""
from __future__ import annotations

from .case_manager import (
    CaseState,
    create_case,
    open_case,
    list_cases,
    load_case_data,
    import_documents,
    get_workflow_map,
)

# Re-export UI primitives so `from ftc_engine.wizard import _prompt, ...` still works.
from .wizard_ui import (
    _prompt,
    _prompt_choice,
    _prompt_multi_choice,
    _prompt_yes_no,
    _prompt_date,
    _print_header,
    _print_table,
)

# Re-export state + pipeline helpers.
from .wizard_state import (
    AVAILABLE_DOCUMENTS,
    _filter_available_docs,
    _merge_auto_data,
    _run_doc_analysis,
    collect_document_selection,
    execute_pipeline,
    _generate_document,
)

# Re-export step collectors.
from .wizard_steps import (
    collect_court,
    collect_plaintiffs,
    collect_defendants,
    collect_facts,
    collect_claims,
    collect_relief,
    collect_exhaustion,
    collect_limitations,
    collect_goals,
    show_case_summary,
    review_case,
    STEP_COLLECTORS,
)


# ── Main wizard entry points ───────────────────────────────────────────────

def run_case_wizard(state: CaseState, case_data: dict) -> None:
    """Run the wizard from the current step onwards."""
    print(get_workflow_map(state))

    while state.current_step != "done":
        step = state.current_step
        collector = STEP_COLLECTORS.get(step)
        if collector is None:
            break

        if step == "generate":
            execute_pipeline(state, case_data)
            break
        else:
            case_data = collector(state, case_data)


def start_wizard() -> None:
    """Main wizard entry — asks new vs existing, routes accordingly."""
    _print_header("FEDERAL TRIAL COUNSEL — CASE WIZARD")

    choice = _prompt_choice("Case type", [
        "New case (start from scratch)",
        "Existing case (resume or import documents)",
    ])

    if choice.startswith("New"):
        case_number = _prompt("Case number", required=True,
                              description="e.g. 6:24-cv-01234-ABC-DEF, or 'pending' for pre-filing")
        state = create_case(case_number)
        case_data = load_case_data(case_number)

        # Document intake
        if _prompt_yes_no("Do you have documents to provide for this case?"):
            doc_path = _prompt("Path to documents folder or file", required=True)
            try:
                imported = import_documents(state.case_number, doc_path)
                print(f"  Imported {len(imported)} document(s)")
                case_data = _run_doc_analysis(state, case_data)
            except FileNotFoundError as e:
                print(f"  Warning: {e}")

        run_case_wizard(state, case_data)
    else:
        # Existing case
        cases = list_cases()
        if cases:
            print("\n  Saved cases:")
            for i, c in enumerate(cases, 1):
                print(f"    {i}. {c.case_number} — {c.case_name} [{c.status}] step={c.current_step}")

            raw = input("\n  Select case number (or enter new case number): ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(cases):
                selected = cases[int(raw) - 1]
                state, case_data = open_case(selected.case_number)
            else:
                # Treat as new case number
                try:
                    state, case_data = open_case(raw)
                except FileNotFoundError:
                    state = create_case(raw)
                    case_data = load_case_data(raw)
        else:
            print("\n  No saved cases found.")
            case_number = _prompt("Case number", required=True)
            try:
                state, case_data = open_case(case_number)
            except FileNotFoundError:
                state = create_case(case_number)
                case_data = load_case_data(case_number)

        # Document intake for existing
        if _prompt_yes_no("Do you have documents to provide?"):
            doc_path = _prompt("Path to documents folder or file", required=True)
            try:
                imported = import_documents(state.case_number, doc_path)
                print(f"  Imported {len(imported)} document(s)")
                case_data = _run_doc_analysis(state, case_data)
            except FileNotFoundError as e:
                print(f"  Warning: {e}")

        run_case_wizard(state, case_data)

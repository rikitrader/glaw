"""
Wizard state + document pipeline helpers.

Holds the catalog of generatable documents, availability filtering based on
case shape, auto-populate merging from document analysis, the document
selection step (Step 11), the per-document generation dispatcher, and the
pipeline executor (Step 12).

The core CaseState dataclass lives in case_manager.py; this module holds the
wizard-layer state: what can be generated, how to render each document, how to
merge auto-extracted intake data, and how to copy output to the user's chosen
location.
"""
from __future__ import annotations

from pathlib import Path

from .case_manager import (
    CaseState,
    save_state,
    save_case_data,
    advance_step,
    get_output_path,
)
from .wizard_ui import (
    _prompt,
    _prompt_choice,
    _prompt_multi_choice,
    _prompt_yes_no,
    _print_header,
)


# ── Document catalog ────────────────────────────────────────────────────────

AVAILABLE_DOCUMENTS = [
    {"key": "complaint", "name": "Complaint Draft"},
    {"key": "analysis", "name": "Full Case Analysis Report"},
    {"key": "js44", "name": "JS-44 Civil Cover Sheet"},
    {"key": "summons", "name": "Summons (per defendant)"},
    {"key": "disclosure", "name": "FRCP 7.1 Corporate Disclosure"},
    {"key": "calendar", "name": "Filing Calendar / Document Map"},
    {"key": "monitor", "name": "Rule 11 Monitor Report"},
    {"key": "risk", "name": "MTD Risk Scores"},
    {"key": "sol", "name": "SOL Report"},
    {"key": "exhibits", "name": "Exhibit Index"},
    {"key": "deposition", "name": "Deposition Outlines"},
    {"key": "questions", "name": "Verification Questions"},
]


def _filter_available_docs(case_data: dict) -> list[dict]:
    """Filter documents to only those possible given the case data."""
    docs = list(AVAILABLE_DOCUMENTS)
    parties = case_data.get("parties", {})
    defs = parties.get("defendants", [])
    all_parties = parties.get("plaintiffs", []) + defs

    # Corporate disclosure only if corporate parties exist
    has_corp = any(
        p.get("entity_type", "").lower() in ("corporation", "llc", "corporate")
        for p in all_parties
    )
    if not has_corp:
        docs = [d for d in docs if d["key"] != "disclosure"]

    # Deposition only if there are witnesses/defendants
    if not defs:
        docs = [d for d in docs if d["key"] != "deposition"]

    return docs


# ── Document intake / auto-populate ─────────────────────────────────────────

def _merge_auto_data(case_data: dict, auto: dict) -> None:
    """Merge auto-extracted data into case_data (in place)."""
    if "parties" in auto:
        for p in auto["parties"].get("plaintiffs", []):
            existing = [x["name"] for x in case_data.get("parties", {}).get("plaintiffs", [])]
            if p["name"] not in existing:
                case_data.setdefault("parties", {}).setdefault("plaintiffs", []).append(p)
        for d in auto["parties"].get("defendants", []):
            existing = [x["name"] for x in case_data.get("parties", {}).get("defendants", [])]
            if d["name"] not in existing:
                case_data.setdefault("parties", {}).setdefault("defendants", []).append(d)
    if "court" in auto and not case_data.get("court", {}).get("district"):
        case_data["court"] = auto["court"]


def _run_doc_analysis(state: CaseState, case_data: dict) -> dict:
    """Analyze imported documents, show report, offer auto-populate."""
    from .doc_analyzer import analyze_intake_docs, format_analysis_report

    print("\n  Analyzing documents...")
    report = analyze_intake_docs(state.case_number)
    print(format_analysis_report(report))

    if report.auto_populated and _prompt_yes_no("Apply extracted data to case?", default=True):
        _merge_auto_data(case_data, report.auto_populated)
        save_case_data(state.case_number, case_data)
        print("  Auto-extracted data applied.")

    if report.suggested_workflow != "new_case":
        from .doc_analyzer import _WORKFLOW_LABELS
        label = _WORKFLOW_LABELS.get(report.suggested_workflow, report.suggested_workflow)
        print(f"\n  Suggested workflow: {label}")
        for rec in report.recommendations:
            print(f"    -> {rec}")
        print()

    return case_data


# ── Step 11: document selection & output config ─────────────────────────────

def collect_document_selection(state: CaseState, case_data: dict) -> dict:
    """Let user select which documents to generate."""
    _print_header("STEP 11: DOCUMENT SELECTION & OUTPUT")

    available = _filter_available_docs(case_data)
    names = [d["name"] for d in available]
    # Default: select all
    preselected = list(range(1, len(names) + 1))

    selected = _prompt_multi_choice("Select documents to generate", names,
                                    preselected=preselected)
    selected_keys = []
    for sel in selected:
        for d in available:
            if d["name"] == sel:
                selected_keys.append(d["key"])
                break

    state.documents_selected = selected_keys

    # Output format
    fmt = _prompt_choice("Output format", [
        "terminal — Display output only",
        "markdown — Save as .md files",
        "docx — Court-formatted Word documents",
        "both — Markdown + Word",
    ])
    state.output_format = fmt.split(" — ")[0]

    # Save location
    home = str(Path.home())
    case_slug = state.case_number.replace(":", "-").replace("/", "-")
    loc = _prompt_choice("Save location", [
        f"desktop — {home}/Desktop/{case_slug}/",
        f"documents — {home}/Documents/{case_slug}/",
        f"case-folder — {state.case_path}/output/ (default)",
        "custom — Enter a custom path",
    ])
    loc_key = loc.split(" — ")[0]
    if loc_key == "desktop":
        state.output_location = str(Path.home() / "Desktop" / case_slug)
    elif loc_key == "documents":
        state.output_location = str(Path.home() / "Documents" / case_slug)
    elif loc_key == "custom":
        custom = _prompt("Save path", required=True,
                         description="absolute or relative path")
        state.output_location = str(Path(custom).expanduser().resolve())
    else:
        state.output_location = ""  # empty = case folder only

    save_state(state)
    advance_step(state, "documents")
    return case_data


# ── Step 12: pipeline executor ──────────────────────────────────────────────

def execute_pipeline(state: CaseState, case_data: dict) -> list[str]:
    """Generate selected documents, save to case folder, display progress."""
    import shutil

    _print_header("STEP 12: GENERATING DOCUMENTS")
    selected = state.documents_selected
    fmt = state.output_format
    generated: list[str] = []
    total = len(selected)

    for i, key in enumerate(selected, 1):
        label = next((d["name"] for d in AVAILABLE_DOCUMENTS if d["key"] == key), key)
        print(f"\n  [{i}/{total}] {label}...", end=" ", flush=True)

        try:
            text = _generate_document(key, case_data, state)
            if text:
                # Save to disk if not terminal-only
                if fmt in ("markdown", "both"):
                    out = get_output_path(state.case_number, key)
                    out_md = out.with_suffix(".md")
                    out_md.write_text(text)
                    generated.append(str(out_md))

                if fmt in ("docx", "both"):
                    try:
                        from .exporter import export_text
                        out = get_output_path(state.case_number, key)
                        out_docx = str(out.with_suffix(".docx"))
                        export_text(text, out_docx)
                        generated.append(out_docx)
                    except Exception:
                        pass  # docx export is optional

                if fmt == "terminal":
                    print("done")
                    print(text)
                else:
                    print("done")
            else:
                print("skipped (no output)")
        except Exception as e:
            print(f"ERROR: {e}")

    advance_step(state, "generate")

    # Copy files to user's chosen location if set
    copied: list[str] = []
    if state.output_location and generated:
        dest = Path(state.output_location)
        dest.mkdir(parents=True, exist_ok=True)
        for src_path in generated:
            src = Path(src_path)
            dst = dest / src.name
            shutil.copy2(src, dst)
            copied.append(str(dst))

    # Summary
    _print_header("GENERATION COMPLETE")
    print(f"\n  Generated {len(generated)} file(s):")
    for g in generated:
        print(f"    → {g}")

    if copied:
        print(f"\n  Also saved to: {state.output_location}")
        for c in copied:
            print(f"    → {c}")

    print(f"\n  Case folder: {state.case_path}")
    print()

    return generated


def _generate_document(key: str, case_data: dict, state: CaseState) -> str:
    """Generate a single document by key. Returns formatted text."""
    if key == "complaint":
        from .drafter import generate_complaint
        return generate_complaint(case_data)

    elif key == "analysis":
        from .suggest import suggest_claims
        from .risk import calculate_mtd_risk
        from .sol import calculate_sol
        from .drafter import analyze_jurisdiction

        lines: list[str] = []
        lines.append("=" * 70)
        lines.append("  FULL CASE ANALYSIS REPORT")
        lines.append("=" * 70)

        jx = analyze_jurisdiction(case_data)
        lines.append(f"\n  Jurisdiction: {jx.basis}")
        lines.append(f"  Venue: {jx.venue}")

        suggestions = suggest_claims(case_data)
        lines.append(f"\n  Suggested Claims ({len(suggestions)}):")
        for s in suggestions:
            lines.append(f"    [{s.score:.0f}] {s.claim_key}")

        claims = case_data.get("claims_requested", [])
        if claims and claims != ["auto_suggest"]:
            lines.append("\n  MTD Risk Scores:")
            for c in claims:
                r = calculate_mtd_risk(case_data, c)
                lines.append(f"    {c}: {r.overall_score}/100")

        injury = case_data.get("limitations", {}).get("key_dates", {}).get("injury_date")
        if injury and claims:
            lines.append("\n  SOL Check:")
            for c in claims:
                if c == "auto_suggest":
                    continue
                sol = calculate_sol(c, injury)
                lines.append(f"    {c}: {sol.days_remaining}d remaining ({sol.status})")

        return "\n".join(lines)

    elif key == "js44":
        from .pacer_meta import generate_js44, format_js44
        return format_js44(generate_js44(case_data))

    elif key == "summons":
        from .pacer_meta import generate_summons, format_summons
        defs = case_data.get("parties", {}).get("defendants", [])
        parts: list[str] = []
        for idx in range(len(defs)):
            s = generate_summons(case_data, idx)
            parts.append(format_summons(s))
        return "\n\n".join(parts)

    elif key == "disclosure":
        from .pacer_meta import generate_corporate_disclosure
        parties = case_data.get("parties", {})
        all_p = parties.get("plaintiffs", []) + parties.get("defendants", [])
        corp = [p for p in all_p
                if p.get("entity_type", "").lower() in ("corporation", "llc", "corporate")]
        if not corp:
            return ""
        parts = []
        for p in corp:
            cd = generate_corporate_disclosure(case_data, p)
            parts.append(f"  FRCP 7.1 Disclosure: {cd.party_name}\n"
                         f"  Parent: {cd.parent_corporation}\n"
                         f"  10%+ Holder: {cd.publicly_held_10pct}")
        return "\n\n".join(parts)

    elif key == "calendar":
        from .filing_calendar import generate_filing_calendar, format_filing_calendar
        cal = generate_filing_calendar(case_data)
        return format_filing_calendar(cal)

    elif key == "monitor":
        from .rule11_monitor import generate_monitor_report, format_monitor_report
        report = generate_monitor_report(case_data)
        return format_monitor_report(report, verbose=True)

    elif key == "risk":
        from .risk import calculate_mtd_risk
        claims = case_data.get("claims_requested", [])
        lines = ["  MTD RISK SCORES", "  " + "-" * 40]
        for c in claims:
            if c == "auto_suggest":
                continue
            r = calculate_mtd_risk(case_data, c)
            lines.append(f"    {c}: {r.overall_score}/100")
        return "\n".join(lines) if len(lines) > 2 else ""

    elif key == "sol":
        from .sol import calculate_sol
        injury = case_data.get("limitations", {}).get("key_dates", {}).get("injury_date")
        claims = case_data.get("claims_requested", [])
        if not injury or not claims:
            return ""
        lines = ["  STATUTE OF LIMITATIONS REPORT", "  " + "-" * 40]
        for c in claims:
            if c == "auto_suggest":
                continue
            result = calculate_sol(c, injury)
            lines.append(f"    {c}: {result.days_remaining}d remaining "
                         f"({result.status}) — deadline {result.deadline}")
        return "\n".join(lines) if len(lines) > 2 else ""

    elif key == "exhibits":
        from .exhibits import generate_exhibit_index, format_exhibit_index
        idx = generate_exhibit_index(case_data)
        return format_exhibit_index(idx, fmt="detailed")

    elif key == "deposition":
        from .deposition import generate_deposition_outline, format_deposition_outline
        defs = case_data.get("parties", {}).get("defendants", [])
        parts = []
        for d in defs:
            outline = generate_deposition_outline(
                case_data, witness_name=d["name"], exam_type="cross")
            parts.append(format_deposition_outline(outline, verbose=True))
        return "\n\n".join(parts)

    elif key == "questions":
        from .questions import generate_questions, format_questions
        qs = generate_questions(case_data)
        return format_questions(qs, verbose=True)

    return ""

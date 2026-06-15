"""
Document Analyzer — Intake, Parse, Classify, and Route legal documents.

Reads user-provided documents (PDF, DOCX, TXT), classifies them as legal
document types, extracts parties/dates/claims/court info, and auto-routes
to the correct workflow.

Layers:
  1. Text Extraction   — read_document()                 (doc_extraction.py)
  2. Classification     — classify_legal_document()       (doc_extraction.py)
  3. Entity Extraction  — extract_parties(), etc.         (doc_extraction.py)
  4. Analysis Pipeline  — analyze_document(), analyze_intake_docs()  (this file)
  5. Workflow Routing   — determine_workflow(), build_auto_populated_data()
                          (doc_routing.py)

This module is the public barrel: `from ftc_engine.doc_analyzer import ...`
re-exports every name the rest of the codebase expects.

Usage:
  from ftc_engine.doc_analyzer import analyze_intake_docs, format_analysis_report
  report = analyze_intake_docs("6:24-cv-01234")
  print(format_analysis_report(report))
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

# Re-export Layers 1-3 (extraction) so external imports keep working.
from .doc_extraction import (
    ExtractedEntity,
    DocumentAnalysis,
    IntakeAnalysisReport,
    SUPPORTED_EXTENSIONS,
    LEGAL_DOCUMENT_CATEGORIES,
    read_pdf,
    read_docx,
    read_text,
    read_document,
    classify_legal_document,
    extract_parties,
    extract_dates,
    extract_case_number,
    extract_claims,
    extract_court,
)

# Re-export Layer 5 (routing) so external imports keep working.
from .doc_routing import (
    WORKFLOW_ROUTING,
    _WORKFLOW_LABELS,
    determine_workflow,
    build_auto_populated_data,
    generate_recommendations,
)


# ── Layer 4: Analysis Pipeline ────────────────────────────────────────────

def analyze_document(file_path: Path) -> DocumentAnalysis:
    """Analyze a single document: read, classify, extract entities."""
    analysis = DocumentAnalysis(
        filename=file_path.name,
        file_path=str(file_path),
        document_category="other",
        confidence_score=0.0,
        extracted_text="",
        text_length=0,
    )

    try:
        text = read_document(file_path)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError, ValueError) as e:
        analysis.errors.append(f"Read error: {e}")
        return analysis

    analysis.extracted_text = text[:5000]
    analysis.text_length = len(text)

    # Classify
    cat, conf = classify_legal_document(text, file_path.name)
    analysis.document_category = cat
    analysis.confidence_score = conf

    # Extract entities
    analysis.parties = extract_parties(text)
    analysis.dates = extract_dates(text)
    analysis.case_numbers = extract_case_number(text)
    analysis.claims = extract_claims(text)
    analysis.courts = extract_court(text)

    # Key phrases (top keywords found)
    phrases: list[str] = []
    if cat in LEGAL_DOCUMENT_CATEGORIES:
        text_lower = text.lower()
        for kw in LEGAL_DOCUMENT_CATEGORIES[cat]:
            if kw in text_lower and kw not in phrases:
                phrases.append(kw)
    analysis.key_phrases = phrases[:10]

    return analysis


def analyze_intake_docs(case_number: str) -> IntakeAnalysisReport:
    """Analyze all documents in a case's intake_docs/ folder."""
    from .case_manager import get_case_path

    intake_dir = get_case_path(case_number) / "intake_docs"
    report = IntakeAnalysisReport(
        case_number=case_number,
        analyzed_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total_documents=0,
        successful_analyses=0,
        failed_analyses=0,
    )

    if not intake_dir.exists():
        report.recommendations.append("No intake_docs folder found. Import documents first.")
        return report

    files = [
        f for f in sorted(intake_dir.rglob("*"))
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    report.total_documents = len(files)

    if not files:
        report.recommendations.append("No supported documents found. Supported: PDF, DOCX, TXT, MD")
        return report

    for fpath in files:
        analysis = analyze_document(fpath)
        report.documents.append(analysis)
        if analysis.errors:
            report.failed_analyses += 1
        else:
            report.successful_analyses += 1

    # Determine workflow and build auto-populated data
    report.suggested_workflow = determine_workflow(report.documents)
    report.auto_populated = build_auto_populated_data(report.documents)
    report.recommendations = generate_recommendations(report.documents)

    return report


# ── Formatting ─────────────────────────────────────────────────────────────

def format_analysis_report(report: IntakeAnalysisReport) -> str:
    """Format the analysis report for CLI display."""
    lines: list[str] = []
    sep = "\u2550" * 70  # ═

    lines.append("")
    lines.append(f"  {sep}")
    lines.append("    DOCUMENT ANALYSIS REPORT")
    lines.append(f"  {sep}")
    lines.append(f"    Case:     {report.case_number}")
    lines.append(f"    Analyzed: {report.analyzed_at}")
    lines.append(f"    Total:    {report.total_documents} documents")
    lines.append(f"    Success:  {report.successful_analyses}  |  Failed: {report.failed_analyses}")
    lines.append("")

    if report.documents:
        lines.append(f"    {'File':<30} {'Category':<25} {'Conf.':<8} {'Entities'}")
        lines.append("    " + "-" * 66)
        for doc in report.documents:
            entity_count = (
                len(doc.parties) + len(doc.dates) + len(doc.case_numbers)
                + len(doc.claims) + len(doc.courts)
            )
            conf_pct = f"{doc.confidence_score:.0%}"
            err = " [ERR]" if doc.errors else ""
            lines.append(
                f"    {doc.filename[:30]:<30} {doc.document_category:<25} {conf_pct:<8} {entity_count}{err}"
            )

    if report.auto_populated:
        lines.append("")
        lines.append("    AUTO-EXTRACTED DATA:")
        if "parties" in report.auto_populated:
            p = report.auto_populated["parties"]
            if p.get("plaintiffs"):
                names = ", ".join(x["name"] for x in p["plaintiffs"])
                lines.append(f"      Plaintiffs: {names}")
            if p.get("defendants"):
                names = ", ".join(x["name"] for x in p["defendants"])
                lines.append(f"      Defendants: {names}")
        if "court" in report.auto_populated:
            lines.append(f"      Court:      {report.auto_populated['court'].get('district', '')}")
        if "claims_extracted" in report.auto_populated:
            lines.append(f"      Claims:     {', '.join(report.auto_populated['claims_extracted'])}")
        if "case_numbers_extracted" in report.auto_populated:
            lines.append(f"      Case No.:   {', '.join(report.auto_populated['case_numbers_extracted'])}")

    # Workflow suggestion
    wf_label = _WORKFLOW_LABELS.get(report.suggested_workflow, report.suggested_workflow)
    lines.append("")
    lines.append(f"    SUGGESTED WORKFLOW: {wf_label}")

    if report.recommendations:
        lines.append("")
        lines.append("    RECOMMENDATIONS:")
        for rec in report.recommendations:
            lines.append(f"      -> {rec}")

    lines.append("")
    lines.append(f"  {sep}")
    lines.append("")

    return "\n".join(lines)

"""
Document Extraction — Layers 1-3 of the document analysis pipeline.

Layer 1: Text Extraction       — read_document(), read_pdf(), read_docx(), read_text()
Layer 2: Classification         — classify_legal_document(), LEGAL_DOCUMENT_CATEGORIES
Layer 3: Entity Extraction      — extract_parties(), extract_dates(), extract_case_number(),
                                   extract_claims(), extract_court()

Dataclasses (ExtractedEntity, DocumentAnalysis, IntakeAnalysisReport) live here so they
can be shared across the pipeline without circular imports.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class ExtractedEntity:
    entity_type: str    # "plaintiff", "defendant", "date", "case_number", "court", "claim"
    value: str
    confidence: float   # 0.0–1.0
    context: str        # surrounding text snippet


@dataclass
class DocumentAnalysis:
    filename: str
    file_path: str
    document_category: str     # from LEGAL_DOCUMENT_CATEGORIES
    confidence_score: float
    extracted_text: str        # first 5000 chars
    text_length: int
    parties: list[ExtractedEntity] = field(default_factory=list)
    dates: list[ExtractedEntity] = field(default_factory=list)
    case_numbers: list[ExtractedEntity] = field(default_factory=list)
    claims: list[ExtractedEntity] = field(default_factory=list)
    courts: list[ExtractedEntity] = field(default_factory=list)
    key_phrases: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class IntakeAnalysisReport:
    case_number: str
    analyzed_at: str
    total_documents: int
    successful_analyses: int
    failed_analyses: int
    documents: list[DocumentAnalysis] = field(default_factory=list)
    suggested_workflow: str = "new_case"
    auto_populated: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


# ── Layer 1: Text Extraction ──────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


def read_pdf(path: Path) -> str:
    """PDF text extraction is intentionally unavailable in zero-dependency mode."""
    raise ValueError("PDF text extraction requires a third-party parser; convert to .txt/.md first")


def read_docx(path: Path) -> str:
    """Extract text from a DOCX file."""
    from docx import Document
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def read_text(path: Path) -> str:
    """Read plain text or markdown files."""
    return path.read_text(encoding="utf-8", errors="replace")


def read_document(path: Path) -> str:
    """Read any supported document format. Dispatches by extension."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    elif ext in (".docx", ".doc"):
        return read_docx(path)
    elif ext in (".txt", ".md"):
        return read_text(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── Layer 2: Legal Document Classification ────────────────────────────────

LEGAL_DOCUMENT_CATEGORIES: dict[str, list[str]] = {
    # Evidence types (aligned with exhibits.py)
    "medical_records": [
        "medical", "hospital", "doctor", "nurse", "diagnosis", "treatment",
        "radiology", "x-ray", "mri", "emergency room", "discharge", "prescription",
    ],
    "police_report": [
        "police", "arrest", "incident report", "use of force", "booking",
        "officer", "body camera", "body cam", "dash cam", "patrol",
    ],
    "financial": [
        "invoice", "receipt", "bank", "check", "payment", "billing", "wage",
        "payroll", "w-2", "tax return", "1099",
    ],
    "correspondence": [
        "letter", "email", "correspondence", "memo", "notice", "demand letter",
    ],
    "photograph": [
        "photo", "image", "picture", "screenshot", "photograph",
    ],
    "employment": [
        "termination", "evaluation", "performance", "handbook", "policy",
        "job description", "offer letter", "employment agreement",
    ],
    "government_record": [
        "foia", "public record", "certificate", "license", "permit",
        "government", "agency", "eeoc", "charge of discrimination",
    ],
    "contract": [
        "contract", "agreement", "lease", "deed", "settlement", "release",
    ],

    # Legal procedural documents (NEW — extends exhibits.py)
    "complaint": [
        "complaint", "civil complaint", "comes now", "jurisdiction",
        "cause of action", "count i", "prayer for relief", "wherefore",
        "plaintiff respectfully", "this action arises",
    ],
    "answer": [
        "answer", "affirmative defense", "general denial", "admits", "denies",
        "defendant answers", "first affirmative defense",
    ],
    "motion_dismiss": [
        "motion to dismiss", "12(b)(6)", "rule 12(b)", "failure to state",
        "plausibility", "iqbal", "twombly", "12(b)(1)",
    ],
    "motion_summary_judgment": [
        "summary judgment", "rule 56", "no genuine issue",
        "material fact", "undisputed", "statement of undisputed facts",
    ],
    "motion_other": [
        "motion to", "motion for", "memorandum in support",
        "respectfully moves", "good cause",
    ],
    "discovery_request": [
        "interrogatories", "request for production", "rfp", "rfa",
        "request for admission", "you are requested", "rule 33", "rule 34",
    ],
    "court_order": [
        "it is ordered", "the court orders", "so ordered",
        "scheduling order", "show cause", "hereby orders",
    ],
    "subpoena": [
        "subpoena", "subpoena duces tecum", "command", "appear and testify",
    ],
    "notice": [
        "notice of removal", "notice of appeal", "notice of filing",
        "hereby give notice", "notice is hereby given",
    ],
    "deposition_transcript": [
        "deposition", "transcript", "testimony", "q.", "a.",
        "direct examination", "cross examination",
    ],
}


_GENERIC_CATEGORIES = {"motion_other"}


def classify_legal_document(text: str, filename: str = "") -> tuple[str, float]:
    """Classify document text into a legal category.

    Returns (category, confidence) where confidence is 0.0–1.0.
    Scoring: keyword count in text + 2x bonus for filename matches.
    Generic catch-all categories (motion_other) only win if no specific
    category scored at all.
    """
    text_lower = text.lower()
    fn_lower = filename.lower()

    best_cat = "other"
    best_score = 0
    best_generic_cat = "other"
    best_generic_score = 0

    for category, keywords in LEGAL_DOCUMENT_CATEGORIES.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += 1
            if kw in fn_lower:
                score += 2  # filename match is strong signal
        if category in _GENERIC_CATEGORIES:
            if score > best_generic_score:
                best_generic_score = score
                best_generic_cat = category
        else:
            if score > best_score:
                best_score = score
                best_cat = category

    # Prefer specific match; fall back to generic only when nothing specific scored
    if best_score == 0 and best_generic_score > 0:
        best_cat = best_generic_cat
        best_score = best_generic_score

    confidence = min(1.0, best_score / 10.0)
    return best_cat, confidence


# ── Layer 3: Entity Extraction (regex, no ML) ─────────────────────────────

def _snippet(text: str, match: re.Match, window: int = 60) -> str:
    """Extract a text snippet around a regex match."""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    return text[start:end].replace("\n", " ").strip()


def extract_parties(text: str) -> list[ExtractedEntity]:
    """Extract plaintiff/defendant names from document text."""
    entities: list[ExtractedEntity] = []

    # Pattern: "Name v. Name" or "Name vs. Name"
    # Length capped at {0,80} to prevent regex backtracking on long inputs
    vs_pat = re.compile(
        r"([A-Z][A-Za-z\s,.']{0,80}?)\s+(?:v\.|vs\.?)\s+([A-Z][A-Za-z\s,.']{0,80}?)(?:[,\n;]|$)",
        re.MULTILINE,
    )
    for m in vs_pat.finditer(text):
        p_name = m.group(1).strip().rstrip(",")
        d_name = m.group(2).strip().rstrip(",")
        if len(p_name) > 2 and len(d_name) > 2:
            entities.append(ExtractedEntity("plaintiff", p_name, 0.8, _snippet(text, m)))
            entities.append(ExtractedEntity("defendant", d_name, 0.8, _snippet(text, m)))

    # Pattern: "Plaintiff: Name" or "Defendant: Name"
    role_pat = re.compile(
        r"(plaintiff|defendant)[s]?\s*[:]\s*([A-Z][A-Za-z\s,.']{0,80}?)(?:\n|$)",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in role_pat.finditer(text):
        role = m.group(1).lower().rstrip("s")
        name = m.group(2).strip().rstrip(",")
        if len(name) > 2:
            entities.append(ExtractedEntity(role, name, 0.7, _snippet(text, m)))

    return entities


def extract_dates(text: str) -> list[ExtractedEntity]:
    """Extract dates in various formats from text."""
    entities: list[ExtractedEntity] = []
    seen: set[str] = set()

    patterns = [
        (r"\b(\d{4}-\d{2}-\d{2})\b", "ISO"),
        (r"\b(\d{2}/\d{2}/\d{4})\b", "US"),
        (r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b", "written"),
    ]

    for pat, fmt_name in patterns:
        for m in re.finditer(pat, text):
            val = m.group(1)
            if val not in seen:
                seen.add(val)
                entities.append(ExtractedEntity("date", val, 0.9, _snippet(text, m)))

    return entities


def extract_case_number(text: str) -> list[ExtractedEntity]:
    """Extract federal case numbers (e.g. Case No. 6:24-cv-01234)."""
    entities: list[ExtractedEntity] = []
    seen: set[str] = set()

    pat = re.compile(
        r"(?:Case\s+(?:No\.|Number|#)\s*)(\d{1,2}:\d{2}-[a-z]{2}-\d{4,6}(?:-[A-Z]{2,4}(?:-[A-Z]{2,4})?)?)",
        re.IGNORECASE,
    )
    for m in pat.finditer(text):
        val = m.group(1)
        if val not in seen:
            seen.add(val)
            entities.append(ExtractedEntity("case_number", val, 0.95, _snippet(text, m)))

    # Also match standalone case-number patterns without "Case No."
    standalone = re.compile(r"\b(\d{1,2}:\d{2}-cv-\d{4,6}(?:-[A-Z]{2,4}(?:-[A-Z]{2,4})?)?)\b")
    for m in standalone.finditer(text):
        val = m.group(1)
        if val not in seen:
            seen.add(val)
            entities.append(ExtractedEntity("case_number", val, 0.7, _snippet(text, m)))

    return entities


def extract_claims(text: str) -> list[ExtractedEntity]:
    """Extract statutory references and legal claims."""
    entities: list[ExtractedEntity] = []
    seen: set[str] = set()

    claim_patterns = [
        (r"42\s*U\.?S\.?C\.?\s*(?:§|Section)\s*1983", "42 U.S.C. § 1983"),
        (r"Title\s+VII", "Title VII"),
        (r"28\s*U\.?S\.?C\.?\s*(?:§|Section)\s*1331", "28 U.S.C. § 1331 (Federal Question)"),
        (r"28\s*U\.?S\.?C\.?\s*(?:§|Section)\s*1332", "28 U.S.C. § 1332 (Diversity)"),
        (r"28\s*U\.?S\.?C\.?\s*(?:§|Section)\s*1441", "28 U.S.C. § 1441 (Removal)"),
        (r"Federal\s+Tort\s+Claims\s+Act|FTCA", "FTCA"),
        (r"18\s*U\.?S\.?C\.?\s*(?:§|Section)\s*1961|RICO", "RICO"),
        (r"Americans?\s+with\s+Disabilities\s+Act|ADA", "ADA"),
        (r"Age\s+Discrimination\s+in\s+Employment\s+Act|ADEA", "ADEA"),
        (r"Family\s+(?:and\s+)?Medical\s+Leave\s+Act|FMLA", "FMLA"),
        (r"Fair\s+Labor\s+Standards\s+Act|FLSA", "FLSA"),
        (r"False\s+Claims\s+Act|FCA", "FCA"),
    ]

    for pat, label in claim_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            if label not in seen:
                seen.add(label)
                entities.append(ExtractedEntity("claim", label, 0.85, _snippet(text, m)))

    return entities


def extract_court(text: str) -> list[ExtractedEntity]:
    """Extract court information from document text."""
    entities: list[ExtractedEntity] = []

    # Federal district court pattern
    pat = re.compile(
        r"(?:UNITED\s+STATES\s+DISTRICT\s+COURT|U\.?S\.?\s+District\s+Court)[,\s]*"
        r"(?:for\s+the\s+)?(.+?(?:DISTRICT|District)\s+(?:of|OF)\s+[A-Z][a-zA-Z\s]+?)(?:\n|$)",
        re.IGNORECASE | re.MULTILINE,
    )
    for m in pat.finditer(text):
        val = m.group(1).strip()
        if len(val) > 5:
            entities.append(ExtractedEntity("court", val, 0.9, _snippet(text, m)))

    # Fallback: just "District of Florida" etc.
    fallback = re.compile(
        r"((?:Northern|Southern|Middle|Eastern|Western|Central)\s+District\s+of\s+[A-Z][a-zA-Z]+)",
        re.IGNORECASE,
    )
    if not entities:
        for m in fallback.finditer(text):
            entities.append(ExtractedEntity("court", m.group(1).strip(), 0.7, _snippet(text, m)))

    return entities

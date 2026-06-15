"""
Exhibit Metadata Extractor — Generates standard Exhibit Indexes by scanning
document metadata, case facts, and filenames.

Produces:
- Numbered exhibit index with authentication methods
- FRE 901/902 authentication checklist
- Anticipated objections per exhibit
- .docx export of exhibit index

Usage:
  ftc exhibits -i case.json --format table
  ftc exhibits -i case.json --scan ./documents/ --numbering bates --prefix SMITH
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass
class ExhibitEntry:
    exhibit_number: str             # "A", "1", "PX-001"
    description: str                # "Medical Records from Tampa General Hospital"
    document_type: str              # "medical_records", "police_report", etc.
    date: str = ""                  # Extracted or inferred date
    author_source: str = ""         # "Tampa General Hospital"
    bates_range: str = ""           # "SMITH-000001 to SMITH-000045"
    authentication_method: str = "" # "FRE 803(6)/902(11) - Business Records"
    authentication_witness: str = ""  # "Records Custodian"
    relevant_claims: list[str] = field(default_factory=list)
    pages: int = 0
    objections_anticipated: list[str] = field(default_factory=list)
    status: str = "needs_authentication"  # authenticated | needs_authentication | self_authenticating


@dataclass
class ExhibitIndex:
    case_name: str
    total_exhibits: int
    entries: list[ExhibitEntry] = field(default_factory=list)
    authentication_checklist: list[dict] = field(default_factory=list)
    missing_authentication: list[str] = field(default_factory=list)
    generated_at: str = ""


# ── Document Classification ──────────────────────────────────────────────────

DOCUMENT_TYPES: dict[str, list[str]] = {
    "medical_records": ["medical", "hospital", "doctor", "nurse", "diagnosis", "treatment",
                        "radiology", "x-ray", "mri", "emergency room", "discharge", "prescription"],
    "police_report": ["police", "arrest", "incident report", "use of force", "booking",
                      "officer", "body camera", "body cam", "dash cam", "patrol"],
    "correspondence": ["letter", "email", "correspondence", "memo", "notice", "demand letter"],
    "financial": ["invoice", "receipt", "bank", "check", "payment", "billing", "wage",
                  "payroll", "w-2", "tax return", "1099"],
    "photograph": ["photo", "image", "picture", "screenshot", "photograph"],
    "video": ["video", "footage", "body camera", "dash cam", "surveillance", "recording"],
    "expert_report": ["expert", "report", "opinion", "analysis", "evaluation", "forensic"],
    "employment": ["termination", "evaluation", "performance", "handbook", "policy",
                   "job description", "offer letter", "employment agreement"],
    "government_record": ["foia", "public record", "certificate", "license", "permit",
                          "government", "agency", "eeoc", "charge of discrimination"],
    "contract": ["contract", "agreement", "lease", "deed", "settlement", "release"],
    "deposition": ["deposition", "transcript", "testimony"],
}

AUTHENTICATION_METHODS: dict[str, tuple[str, str, str]] = {
    # type -> (FRE rule, method description, witness/certification needed)
    "medical_records": ("FRE 803(6)/902(11)", "Business Records", "Records Custodian or FRE 902(11) Certification"),
    "police_report": ("FRE 803(8)/902(1)", "Public Records", "Self-authenticating with seal/certification"),
    "correspondence": ("FRE 901(b)(1)", "Witness with Knowledge", "Author or recipient"),
    "financial": ("FRE 803(6)/902(11)", "Business Records", "Records Custodian or FRE 902(11) Certification"),
    "photograph": ("FRE 901(b)(1)", "Witness with Knowledge", "Person familiar with scene depicted"),
    "video": ("FRE 901(b)(1)/(b)(9)", "Process/System Authentication", "Camera operator or system custodian"),
    "expert_report": ("FRE 901(b)(1)/702", "Expert Authentication", "Expert witness at deposition/trial"),
    "employment": ("FRE 803(6)/902(11)", "Business Records", "HR Records Custodian or FRE 902(11) Certification"),
    "government_record": ("FRE 902(1)/(2)", "Public Records", "Self-authenticating with seal"),
    "contract": ("FRE 901(b)(1)", "Witness with Knowledge", "Signatory or witness to execution"),
    "deposition": ("FRE 801(d)(1)", "Prior Testimony", "Court reporter certification"),
}

# Common evidentiary objections by document type
_OBJECTIONS: dict[str, list[str]] = {
    "medical_records": ["Hearsay (FRE 802) — address via FRE 803(6) business records exception"],
    "police_report": ["Hearsay (FRE 802) — address via FRE 803(8) public records exception",
                      "Opinions in report (FRE 701/702) — may need to establish officer's training"],
    "correspondence": ["Hearsay (FRE 802) — if offered for truth of matter asserted",
                       "Relevance (FRE 401) — establish connection to claims"],
    "financial": ["Hearsay (FRE 802) — address via FRE 803(6) business records"],
    "photograph": ["Authentication (FRE 901) — need witness to verify accuracy",
                   "Prejudice (FRE 403) — graphic photos may be excluded"],
    "video": ["Authentication (FRE 901) — verify completeness and accuracy",
              "Best evidence (FRE 1002) — must be original or duplicate"],
    "expert_report": ["Daubert/FRE 702 — reliability of methodology",
                      "FRE 703 — basis for opinion must be reasonable"],
    "employment": ["Hearsay (FRE 802) — address via FRE 803(6)",
                   "Privilege — attorney-client or work product claims"],
}


# ── Classification Helpers ───────────────────────────────────────────────────

def _classify_document_type(description: str) -> str:
    """Classify a document into a standard type category."""
    desc_lower = description.lower()
    best_type = "other"
    best_score = 0

    for dtype, keywords in DOCUMENT_TYPES.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > best_score:
            best_score = score
            best_type = dtype

    return best_type


def _suggest_authentication(doc_type: str) -> tuple[str, str, str]:
    """Suggest FRE authentication method for a document type."""
    return AUTHENTICATION_METHODS.get(doc_type, (
        "FRE 901(b)(1)", "Witness with Knowledge", "Witness familiar with document"
    ))


def _anticipate_objections(doc_type: str) -> list[str]:
    """Anticipate likely evidentiary objections."""
    return _OBJECTIONS.get(doc_type, ["Relevance (FRE 401)", "Authentication (FRE 901)"])


def _extract_date_from_text(text: str) -> str:
    """Try to extract a date from a description or filename."""
    # Match YYYY-MM-DD, MM/DD/YYYY, or month-day-year patterns
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{2}-\d{2}-\d{4})",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return ""


def _number_exhibit(index: int, numbering: str, prefix: str = "") -> str:
    """Generate exhibit number based on numbering scheme."""
    if numbering == "alpha":
        if index < 26:
            return chr(65 + index)  # A-Z
        return f"A{chr(65 + index - 26)}"  # AA, AB, ...
    elif numbering == "numeric":
        return str(index + 1)
    elif numbering == "bates":
        return f"{prefix}-{index + 1:06d}" if prefix else f"EX-{index + 1:06d}"
    return str(index + 1)


def _map_to_claims(description: str, case_data: dict) -> list[str]:
    """Map an exhibit to relevant claim keys based on description."""
    claims = case_data.get("claims_requested", [])
    if claims == ["auto_suggest"] or not claims:
        return []

    desc_lower = description.lower()
    relevant = []

    # Simple keyword matching
    claim_keywords = {
        "force": ["1983_fourth_excessive_force"],
        "arrest": ["1983_fourth_false_arrest"],
        "medical": ["1983_fourth_excessive_force", "ftca_medical_malpractice"],
        "employment": ["title_vii_disparate_treatment", "adea_age_discrimination"],
        "termination": ["title_vii_disparate_treatment", "fmla_retaliation"],
        "discrimination": ["title_vii_disparate_treatment", "1983_fourteenth_equal_protection"],
        "policy": ["1983_monell_municipal_liability"],
        "training": ["1983_monell_municipal_liability"],
    }

    for keyword, claim_keys in claim_keywords.items():
        if keyword in desc_lower:
            for ck in claim_keys:
                if ck in claims and ck not in relevant:
                    relevant.append(ck)

    return relevant


# ── Extraction Functions ─────────────────────────────────────────────────────

def _extract_from_case_facts(case_data: dict, numbering: str, prefix: str) -> list[ExhibitEntry]:
    """Extract exhibit entries from case_data facts."""
    entries = []
    seen = set()

    facts = case_data.get("facts", [])
    idx = 0

    for fact in facts:
        for doc in fact.get("documents", []):
            if doc in seen:
                continue
            seen.add(doc)

            doc_type = _classify_document_type(doc)
            rule, method, witness = _suggest_authentication(doc_type)
            objections = _anticipate_objections(doc_type)
            claims = _map_to_claims(doc, case_data)
            doc_date = fact.get("date", "") or _extract_date_from_text(doc)

            # Self-authenticating check
            status = "needs_authentication"
            if doc_type in ("government_record", "police_report"):
                status = "self_authenticating"

            entries.append(ExhibitEntry(
                exhibit_number=_number_exhibit(idx, numbering, prefix),
                description=doc,
                document_type=doc_type,
                date=doc_date,
                author_source="",
                authentication_method=f"{rule} - {method}",
                authentication_witness=witness,
                relevant_claims=claims,
                objections_anticipated=objections,
                status=status,
            ))
            idx += 1

    return entries


def _extract_from_manifest(manifest: list[dict], numbering: str, prefix: str) -> list[ExhibitEntry]:
    """Extract from a user-provided document manifest."""
    entries = []
    for idx, item in enumerate(manifest):
        desc = item.get("description", item.get("name", f"Document {idx + 1}"))
        doc_type = item.get("type", _classify_document_type(desc))
        rule, method, witness = _suggest_authentication(doc_type)
        objections = _anticipate_objections(doc_type)

        status = "needs_authentication"
        if doc_type in ("government_record", "police_report"):
            status = "self_authenticating"

        entries.append(ExhibitEntry(
            exhibit_number=_number_exhibit(idx, numbering, prefix),
            description=desc,
            document_type=doc_type,
            date=item.get("date", _extract_date_from_text(desc)),
            author_source=item.get("author", item.get("source", "")),
            bates_range=item.get("bates_range", ""),
            authentication_method=f"{rule} - {method}",
            authentication_witness=witness,
            pages=item.get("pages", 0),
            objections_anticipated=objections,
            status=status,
        ))

    return entries


def _scan_directory(directory: str, numbering: str, prefix: str) -> list[ExhibitEntry]:
    """Scan a directory for documents and extract metadata from filenames."""
    entries = []
    dir_path = Path(directory)
    if not dir_path.exists():
        return entries

    extensions = {".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png",
                  ".tiff", ".mp4", ".mov", ".xlsx", ".csv"}

    idx = 0
    for f in sorted(dir_path.iterdir()):
        if f.suffix.lower() in extensions and not f.name.startswith("."):
            desc = f.stem.replace("_", " ").replace("-", " ").title()
            doc_type = _classify_document_type(desc)
            rule, method, witness = _suggest_authentication(doc_type)
            doc_date = _extract_date_from_text(f.name)

            entries.append(ExhibitEntry(
                exhibit_number=_number_exhibit(idx, numbering, prefix),
                description=desc,
                document_type=doc_type,
                date=doc_date,
                authentication_method=f"{rule} - {method}",
                authentication_witness=witness,
                objections_anticipated=_anticipate_objections(doc_type),
                status="needs_authentication",
            ))
            idx += 1

    return entries


# ── Main API ─────────────────────────────────────────────────────────────────

def generate_exhibit_index(
    case_data: dict,
    document_manifest: list[dict] | None = None,
    scan_directory: str | None = None,
    numbering: str = "alpha",
    prefix: str = "",
) -> ExhibitIndex:
    """Generate a comprehensive exhibit index.

    Args:
        case_data: The case JSON data
        document_manifest: Optional list of document dicts
        scan_directory: Optional directory path to scan
        numbering: "alpha" (A, B, C), "numeric" (1, 2, 3), or "bates"
        prefix: Bates prefix (e.g., "SMITH")

    Returns:
        ExhibitIndex with entries and authentication checklist
    """
    entries = []

    # Priority: manifest > directory scan > case facts
    if document_manifest:
        entries = _extract_from_manifest(document_manifest, numbering, prefix)
    elif scan_directory:
        entries = _scan_directory(scan_directory, numbering, prefix)
    else:
        entries = _extract_from_case_facts(case_data, numbering, prefix)

    # Build authentication checklist
    checklist = []
    missing = []
    for e in entries:
        checklist.append({
            "exhibit": e.exhibit_number,
            "description": e.description,
            "method": e.authentication_method,
            "witness": e.authentication_witness,
            "status": e.status,
        })
        if e.status == "needs_authentication":
            missing.append(e.exhibit_number)

    # Case name
    parties = case_data.get("parties", {})
    plaintiffs = parties.get("plaintiffs", [])
    defendants = parties.get("defendants", [])
    p_name = plaintiffs[0]["name"] if plaintiffs else "Plaintiff"
    d_name = defendants[0]["name"] if defendants else "Defendant"
    case_name = f"{p_name} v. {d_name}"

    return ExhibitIndex(
        case_name=case_name,
        total_exhibits=len(entries),
        entries=entries,
        authentication_checklist=checklist,
        missing_authentication=missing,
        generated_at=str(date.today()),
    )


def format_exhibit_index(index: ExhibitIndex, fmt: str = "table") -> str:
    """Format exhibit index for CLI output.

    Args:
        index: The ExhibitIndex to format
        fmt: "table" for compact table, "detailed" for full details
    """
    lines = []

    lines.append("")
    lines.append("=" * 70)
    lines.append("         EXHIBIT INDEX")
    lines.append("=" * 70)
    lines.append(f"  Case:     {index.case_name}")
    lines.append(f"  Exhibits: {index.total_exhibits}")
    lines.append(f"  Pending:  {len(index.missing_authentication)} need authentication")
    lines.append("")

    if fmt == "table":
        lines.append(f"  {'Ex.':<6} {'Description':<35} {'Type':<18} {'Auth Status'}")
        lines.append("  " + "-" * 68)
        for e in index.entries:
            status_icon = {"authenticated": "OK", "self_authenticating": "SA",
                           "needs_authentication": "!!"}.get(e.status, "??")
            lines.append(f"  {e.exhibit_number:<6} {e.description[:35]:<35} {e.document_type:<18} [{status_icon}]")
    else:
        for e in index.entries:
            lines.append(f"  Exhibit {e.exhibit_number}: {e.description}")
            lines.append(f"    Type:           {e.document_type}")
            if e.date:
                lines.append(f"    Date:           {e.date}")
            if e.author_source:
                lines.append(f"    Source:         {e.author_source}")
            if e.bates_range:
                lines.append(f"    Bates:          {e.bates_range}")
            lines.append(f"    Authentication: {e.authentication_method}")
            lines.append(f"    Witness:        {e.authentication_witness}")
            lines.append(f"    Status:         {e.status}")
            if e.relevant_claims:
                lines.append(f"    Claims:         {', '.join(e.relevant_claims)}")
            if e.objections_anticipated:
                for obj in e.objections_anticipated:
                    lines.append(f"    [!] {obj}")
            lines.append("")

    if index.missing_authentication:
        lines.append("")
        lines.append(f"  AUTHENTICATION NEEDED: Exhibits {', '.join(index.missing_authentication)}")

    lines.append("")
    lines.append("=" * 70)
    lines.append(f"  Generated: {index.generated_at}")
    lines.append("")

    return "\n".join(lines)

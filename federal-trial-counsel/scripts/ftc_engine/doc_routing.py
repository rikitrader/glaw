"""
Document Routing — Layer 5 of the document analysis pipeline.

Maps document classifications to downstream workflows, merges extracted
entities into a case_data-compatible dict, and generates plain-English
recommendations a paralegal can act on.

Public surface:
  - WORKFLOW_ROUTING            (dict): category → workflow key
  - _WORKFLOW_LABELS            (dict): workflow key → human label
  - determine_workflow()        : pick a workflow from a list of analyses
  - build_auto_populated_data() : merge entities into case_data shape
  - generate_recommendations()  : actionable advisories per category
"""
from __future__ import annotations

from .doc_extraction import DocumentAnalysis


# ── Workflow Routing ──────────────────────────────────────────────────────

WORKFLOW_ROUTING: dict[str, str] = {
    # Procedural documents → specific workflows
    "complaint":                "complaint_defense",
    "answer":                   "existing_litigation",
    "motion_dismiss":           "motion_response",
    "motion_summary_judgment":  "motion_response",
    "motion_other":             "motion_response",
    "discovery_request":        "discovery_response",
    "court_order":              "compliance",
    "subpoena":                 "compliance",
    "notice":                   "existing_litigation",
    "deposition_transcript":    "existing_litigation",
    # Evidence types → standard new case
    "medical_records":          "new_case",
    "police_report":            "new_case",
    "financial":                "new_case",
    "correspondence":           "new_case",
    "photograph":               "new_case",
    "employment":               "new_case",
    "government_record":        "new_case",
    "contract":                 "new_case",
}

# Priority order for routing (higher priority = first match wins)
_ROUTING_PRIORITY = [
    "complaint", "motion_dismiss", "motion_summary_judgment", "motion_other",
    "discovery_request", "court_order", "subpoena", "notice", "answer",
    "deposition_transcript",
]


_WORKFLOW_LABELS: dict[str, str] = {
    "new_case":             "New Case Intake",
    "complaint_defense":    "Complaint Defense (Answer/MTD)",
    "existing_litigation":  "Existing Litigation Management",
    "motion_response":      "Motion Response",
    "discovery_response":   "Discovery Response",
    "compliance":           "Court Order Compliance",
}


def determine_workflow(analyses: list[DocumentAnalysis]) -> str:
    """Determine the best workflow based on document classifications.

    Priority: complaint > motion > discovery > order > evidence.
    """
    if not analyses:
        return "new_case"

    categories = {a.document_category for a in analyses if not a.errors}

    for cat in _ROUTING_PRIORITY:
        if cat in categories:
            return WORKFLOW_ROUTING.get(cat, "new_case")

    return "new_case"


def build_auto_populated_data(analyses: list[DocumentAnalysis]) -> dict:
    """Merge extracted entities into a case_data-compatible structure."""
    auto: dict = {}

    all_parties_p: list[dict] = []
    all_parties_d: list[dict] = []
    all_dates: list[str] = []
    court_info: dict = {}
    claims_found: list[str] = []
    case_nums: list[str] = []

    seen_names: set[str] = set()

    for a in analyses:
        if a.errors:
            continue

        for entity in a.parties:
            name = entity.value
            if name in seen_names:
                continue
            seen_names.add(name)
            party = {"name": name, "entity_type": "individual", "citizenship": ""}
            if entity.entity_type == "plaintiff":
                all_parties_p.append(party)
            else:
                all_parties_d.append(party)

        for entity in a.dates:
            if entity.value not in all_dates:
                all_dates.append(entity.value)

        for entity in a.courts:
            if not court_info:
                court_info = {"district": entity.value, "division": "", "state": ""}

        for entity in a.claims:
            if entity.value not in claims_found:
                claims_found.append(entity.value)

        for entity in a.case_numbers:
            if entity.value not in case_nums:
                case_nums.append(entity.value)

    if all_parties_p or all_parties_d:
        auto["parties"] = {
            "plaintiffs": all_parties_p,
            "defendants": all_parties_d,
        }

    if court_info:
        auto["court"] = court_info

    if claims_found:
        auto["claims_extracted"] = claims_found

    if all_dates:
        auto["dates_extracted"] = all_dates

    if case_nums:
        auto["case_numbers_extracted"] = case_nums

    return auto


def generate_recommendations(analyses: list[DocumentAnalysis]) -> list[str]:
    """Generate actionable recommendations based on the analysis."""
    recs: list[str] = []
    categories = [a.document_category for a in analyses if not a.errors]

    if "complaint" in categories:
        recs.append("Complaint detected — Answer or MTD due within 21 days of service")

    if "motion_dismiss" in categories:
        recs.append("Motion to Dismiss detected — Response due within 21 days")

    if "motion_summary_judgment" in categories:
        recs.append("Summary Judgment motion detected — Response due per local rule")

    if "discovery_request" in categories:
        recs.append("Discovery requests detected — Responses due within 30 days")

    if "court_order" in categories:
        recs.append("Court order detected — Check compliance deadlines immediately")

    if "subpoena" in categories:
        recs.append("Subpoena detected — Compliance or motion to quash required")

    # Claims detected
    all_claims: list[str] = []
    for a in analyses:
        for e in a.claims:
            if e.value not in all_claims:
                all_claims.append(e.value)
    if all_claims:
        recs.append(f"Statutory references found: {', '.join(all_claims)}")

    if not recs:
        recs.append("Evidence documents detected — proceed with standard case intake")

    return recs

"""
PACER/ECF Meta-Generator — Automated generation of secondary filing documents.

Generates:
- JS-44 Civil Cover Sheet
- Federal Summons (for each defendant)
- Corporate Disclosure Statement (FRCP 7.1)
- Notice of Interested Parties

Usage:
  ftc pacer -i case.json --all
  ftc pacer -i case.json --js44
  ftc pacer -i case.json --summons
  ftc pacer -i case.json --disclosure
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class JS44CoverSheet:
    """JS-44 Civil Cover Sheet data."""
    plaintiff_name: str
    plaintiff_county: str = ""
    plaintiff_attorney: str = ""
    plaintiff_attorney_bar: str = ""
    plaintiff_attorney_address: str = ""
    plaintiff_attorney_phone: str = ""
    defendant_name: str = ""
    defendant_county: str = ""
    defendant_attorney: str = ""
    basis_of_jurisdiction: str = ""  # 1=US Plaintiff, 2=US Defendant, 3=Federal Question, 4=Diversity
    citizenship_plaintiff: str = ""  # For diversity
    citizenship_defendant: str = ""
    nature_of_suit_code: str = ""    # 3-digit code
    nature_of_suit_text: str = ""
    origin: str = "1"               # 1=Original, 2=Removed, etc.
    cause_of_action: str = ""       # Statutory citation
    brief_description: str = ""
    demand_amount: str = ""
    jury_demand: str = "Yes"
    related_cases: list[str] = field(default_factory=list)
    class_action: bool = False


@dataclass
class Summons:
    """Federal summons for a defendant."""
    court_name: str
    court_address: str = ""
    case_number: str = ""
    plaintiff_name: str = ""
    defendant_name: str = ""
    defendant_address: str = ""
    plaintiff_attorney_name: str = ""
    plaintiff_attorney_address: str = ""
    plaintiff_attorney_phone: str = ""
    response_days: int = 21


@dataclass
class CorporateDisclosure:
    """FRCP 7.1 Corporate Disclosure Statement."""
    party_name: str
    party_type: str = ""        # corporation | llc | partnership
    parent_corporation: str = "None"
    publicly_held_10pct: str = "None"
    additional_disclosures: list[str] = field(default_factory=list)


@dataclass
class PacerFilingPackage:
    """Complete filing package."""
    js44: Optional[JS44CoverSheet] = None
    summonses: list[Summons] = field(default_factory=list)
    corporate_disclosures: list[CorporateDisclosure] = field(default_factory=list)
    notice_of_interested_parties: str = ""
    generated_at: str = ""
    warnings: list[str] = field(default_factory=list)


# ── Nature of Suit Code Mapping ──────────────────────────────────────────────

CLAIM_NATURE_CODES: dict[str, tuple[str, str]] = {
    "1983_fourth_excessive_force": ("440", "Other Civil Rights"),
    "1983_fourth_false_arrest": ("440", "Other Civil Rights"),
    "1983_fourth_unlawful_search_seizure": ("440", "Other Civil Rights"),
    "1983_first_amendment_retaliation": ("440", "Other Civil Rights"),
    "1983_first_amendment_speech_restriction": ("440", "Other Civil Rights"),
    "1983_fourteenth_procedural_due_process": ("440", "Other Civil Rights"),
    "1983_fourteenth_substantive_due_process": ("440", "Other Civil Rights"),
    "1983_fourteenth_equal_protection": ("440", "Other Civil Rights"),
    "1983_monell_municipal_liability": ("440", "Other Civil Rights"),
    "1983_eighth_deliberate_indifference": ("550", "Prisoner - Civil Rights"),
    "1985_conspiracy": ("440", "Other Civil Rights"),
    "1986_failure_to_prevent": ("440", "Other Civil Rights"),
    "bivens_fourth_search_seizure": ("440", "Other Civil Rights"),
    "bivens_fifth_due_process": ("440", "Other Civil Rights"),
    "bivens_eighth_deliberate_indifference": ("550", "Prisoner - Civil Rights"),
    "title_vii_disparate_treatment": ("442", "Employment - Civil Rights"),
    "title_vii_hostile_work_environment": ("442", "Employment - Civil Rights"),
    "title_vii_retaliation": ("442", "Employment - Civil Rights"),
    "adea_age_discrimination": ("442", "Employment - Civil Rights"),
    "ada_title_i_employment_disability": ("442", "Employment - Civil Rights"),
    "fmla_interference": ("448", "Employment - FMLA"),
    "fmla_retaliation": ("448", "Employment - FMLA"),
    "flsa_unpaid_wages_overtime": ("710", "Fair Labor Standards Act"),
    "ftca_negligence": ("360", "Personal Injury - Other"),
    "ftca_medical_malpractice": ("362", "Personal Injury - Medical Malpractice"),
    "ftca_wrongful_death": ("365", "Personal Injury - Product Liability"),
    "fcra_inaccurate_reporting": ("480", "Consumer Credit"),
    "fdcpa_prohibited_practices": ("480", "Consumer Credit"),
    "tila_disclosure_violations": ("480", "Consumer Credit"),
    "false_claims_act_qui_tam": ("376", "Qui Tam (31 USC 3729(a))"),
    "rico_1962c": ("470", "Racketeer Influenced and Corrupt Organizations"),
    "rico_1962d_conspiracy": ("470", "Racketeer Influenced and Corrupt Organizations"),
    "antitrust_sherman_section_1": ("410", "Antitrust"),
    "antitrust_sherman_section_2": ("410", "Antitrust"),
    "lanham_trademark_infringement": ("840", "Trademark"),
    "copyright_infringement": ("820", "Copyrights"),
    "patent_infringement": ("830", "Patent"),
    "erisa_502a1b_benefits": ("791", "Employee Ret. Inc. Security Act"),
    "erisa_502a3_equitable_relief": ("791", "Employee Ret. Inc. Security Act"),
    "apa_arbitrary_capricious": ("899", "Administrative Procedure Act"),
    "apa_unlawful_withholding_unreasonable_delay": ("899", "Administrative Procedure Act"),
    "tax_refund_suit": ("870", "Taxes (U.S. Plaintiff or Defendant)"),
    "tax_wrongful_levy": ("870", "Taxes (U.S. Plaintiff or Defendant)"),
}

CATEGORY_NATURE_CODES: dict[str, tuple[str, str]] = {
    "constitutional_civil_rights": ("440", "Other Civil Rights"),
    "bivens": ("440", "Other Civil Rights"),
    "employment": ("442", "Employment - Civil Rights"),
    "tort_government": ("360", "Personal Injury - Other"),
    "financial_consumer": ("480", "Consumer Credit"),
    "commercial": ("890", "Other Statutory Actions"),
    "administrative": ("899", "Administrative Procedure Act"),
    "erisa": ("791", "Employee Ret. Inc. Security Act"),
    "tax": ("870", "Taxes"),
}


# ── Helper Functions ─────────────────────────────────────────────────────────

def _determine_nature_of_suit(case_data: dict) -> tuple[str, str]:
    """Determine JS-44 nature of suit code from claims."""
    claims = case_data.get("claims_requested", [])

    # Try specific claim mapping first
    for claim_key in claims:
        if claim_key in CLAIM_NATURE_CODES:
            return CLAIM_NATURE_CODES[claim_key]

    # Fall back to category mapping
    from .claims import get_claim
    for claim_key in claims:
        meta = get_claim(claim_key)
        if meta and meta.category in CATEGORY_NATURE_CODES:
            return CATEGORY_NATURE_CODES[meta.category]

    return ("440", "Other Civil Rights")


def _determine_jurisdiction_basis(case_data: dict) -> str:
    """Map jurisdiction analysis to JS-44 basis code."""
    from .drafter import analyze_jurisdiction
    jx = analyze_jurisdiction(case_data)

    if jx.basis == "federal_question":
        return "3"  # Federal Question
    elif jx.basis == "diversity":
        return "4"  # Diversity

    # Check for government parties
    parties = case_data.get("parties", {})
    for p in parties.get("plaintiffs", []):
        if p.get("type") == "federal":
            return "1"  # U.S. Government Plaintiff
    for d in parties.get("defendants", []):
        if d.get("type") == "federal":
            return "2"  # U.S. Government Defendant

    return "3"  # Default to federal question


def _get_cause_of_action(case_data: dict) -> str:
    """Get primary statutory citation for the cause of action."""
    from .claims import get_claim
    claims = case_data.get("claims_requested", [])
    for claim_key in claims:
        meta = get_claim(claim_key)
        if meta:
            return meta.source
    return ""


def _get_citizenship_code(party: dict) -> str:
    """Map party citizenship to JS-44 code."""
    etype = party.get("entity_type", "individual")
    citizenship = party.get("citizenship", "")

    if etype == "individual":
        return f"Citizen of {citizenship}" if citizenship else "Citizen of this State"
    elif etype in ("corporation", "llc"):
        state = party.get("citizenship", party.get("state_of_incorporation", ""))
        ppb = party.get("principal_place_of_business", "")
        if state and ppb:
            return f"Incorporated in {state}, PPB in {ppb}"
        return f"Incorporated in {state}" if state else "Corporation"
    elif etype == "federal_agency":
        return "U.S. Government"
    return citizenship or "Unknown"


def _is_corporate_party(party: dict) -> bool:
    """Check if a party requires FRCP 7.1 disclosure."""
    etype = party.get("entity_type", "").lower()
    return etype in ("corporation", "llc", "partnership", "limited_partnership",
                     "limited_liability_company", "corporate")


# ── Main API ─────────────────────────────────────────────────────────────────

def generate_js44(case_data: dict) -> JS44CoverSheet:
    """Generate JS-44 Civil Cover Sheet from case data."""
    parties = case_data.get("parties", {})
    plaintiffs = parties.get("plaintiffs", [])
    defendants = parties.get("defendants", [])
    attorney = case_data.get("attorney", {})

    nature_code, nature_text = _determine_nature_of_suit(case_data)
    basis = _determine_jurisdiction_basis(case_data)
    cause = _get_cause_of_action(case_data)

    p_name = plaintiffs[0]["name"] if plaintiffs else "[PLAINTIFF]"
    d_name = defendants[0]["name"] if defendants else "[DEFENDANT]"

    # Brief description from claims
    claims = case_data.get("claims_requested", [])
    from .claims import get_claim
    claim_names = []
    for ck in claims[:3]:
        meta = get_claim(ck)
        if meta:
            claim_names.append(meta.name)
    brief = "; ".join(claim_names) if claim_names else "Civil action"

    # Demand amount
    demand = ""
    for f in case_data.get("facts", []):
        if f.get("damages_estimate"):
            demand = f["damages_estimate"]
            break

    # Jury demand
    relief = case_data.get("relief_requested", [])
    jury = "Yes" if "money" in relief else "No"

    return JS44CoverSheet(
        plaintiff_name=p_name,
        plaintiff_county=case_data.get("court", {}).get("state", ""),
        plaintiff_attorney=attorney.get("name", "[ATTORNEY NAME]"),
        plaintiff_attorney_bar=attorney.get("bar_number", "[BAR NO.]"),
        plaintiff_attorney_address=attorney.get("address", "[ADDRESS]"),
        plaintiff_attorney_phone=attorney.get("phone", "[PHONE]"),
        defendant_name=d_name,
        defendant_county="",
        basis_of_jurisdiction=basis,
        citizenship_plaintiff=_get_citizenship_code(plaintiffs[0]) if plaintiffs else "",
        citizenship_defendant=_get_citizenship_code(defendants[0]) if defendants else "",
        nature_of_suit_code=nature_code,
        nature_of_suit_text=nature_text,
        origin="1",  # Original proceeding (default)
        cause_of_action=cause,
        brief_description=brief,
        demand_amount=demand,
        jury_demand=jury,
    )


def generate_summons(case_data: dict, defendant_index: int = 0) -> Summons:
    """Generate summons for a specific defendant."""
    parties = case_data.get("parties", {})
    plaintiffs = parties.get("plaintiffs", [])
    defendants = parties.get("defendants", [])
    attorney = case_data.get("attorney", {})
    court = case_data.get("court", {})

    if defendant_index >= len(defendants):
        raise IndexError(f"Defendant index {defendant_index} out of range (have {len(defendants)})")

    defendant = defendants[defendant_index]

    # Determine response days (60 for US government)
    response_days = 21
    if defendant.get("type") == "federal":
        response_days = 60

    # Get district info for court address
    from .districts import get_active_district
    ctx = get_active_district()
    court_address = ctx.config.court_address

    return Summons(
        court_name=f"United States District Court, {court.get('district', ctx.config.name)}",
        court_address=court_address,
        case_number=case_data.get("case_number", "___-cv-_______-___"),
        plaintiff_name=plaintiffs[0]["name"] if plaintiffs else "[PLAINTIFF]",
        defendant_name=defendant["name"],
        defendant_address=defendant.get("address", "[DEFENDANT ADDRESS]"),
        plaintiff_attorney_name=attorney.get("name", "[ATTORNEY NAME]"),
        plaintiff_attorney_address=attorney.get("address", "[ADDRESS]"),
        plaintiff_attorney_phone=attorney.get("phone", "[PHONE]"),
        response_days=response_days,
    )


def generate_all_summonses(case_data: dict) -> list[Summons]:
    """Generate summonses for all defendants."""
    defendants = case_data.get("parties", {}).get("defendants", [])
    return [generate_summons(case_data, i) for i in range(len(defendants))]


def generate_corporate_disclosure(case_data: dict, party: dict) -> CorporateDisclosure:
    """Generate FRCP 7.1 disclosure for a corporate party."""
    return CorporateDisclosure(
        party_name=party["name"],
        party_type=party.get("entity_type", "corporation"),
        parent_corporation=party.get("parent_corporation", "None"),
        publicly_held_10pct=party.get("publicly_held_10pct", "None"),
    )


def generate_all_disclosures(case_data: dict) -> list[CorporateDisclosure]:
    """Generate FRCP 7.1 disclosures for all corporate parties."""
    parties = case_data.get("parties", {})
    disclosures = []

    for p in parties.get("plaintiffs", []):
        if _is_corporate_party(p):
            disclosures.append(generate_corporate_disclosure(case_data, p))
    for d in parties.get("defendants", []):
        if _is_corporate_party(d):
            disclosures.append(generate_corporate_disclosure(case_data, d))

    return disclosures


def generate_notice_of_interested_parties(case_data: dict) -> str:
    """Generate Notice of Interested Parties text."""
    parties = case_data.get("parties", {})
    lines = []
    lines.append("NOTICE OF INTERESTED PARTIES")
    lines.append("")
    lines.append("Pursuant to the Court's Standing Order, the following persons and entities")
    lines.append("have an interest in the outcome of this case:")
    lines.append("")

    idx = 1
    for p in parties.get("plaintiffs", []):
        lines.append(f"  {idx}. {p['name']} (Plaintiff)")
        idx += 1
    for d in parties.get("defendants", []):
        lines.append(f"  {idx}. {d['name']} (Defendant)")
        idx += 1

    lines.append("")
    lines.append("No other persons or entities are known to have an interest in this case.")

    return "\n".join(lines)


def generate_filing_package(case_data: dict) -> PacerFilingPackage:
    """Generate complete PACER filing package."""
    warnings = []

    # JS-44
    js44 = generate_js44(case_data)

    # Summonses
    summonses = generate_all_summonses(case_data)
    if not summonses:
        warnings.append("No defendants found — summonses not generated")

    # Corporate disclosures
    disclosures = generate_all_disclosures(case_data)

    # Notice
    notice = generate_notice_of_interested_parties(case_data)

    # Validation warnings
    if not case_data.get("attorney"):
        warnings.append("No attorney information — placeholders used in JS-44 and summonses")
    if js44.basis_of_jurisdiction == "4" and not js44.demand_amount:
        warnings.append("Diversity case requires amount in controversy > $75,000 — no demand amount specified")

    return PacerFilingPackage(
        js44=js44,
        summonses=summonses,
        corporate_disclosures=disclosures,
        notice_of_interested_parties=notice,
        generated_at=str(date.today()),
        warnings=warnings,
    )


# ── Formatters ───────────────────────────────────────────────────────────────

def format_js44(sheet: JS44CoverSheet) -> str:
    """Format JS-44 for CLI output."""
    basis_labels = {"1": "U.S. Government Plaintiff", "2": "U.S. Government Defendant",
                    "3": "Federal Question", "4": "Diversity"}
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("         JS-44 CIVIL COVER SHEET")
    lines.append("=" * 70)
    lines.append(f"  Plaintiff:       {sheet.plaintiff_name}")
    lines.append(f"  Defendant:       {sheet.defendant_name}")
    lines.append(f"  Attorney:        {sheet.plaintiff_attorney} (Bar #{sheet.plaintiff_attorney_bar})")
    lines.append(f"  Jurisdiction:    {basis_labels.get(sheet.basis_of_jurisdiction, 'Unknown')}")
    if sheet.basis_of_jurisdiction == "4":
        lines.append(f"  Citizenship (P): {sheet.citizenship_plaintiff}")
        lines.append(f"  Citizenship (D): {sheet.citizenship_defendant}")
    lines.append(f"  Nature of Suit:  {sheet.nature_of_suit_code} - {sheet.nature_of_suit_text}")
    lines.append(f"  Origin:          {sheet.origin} - Original Proceeding")
    lines.append(f"  Cause of Action: {sheet.cause_of_action}")
    lines.append(f"  Description:     {sheet.brief_description}")
    if sheet.demand_amount:
        lines.append(f"  Demand:          {sheet.demand_amount}")
    lines.append(f"  Jury Demand:     {sheet.jury_demand}")
    if sheet.class_action:
        lines.append(f"  Class Action:    Yes")
    lines.append("=" * 70)
    lines.append("")
    return "\n".join(lines)


def format_summons(summons: Summons) -> str:
    """Format a single summons for CLI output."""
    lines = []
    lines.append(f"  SUMMONS - {summons.defendant_name}")
    lines.append(f"    Court:    {summons.court_name}")
    lines.append(f"    Case:     {summons.case_number}")
    lines.append(f"    Plaintiff: {summons.plaintiff_name}")
    lines.append(f"    Response:  {summons.response_days} days from service")
    return "\n".join(lines)


def format_filing_package(package: PacerFilingPackage) -> str:
    """Format complete filing package for CLI output."""
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("         PACER/ECF FILING PACKAGE")
    lines.append("=" * 70)

    # Counts
    doc_count = 0
    if package.js44:
        doc_count += 1
    doc_count += len(package.summonses)
    doc_count += len(package.corporate_disclosures)
    if package.notice_of_interested_parties:
        doc_count += 1

    lines.append(f"  Documents generated: {doc_count}")
    lines.append(f"  Generated: {package.generated_at}")
    lines.append("")

    # JS-44
    if package.js44:
        lines.append(format_js44(package.js44))

    # Summonses
    if package.summonses:
        lines.append("  ## SUMMONSES")
        lines.append("")
        for s in package.summonses:
            lines.append(format_summons(s))
            lines.append("")

    # Corporate disclosures
    if package.corporate_disclosures:
        lines.append("  ## CORPORATE DISCLOSURE STATEMENTS (FRCP 7.1)")
        lines.append("")
        for cd in package.corporate_disclosures:
            lines.append(f"  {cd.party_name} ({cd.party_type})")
            lines.append(f"    Parent Corporation:    {cd.parent_corporation}")
            lines.append(f"    10%+ Public Holder:    {cd.publicly_held_10pct}")
            lines.append("")

    # Notice
    if package.notice_of_interested_parties:
        lines.append("  ## NOTICE OF INTERESTED PARTIES")
        lines.append("")
        for line in package.notice_of_interested_parties.split("\n"):
            lines.append(f"  {line}")
        lines.append("")

    # Warnings
    if package.warnings:
        lines.append("  ## WARNINGS")
        for w in package.warnings:
            lines.append(f"  [!!] {w}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("")
    return "\n".join(lines)

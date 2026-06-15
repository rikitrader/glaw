"""
Statute of Limitations Calculator - computes deadlines with tolling analysis.
Keys aligned with TypeScript engine (claim_library.ts).
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta, datetime
from typing import Optional
from .claims import get_claim, CLAIM_LIBRARY


@dataclass
class SOLResult:
    claim_key: str
    claim_name: str
    injury_date: date
    sol_period: str
    deadline: date
    days_remaining: int
    status: str  # "safe", "urgent", "expired"
    tolling_notes: list[str]


# SOL periods in days for each claim — keys aligned with TS claim_library.ts
SOL_DAYS: dict[str, int] = {
    "1983_first_amendment_retaliation": 1461,  # 4 years FL
    "1983_first_amendment_speech_restriction": 1461,
    "1983_fourth_excessive_force": 1461,
    "1983_fourth_false_arrest": 1461,
    "1983_fourth_unlawful_search_seizure": 1461,
    "1983_fourteenth_procedural_due_process": 1461,
    "1983_fourteenth_substantive_due_process": 1461,
    "1983_fourteenth_equal_protection": 1461,
    "1983_monell_municipal_liability": 1461,
    "1985_conspiracy": 1461,
    "1986_failure_to_prevent": 365,
    "1983_eighth_deliberate_indifference": 1461,
    "bivens_fourth_search_seizure": 1461,
    "bivens_fifth_due_process": 1461,
    "bivens_eighth_deliberate_indifference": 1461,
    "apa_arbitrary_capricious": 2192,  # 6 years
    "apa_unlawful_withholding_unreasonable_delay": 2192,
    "mandamus_compel_ministerial_duty": 2192,
    "habeas_detention_challenge": 365,
    "title_vii_disparate_treatment": 90,  # 90 days from right-to-sue
    "title_vii_hostile_work_environment": 90,
    "title_vii_retaliation": 90,
    "adea_age_discrimination": 90,
    "ada_title_i_employment_disability": 90,
    "fmla_interference": 730,
    "fmla_retaliation": 730,
    "flsa_unpaid_wages_overtime": 730,
    "ftca_negligence": 730,  # 2 years + admin
    "ftca_medical_malpractice": 730,
    "ftca_wrongful_death": 730,
    "fcra_inaccurate_reporting": 730,
    "fdcpa_prohibited_practices": 365,
    "tila_disclosure_violations": 365,
    "false_claims_act_qui_tam": 2192,
    "rico_1962c": 1461,
    "rico_1962d_conspiracy": 1461,
    "antitrust_sherman_section_1": 1461,
    "antitrust_sherman_section_2": 1461,
    "lanham_trademark_infringement": 1461,
    "copyright_infringement": 1096,  # 3 years
    "patent_infringement": 2192,
    "erisa_502a1b_benefits": 1461,
    "erisa_502a3_equitable_relief": 1461,
    "tax_refund_suit": 730,
    "tax_wrongful_levy": 274,  # 9 months
}


def calculate_sol(claim_key: str, injury_date_str: str, district_code: str | None = None) -> SOLResult:
    """Calculate SOL deadline for a claim.

    Args:
        claim_key: The claim key
        injury_date_str: Injury date in YYYY-MM-DD format
        district_code: Optional district code for state-specific SOL override
    """
    meta = get_claim(claim_key)
    if not meta:
        raise ValueError(f"Unknown claim: {claim_key}")

    try:
        injury = datetime.strptime(injury_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {injury_date_str}. Use YYYY-MM-DD")

    if injury > date.today():
        raise ValueError(f"Injury date {injury_date_str} is in the future")

    # Use district-aware SOL if available
    sol_days = SOL_DAYS.get(claim_key, 1461)
    if district_code:
        try:
            from .districts import get_sol_days_for_district
            sol_days = get_sol_days_for_district(claim_key, district_code)
        except Exception:
            pass  # Fall back to default

    deadline = injury + timedelta(days=sol_days)
    remaining = (deadline - date.today()).days

    if remaining < 0:
        status = "expired"
    elif remaining < 90:
        status = "urgent"
    else:
        status = "safe"

    tolling = _get_tolling_notes(claim_key, meta)

    return SOLResult(
        claim_key=claim_key,
        claim_name=meta.name,
        injury_date=injury,
        sol_period=meta.statute_of_limitations,
        deadline=deadline,
        days_remaining=remaining,
        status=status,
        tolling_notes=tolling,
    )


def calculate_all_sol(claim_keys: list[str], injury_date_str: str) -> list[SOLResult]:
    """Calculate SOL for multiple claims."""
    return [calculate_sol(ck, injury_date_str) for ck in claim_keys]


def _get_tolling_notes(claim_key: str, meta) -> list[str]:
    notes = []
    cat = meta.category

    if cat == "constitutional_civil_rights":
        notes.append("Discovery rule may toll if injury not immediately apparent")
        notes.append("Continuing violation doctrine may extend for ongoing conduct")
        notes.append("Equitable tolling if defendant concealed actions")

    if cat == "employment":
        notes.append("Continuing violation for hostile environment (National Railroad)")
        notes.append("Equitable tolling for EEOC processing delays")
        if "title_vii" in claim_key:
            notes.append("90-day period runs from receipt of right-to-sue letter")

    if cat == "tort_government":
        notes.append("2-year period for filing SF-95 admin claim")
        notes.append("After denial: 6 months to file suit")
        notes.append("If no response in 6 months: deemed denial, no time limit on suit")

    if cat == "administrative":
        notes.append("SOL may be tolled during administrative proceedings")

    if "flsa" in claim_key:
        notes.append("3-year SOL for willful violations (vs. 2-year standard)")

    return notes

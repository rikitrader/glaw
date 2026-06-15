"""
Auto Claim Suggestion Engine - Analyzes facts and suggests applicable federal claims.
Keys aligned with TypeScript engine (claim_library.ts).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .claims import CLAIM_LIBRARY, get_claim


@dataclass
class ClaimSuggestion:
    claim_key: str
    claim_name: str
    match_score: int
    reasons: list[str]
    showstoppers: list[str]


# Keyword patterns associated with claim categories
FACT_PATTERNS: dict[str, list[str]] = {
    "force": ["force", "beat", "shot", "tased", "pepper spray", "punched", "kicked",
              "slammed", "choked", "struck", "baton", "tackled", "restrained"],
    "arrest": ["arrest", "detained", "seized", "handcuffed", "custody", "taken into",
               "booked", "jailed"],
    "search": ["search", "warrant", "entered", "confiscated", "seized property",
               "raided", "pat down", "strip search", "searched"],
    "employment": ["fired", "terminated", "demoted", "suspended", "promoted", "hired",
                   "laid off", "not promoted", "disciplined", "transferred"],
    "discrimination": ["discrimination", "because of", "race", "gender", "sex", "age",
                       "disability", "religion", "national origin", "color", "protected class"],
    "harassment": ["harassed", "hostile", "offensive", "slurs", "groping", "intimidation",
                   "unwelcome", "severe and pervasive"],
    "retaliation": ["retaliated", "complained", "reported", "whistleblow", "filed complaint",
                    "protected activity", "adverse after"],
    "speech": ["speech", "spoke", "protest", "public concern", "silence", "censor",
               "viewpoint", "expression", "petition"],
    "negligence": ["negligent", "careless", "failed to", "should have", "malpractice",
                   "standard of care"],
    "fraud": ["fraud", "misrepresented", "false", "deceived", "scheme", "lied",
              "false claim", "qui tam", "billing fraud", "overbill", "kickback"],
    "policy": ["policy", "custom", "training", "pattern", "widespread", "failure to train",
               "policymaker", "deliberate indifference"],
    "federal_employee": ["federal", "VA", "military", "IRS", "FBI", "ICE", "postal",
                         "government", "DEA", "ATF", "CBP", "USMS", "BOP", "secret service"],
    "contract": ["contract", "agreement", "breach", "promised", "failed to pay"],
    "wages": ["unpaid", "overtime", "minimum wage", "hours worked", "wages",
              "off the clock", "misclassified", "exempt"],
    "medical": ["medical", "hospital", "treatment", "surgery", "doctor", "nurse",
                "misdiagnosed", "patient"],
    "due_process": ["hearing", "notice", "fired without", "license revoked", "property taken",
                    "deprive", "no hearing", "without process"],
    "enterprise": ["organization", "company", "network", "scheme", "ongoing",
                   "racketeering", "predicate acts", "mail fraud", "wire fraud"],
    "death": ["death", "died", "killed", "fatal", "decedent", "surviving", "wrongful death"],
    "prison": ["prison", "inmate", "jail", "correctional", "conditions of", "cell",
               "lockdown", "solitary", "medical care"],
    "habeas": ["habeas", "detention", "custody", "immigration detention",
               "unlawful imprisonment", "release", "parole", "sentence"],
    "agency": ["agency", "petition", "visa", "immigration", "unreasonable delay",
               "application pending", "adjudication", "final action", "withholding"],
    "antitrust": ["antitrust", "monopoly", "price fixing", "restraint of trade",
                  "market power", "cartel", "bid rigging", "boycott", "tying"],
    "trademark": ["trademark", "brand", "confusion", "counterfeit", "trade dress",
                  "knock off", "dilution"],
    "copyright": ["copyright", "copied", "pirated", "reproduction", "derivative work",
                  "DMCA", "original work"],
    "patent": ["patent", "invention", "claim chart", "prior art", "prosecution",
               "patent holder"],
    "credit": ["credit report", "inaccurate report", "credit score", "furnisher",
               "consumer report", "dispute", "equifax", "experian", "transunion"],
    "debt_collection": ["debt collector", "harassing calls", "collection letter",
                        "cease and desist", "third party disclosure", "validation notice"],
    "lending": ["lending", "loan", "APR", "interest rate", "disclosure",
                "truth in lending", "rescission", "finance charge"],
    "erisa": ["ERISA", "benefits", "plan denied", "long term disability", "pension",
              "401k", "fiduciary", "claim denied", "insurance denied"],
    "tax": ["tax", "IRS", "refund", "levy", "lien", "assessment", "taxpayer",
            "collection", "internal revenue"],
    "disability": ["disability", "accommodation", "wheelchair", "impairment", "ADA",
                   "medical condition", "reasonable modification"],
    "age": ["age", "older", "younger worker", "over 40", "replaced by younger", "too old"],
    "fmla": ["FMLA", "medical leave", "family leave", "maternity", "paternity",
             "serious health", "leave request"],
    "conspiracy": ["conspired", "agreed", "coordinated", "concerted action",
                   "acting together", "colluded", "joint action"],
}

# Map patterns to claim keys — aligned with TypeScript claim_library.ts keys
PATTERN_CLAIM_MAP: dict[str, list[str]] = {
    "force": ["1983_fourth_excessive_force"],
    "arrest": ["1983_fourth_false_arrest"],
    "search": ["1983_fourth_unlawful_search_seizure", "bivens_fourth_search_seizure"],
    "employment": ["title_vii_disparate_treatment", "adea_age_discrimination",
                   "ada_title_i_employment_disability", "fmla_interference", "fmla_retaliation"],
    "discrimination": ["title_vii_disparate_treatment", "1983_fourteenth_equal_protection",
                       "adea_age_discrimination", "ada_title_i_employment_disability"],
    "harassment": ["title_vii_hostile_work_environment"],
    "retaliation": ["1983_first_amendment_retaliation", "title_vii_retaliation", "fmla_retaliation"],
    "speech": ["1983_first_amendment_retaliation", "1983_first_amendment_speech_restriction"],
    "negligence": ["ftca_negligence", "ftca_medical_malpractice"],
    "fraud": ["false_claims_act_qui_tam", "rico_1962c"],
    "policy": ["1983_monell_municipal_liability"],
    "federal_employee": ["bivens_fourth_search_seizure", "bivens_fifth_due_process",
                         "bivens_eighth_deliberate_indifference", "ftca_negligence"],
    "wages": ["flsa_unpaid_wages_overtime"],
    "medical": ["ftca_medical_malpractice"],
    "due_process": ["1983_fourteenth_procedural_due_process",
                    "1983_fourteenth_substantive_due_process",
                    "bivens_fifth_due_process"],
    "enterprise": ["rico_1962c", "rico_1962d_conspiracy"],
    "death": ["ftca_wrongful_death"],
    "prison": ["1983_eighth_deliberate_indifference", "bivens_eighth_deliberate_indifference"],
    "habeas": ["habeas_detention_challenge"],
    "agency": ["apa_arbitrary_capricious", "apa_unlawful_withholding_unreasonable_delay",
               "mandamus_compel_ministerial_duty"],
    "antitrust": ["antitrust_sherman_section_1", "antitrust_sherman_section_2"],
    "trademark": ["lanham_trademark_infringement"],
    "copyright": ["copyright_infringement"],
    "patent": ["patent_infringement"],
    "credit": ["fcra_inaccurate_reporting"],
    "debt_collection": ["fdcpa_prohibited_practices"],
    "lending": ["tila_disclosure_violations"],
    "erisa": ["erisa_502a1b_benefits", "erisa_502a3_equitable_relief"],
    "tax": ["tax_refund_suit", "tax_wrongful_levy"],
    "disability": ["ada_title_i_employment_disability"],
    "age": ["adea_age_discrimination"],
    "fmla": ["fmla_interference", "fmla_retaliation"],
    "conspiracy": ["1985_conspiracy", "1986_failure_to_prevent", "rico_1962d_conspiracy"],
}


def suggest_claims(case_data: dict, max_results: int = 10) -> list[ClaimSuggestion]:
    """Auto-suggest claims based on case facts and party types."""
    facts = case_data.get("facts", [])
    parties = case_data.get("parties", {})
    exhaustion = case_data.get("exhaustion", {})

    all_facts_text = " ".join(
        f"{f.get('event', '')} {f.get('harm', '')} {' '.join(f.get('actors', []))}"
        for f in facts
    ).lower()

    defendants = parties.get("defendants", [])
    has_state_actor = any(d.get("type") in ("state", "local", "federal", "officer") for d in defendants)
    has_federal = any(d.get("type") == "federal" for d in defendants)
    has_municipal = any(d.get("type") == "local" for d in defendants)

    # Score each claim
    scores: dict[str, ClaimSuggestion] = {}

    # Pattern-based matching
    for pattern_name, keywords in FACT_PATTERNS.items():
        matches = sum(1 for kw in keywords if kw.lower() in all_facts_text)
        if matches == 0:
            continue

        claim_keys = PATTERN_CLAIM_MAP.get(pattern_name, [])
        for ck in claim_keys:
            meta = get_claim(ck)
            if not meta:
                continue

            if ck not in scores:
                scores[ck] = ClaimSuggestion(ck, meta.name, 0, [], [])

            s = scores[ck]
            s.match_score += min(30, matches * 10)
            s.reasons.append(f"Fact pattern: {pattern_name} ({matches} keyword matches)")

    # Defendant-type adjustments
    for ck, s in list(scores.items()):
        meta = get_claim(ck)
        if not meta:
            continue

        cat = meta.category
        if cat in ("constitutional_civil_rights", "bivens"):
            if has_state_actor:
                s.match_score += 20
                s.reasons.append("State actor defendant present")
            else:
                s.showstoppers.append("No state actor defendant - 1983/Bivens requires color of law")

        if cat == "bivens" and meta.viability_warning:
            s.showstoppers.append(meta.viability_warning)

        if cat == "tort_government" and not has_federal:
            s.showstoppers.append("No federal defendant - FTCA requires federal employee")

        # Exhaustion checks
        if meta.exhaustion_required:
            etype = meta.exhaustion_type or ""
            if "eeoc" in etype and exhaustion.get("eeoc_charge_filed") is False:
                s.showstoppers.append("EEOC charge not filed")
            if "ftca" in etype and exhaustion.get("ftca_admin_claim_filed") is False:
                s.showstoppers.append("SF-95 admin claim not filed")

    # Municipal defendant -> always suggest Monell
    if has_municipal and "1983_monell_municipal_liability" not in scores:
        meta = get_claim("1983_monell_municipal_liability")
        if meta:
            scores["1983_monell_municipal_liability"] = ClaimSuggestion(
                "1983_monell_municipal_liability", meta.name, 25,
                ["Municipal defendant present - Monell required for entity liability"], []
            )

    # Sort by score, filter out zero-score
    results = sorted(scores.values(), key=lambda x: -x.match_score)
    results = [r for r in results if r.match_score > 0]
    return results[:max_results]

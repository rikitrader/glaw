"""
Federal Claim Library - 44+ federal causes of action with metadata.
Ported from claim_library.ts to Python for local execution.
Keys aligned with TypeScript engine (claim_library.ts).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClaimMetadata:
    name: str
    category: str
    source: str
    heightened_pleading: bool = False
    exhaustion_required: bool = False
    exhaustion_type: Optional[str] = None
    immunities: list[str] = field(default_factory=list)
    typical_defenses: list[str] = field(default_factory=list)
    jurisdiction: str = "federal_question"
    statute_of_limitations: str = ""
    viability_warning: Optional[str] = None


CLAIM_LIBRARY: dict[str, ClaimMetadata] = {
    # === CONSTITUTIONAL / CIVIL RIGHTS (42 U.S.C. 1983) ===
    "1983_first_amendment_retaliation": ClaimMetadata(
        name="First Amendment Retaliation (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. I",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Speech not on public concern", "Garcetti official duties"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_first_amendment_speech_restriction": ClaimMetadata(
        name="First Amendment Speech Restriction (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. I",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Viewpoint-neutral restriction", "Content-neutral regulation", "Compelling government interest"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourth_excessive_force": ClaimMetadata(
        name="Fourth Amendment Excessive Force (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. IV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Reasonable force", "Heck v. Humphrey bar"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourth_false_arrest": ClaimMetadata(
        name="Fourth Amendment False Arrest (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. IV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Probable cause", "Arguable probable cause"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourth_unlawful_search_seizure": ClaimMetadata(
        name="Fourth Amendment Unlawful Search/Seizure (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. IV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Warrant exception", "Consent", "Exigent circumstances"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourteenth_procedural_due_process": ClaimMetadata(
        name="Fourteenth Amendment Procedural Due Process (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. XIV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "No protected interest", "Adequate post-deprivation remedy"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourteenth_substantive_due_process": ClaimMetadata(
        name="Fourteenth Amendment Substantive Due Process (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. XIV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Rational basis", "No fundamental right"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_fourteenth_equal_protection": ClaimMetadata(
        name="Fourteenth Amendment Equal Protection (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. XIV",
        immunities=["qualified"],
        typical_defenses=["Qualified immunity", "Rational basis", "No similarly situated comparators"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1983_monell_municipal_liability": ClaimMetadata(
        name="Monell Municipal Liability (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; Monell v. Dept. of Social Servs., 436 U.S. 658 (1978)",
        immunities=[],
        typical_defenses=["No policy/custom", "No moving force causation", "Isolated incident"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1985_conspiracy": ClaimMetadata(
        name="Conspiracy to Interfere with Civil Rights (42 U.S.C. 1985)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1985(3)",
        immunities=["qualified"],
        typical_defenses=["No agreement", "Intracorporate conspiracy doctrine", "No class-based animus"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),
    "1986_failure_to_prevent": ClaimMetadata(
        name="Failure to Prevent Conspiracy (42 U.S.C. 1986)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1986",
        immunities=["qualified"],
        typical_defenses=["No underlying 1985 violation", "No knowledge", "No power to prevent"],
        statute_of_limitations="1 year",
    ),
    "1983_eighth_deliberate_indifference": ClaimMetadata(
        name="Eighth Amendment Deliberate Indifference (42 U.S.C. 1983)",
        category="constitutional_civil_rights",
        source="42 U.S.C. 1983; U.S. Const. amend. VIII; Estelle v. Gamble, 429 U.S. 97 (1976)",
        immunities=["qualified"],
        exhaustion_required=True, exhaustion_type="plra",
        typical_defenses=["Qualified immunity", "Mere negligence", "No subjective knowledge", "PLRA exhaustion"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
    ),

    # === BIVENS ===
    "bivens_fourth_search_seizure": ClaimMetadata(
        name="Bivens - Fourth Amendment (Federal Officers)",
        category="bivens",
        source="Bivens v. Six Unknown Named Agents, 403 U.S. 388 (1971)",
        immunities=["qualified", "sovereign"],
        typical_defenses=["Qualified immunity", "New context", "Special factors"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
        viability_warning="Post-Egbert v. Boule (2022): Bivens expansion extremely limited",
    ),
    "bivens_fifth_due_process": ClaimMetadata(
        name="Bivens - Fifth Amendment Due Process (Federal Officers)",
        category="bivens",
        source="Davis v. Passman, 442 U.S. 228 (1979)",
        immunities=["qualified", "sovereign"],
        typical_defenses=["Qualified immunity", "New context", "Alternative remedies"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
        viability_warning="Post-Egbert: Court reluctant to extend Bivens beyond existing contexts",
    ),
    "bivens_eighth_deliberate_indifference": ClaimMetadata(
        name="Bivens - Eighth Amendment (Federal Prisoners)",
        category="bivens",
        source="Carlson v. Green, 446 U.S. 14 (1980)",
        immunities=["qualified", "sovereign"],
        exhaustion_required=True, exhaustion_type="plra",
        typical_defenses=["Qualified immunity", "FTCA alternative", "Special factors"],
        statute_of_limitations="State personal injury SOL (FL: 4 years)",
        viability_warning="Only viable in traditional prison conditions context",
    ),

    # === ADMINISTRATIVE / APA ===
    "apa_arbitrary_capricious": ClaimMetadata(
        name="APA - Arbitrary and Capricious (5 U.S.C. 706)",
        category="administrative",
        source="5 U.S.C. 706(2)(A)",
        immunities=["sovereign"],
        exhaustion_required=True, exhaustion_type="apa_final_action",
        typical_defenses=["No final agency action", "Committed to agency discretion", "Adequate reasoning"],
        statute_of_limitations="6 years (28 U.S.C. 2401)",
    ),
    "apa_unlawful_withholding_unreasonable_delay": ClaimMetadata(
        name="APA - Unlawful Withholding/Unreasonable Delay (5 U.S.C. 706(1))",
        category="administrative",
        source="5 U.S.C. 706(1)",
        immunities=["sovereign"],
        typical_defenses=["Agency has rule of reason", "Competing priorities", "TRAC factors"],
        statute_of_limitations="6 years",
    ),
    "mandamus_compel_ministerial_duty": ClaimMetadata(
        name="Mandamus (28 U.S.C. 1361)",
        category="administrative",
        source="28 U.S.C. 1361",
        immunities=["sovereign"],
        typical_defenses=["Discretionary duty", "Alternative remedy", "No clear right"],
        statute_of_limitations="6 years",
    ),
    "habeas_detention_challenge": ClaimMetadata(
        name="Habeas Corpus (28 U.S.C. 2241)",
        category="administrative",
        source="28 U.S.C. 2241",
        immunities=[],
        exhaustion_required=True, exhaustion_type="administrative",
        typical_defenses=["Exhaustion", "Procedural default", "Not in custody"],
        statute_of_limitations="1 year (AEDPA)",
    ),

    # === EMPLOYMENT ===
    "title_vii_disparate_treatment": ClaimMetadata(
        name="Title VII Disparate Treatment",
        category="employment",
        source="42 U.S.C. 2000e-2",
        exhaustion_required=True, exhaustion_type="eeoc",
        immunities=["eleventh_amendment"],
        typical_defenses=["Legitimate nondiscriminatory reason", "Same-actor inference", "Stray remarks"],
        statute_of_limitations="90 days from EEOC right-to-sue letter",
    ),
    "title_vii_hostile_work_environment": ClaimMetadata(
        name="Title VII Hostile Work Environment",
        category="employment",
        source="42 U.S.C. 2000e-2",
        exhaustion_required=True, exhaustion_type="eeoc",
        immunities=["eleventh_amendment"],
        typical_defenses=["Faragher/Ellerth defense", "Not severe/pervasive", "Not based on protected class"],
        statute_of_limitations="90 days from EEOC right-to-sue letter",
    ),
    "title_vii_retaliation": ClaimMetadata(
        name="Title VII Retaliation",
        category="employment",
        source="42 U.S.C. 2000e-3",
        exhaustion_required=True, exhaustion_type="eeoc",
        immunities=["eleventh_amendment"],
        typical_defenses=["No protected activity", "No adverse action", "No causal connection"],
        statute_of_limitations="90 days from EEOC right-to-sue letter",
    ),
    "adea_age_discrimination": ClaimMetadata(
        name="Age Discrimination (ADEA)",
        category="employment",
        source="29 U.S.C. 621 et seq.",
        exhaustion_required=True, exhaustion_type="eeoc",
        immunities=["eleventh_amendment"],
        typical_defenses=["RFOA defense", "BFOQ", "Not 40+"],
        statute_of_limitations="90 days from EEOC right-to-sue",
    ),
    "ada_title_i_employment_disability": ClaimMetadata(
        name="Disability Discrimination (ADA Title I)",
        category="employment",
        source="42 U.S.C. 12112",
        exhaustion_required=True, exhaustion_type="eeoc",
        immunities=["eleventh_amendment"],
        typical_defenses=["Not qualified individual", "Undue hardship", "Direct threat"],
        statute_of_limitations="90 days from EEOC right-to-sue",
    ),
    "fmla_interference": ClaimMetadata(
        name="FMLA Interference",
        category="employment",
        source="29 U.S.C. 2615(a)(1)",
        immunities=["eleventh_amendment"],
        typical_defenses=["Not eligible employee", "No serious health condition", "Not FMLA-qualifying"],
        statute_of_limitations="2 years (3 years willful)",
    ),
    "fmla_retaliation": ClaimMetadata(
        name="FMLA Retaliation",
        category="employment",
        source="29 U.S.C. 2615(a)(2)",
        immunities=["eleventh_amendment"],
        typical_defenses=["Legitimate reason", "No causal connection", "Would have been terminated anyway"],
        statute_of_limitations="2 years (3 years willful)",
    ),
    "flsa_unpaid_wages_overtime": ClaimMetadata(
        name="FLSA Unpaid Wages/Overtime",
        category="employment",
        source="29 U.S.C. 207",
        immunities=["eleventh_amendment"],
        typical_defenses=["Exempt status", "No hours worked", "Good faith defense"],
        statute_of_limitations="2 years (3 years willful)",
    ),

    # === FTCA ===
    "ftca_negligence": ClaimMetadata(
        name="FTCA Negligence",
        category="tort_government",
        source="28 U.S.C. 2671-2680",
        immunities=["sovereign"],
        exhaustion_required=True, exhaustion_type="ftca_sf95",
        typical_defenses=["Discretionary function", "Independent contractor", "Feres doctrine"],
        statute_of_limitations="2 years + admin claim",
    ),
    "ftca_medical_malpractice": ClaimMetadata(
        name="FTCA Medical Malpractice",
        category="tort_government",
        source="28 U.S.C. 2671-2680",
        immunities=["sovereign"],
        exhaustion_required=True, exhaustion_type="ftca_sf95",
        typical_defenses=["Discretionary function", "Standard of care met", "No causation"],
        statute_of_limitations="2 years + admin claim",
    ),
    "ftca_wrongful_death": ClaimMetadata(
        name="FTCA Wrongful Death",
        category="tort_government",
        source="28 U.S.C. 2671-2680",
        immunities=["sovereign"],
        exhaustion_required=True, exhaustion_type="ftca_sf95",
        typical_defenses=["Discretionary function", "No proximate cause", "Feres doctrine"],
        statute_of_limitations="2 years + admin claim",
    ),

    # === FINANCIAL / CONSUMER ===
    "fcra_inaccurate_reporting": ClaimMetadata(
        name="Fair Credit Reporting Act Violation",
        category="financial_consumer",
        source="15 U.S.C. 1681 et seq.",
        typical_defenses=["Reasonable procedures", "No willfulness", "Standing"],
        statute_of_limitations="2 years (5 years willful)",
    ),
    "fdcpa_prohibited_practices": ClaimMetadata(
        name="Fair Debt Collection Practices Act Violation",
        category="financial_consumer",
        source="15 U.S.C. 1692 et seq.",
        typical_defenses=["Not debt collector", "Bona fide error", "No communication"],
        statute_of_limitations="1 year",
    ),
    "tila_disclosure_violations": ClaimMetadata(
        name="Truth in Lending Act Violation",
        category="financial_consumer",
        source="15 U.S.C. 1601 et seq.",
        typical_defenses=["Technical compliance", "Bona fide error", "Rescission limitations"],
        statute_of_limitations="1 year (3 years rescission)",
    ),

    # === COMMERCIAL / RICO / IP ===
    "false_claims_act_qui_tam": ClaimMetadata(
        name="False Claims Act - Qui Tam",
        category="commercial",
        source="31 U.S.C. 3729-3733",
        heightened_pleading=True,
        typical_defenses=["No false claim", "No materiality", "Public disclosure bar"],
        statute_of_limitations="6 years (10 years max)",
    ),
    "rico_1962c": ClaimMetadata(
        name="RICO 1962(c) - Pattern of Racketeering",
        category="commercial",
        source="18 U.S.C. 1962(c)",
        heightened_pleading=True,
        typical_defenses=["No enterprise", "No pattern", "No continuity", "No proximate cause"],
        statute_of_limitations="4 years (civil)",
    ),
    "rico_1962d_conspiracy": ClaimMetadata(
        name="RICO Conspiracy (18 U.S.C. 1962(d))",
        category="commercial",
        source="18 U.S.C. 1962(d)",
        heightened_pleading=True,
        typical_defenses=["No underlying RICO violation", "No agreement", "Withdrawal"],
        statute_of_limitations="4 years",
    ),
    "antitrust_sherman_section_1": ClaimMetadata(
        name="Sherman Act Section 1 - Restraint of Trade",
        category="commercial",
        source="15 U.S.C. 1",
        typical_defenses=["Rule of reason", "No agreement", "No antitrust injury"],
        statute_of_limitations="4 years",
    ),
    "antitrust_sherman_section_2": ClaimMetadata(
        name="Sherman Act Section 2 - Monopolization",
        category="commercial",
        source="15 U.S.C. 2",
        typical_defenses=["No monopoly power", "Legitimate business justification", "No anticompetitive conduct"],
        statute_of_limitations="4 years",
    ),
    "lanham_trademark_infringement": ClaimMetadata(
        name="Lanham Act - Trademark Infringement",
        category="commercial",
        source="15 U.S.C. 1114, 1125",
        typical_defenses=["No likelihood of confusion", "Fair use", "Laches"],
        statute_of_limitations="Analogous state SOL",
    ),
    "copyright_infringement": ClaimMetadata(
        name="Copyright Infringement",
        category="commercial",
        source="17 U.S.C. 501",
        immunities=["eleventh_amendment"],
        typical_defenses=["Fair use", "Independent creation", "No substantial similarity"],
        statute_of_limitations="3 years",
    ),
    "patent_infringement": ClaimMetadata(
        name="Patent Infringement",
        category="commercial",
        source="35 U.S.C. 271",
        immunities=["eleventh_amendment"],
        typical_defenses=["Non-infringement", "Invalidity", "Prosecution history estoppel"],
        statute_of_limitations="6 years (damages)",
    ),

    # === ERISA ===
    "erisa_502a1b_benefits": ClaimMetadata(
        name="ERISA Benefits Denial (502(a)(1)(B))",
        category="erisa",
        source="29 U.S.C. 1132(a)(1)(B)",
        exhaustion_required=True, exhaustion_type="erisa_internal",
        typical_defenses=["Abuse of discretion", "Plan terms", "Untimely internal appeal"],
        statute_of_limitations="Analogous state SOL",
    ),
    "erisa_502a3_equitable_relief": ClaimMetadata(
        name="ERISA Equitable Relief (502(a)(3))",
        category="erisa",
        source="29 U.S.C. 1132(a)(3)",
        typical_defenses=["Adequate remedy under 502(a)(1)(B)", "No equitable basis", "Monetary relief disguised"],
        statute_of_limitations="Analogous state SOL",
    ),

    # === TAX ===
    "tax_refund_suit": ClaimMetadata(
        name="Tax Refund Suit",
        category="tax",
        source="28 U.S.C. 1346(a)(1)",
        immunities=["sovereign"],
        exhaustion_required=True, exhaustion_type="irs_claim",
        typical_defenses=["Full payment rule", "Flora rule", "No valid claim filed"],
        statute_of_limitations="2 years from disallowance",
    ),
    "tax_wrongful_levy": ClaimMetadata(
        name="Wrongful Levy (26 U.S.C. 7426)",
        category="tax",
        source="26 U.S.C. 7426",
        immunities=["sovereign"],
        typical_defenses=["Property belonged to taxpayer", "Valid assessment", "Proper procedures followed"],
        statute_of_limitations="9 months from levy",
    ),
}


def get_claim(key: str) -> ClaimMetadata | None:
    return CLAIM_LIBRARY.get(key)


def get_claims_by_category(category: str) -> dict[str, ClaimMetadata]:
    return {k: v for k, v in CLAIM_LIBRARY.items() if v.category == category}


def get_exhaustion_required() -> dict[str, ClaimMetadata]:
    return {k: v for k, v in CLAIM_LIBRARY.items() if v.exhaustion_required}


def get_heightened_pleading() -> dict[str, ClaimMetadata]:
    return {k: v for k, v in CLAIM_LIBRARY.items() if v.heightened_pleading}


def list_categories() -> list[str]:
    return sorted(set(c.category for c in CLAIM_LIBRARY.values()))

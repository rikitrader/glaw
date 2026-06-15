"""
Built-in viability knowledge base for the Rule 11 Duty Monitor.

This is a static dataset of ViabilityIssue entries keyed by claim_key,
covering the major Supreme Court and Circuit decisions that affect
specific federal causes of action.

Kept in its own module so rule11_monitor.py stays focused on logic.
The data is consumed via _check_built_in_viability() which simply
returns VIABILITY_KNOWLEDGE.get(claim_key, []).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ViabilityIssue:
    severity: str  # critical | high | medium | low
    category: str  # scotus_decision | circuit_decision | statutory_amendment | bivens_limitation | exhaustion_change | immunity_expansion
    description: str
    citation: str = ""
    date: str = ""
    recommendation: str = ""


VIABILITY_KNOWLEDGE: dict[str, list[ViabilityIssue]] = {
    # Bivens claims — post-Egbert severe restrictions
    "bivens_fourth_search_seizure": [
        ViabilityIssue(
            severity="critical",
            category="scotus_decision",
            description="Bivens extension effectively frozen after Egbert v. Boule. New contexts almost certainly barred.",
            citation="Egbert v. Boule, 596 U.S. 482 (2022)",
            date="2022-06-08",
            recommendation="Verify this is a recognized Bivens context (Bivens itself, Davis, Carlson). If new context, consider § 1983 or FTCA alternative.",
        ),
        ViabilityIssue(
            severity="high",
            category="scotus_decision",
            description="Even in recognized Fourth Amendment Bivens context, courts increasingly find 'special factors' counsel hesitation.",
            citation="Ziglar v. Abbasi, 582 U.S. 120 (2017)",
            date="2017-06-19",
            recommendation="Plead within the exact factual contours of Bivens v. Six Unknown Named Agents, 403 U.S. 388 (1971).",
        ),
    ],
    "bivens_fifth_due_process": [
        ViabilityIssue(
            severity="critical",
            category="scotus_decision",
            description="Fifth Amendment Bivens claims face near-certain dismissal in new contexts post-Egbert.",
            citation="Egbert v. Boule, 596 U.S. 482 (2022)",
            date="2022-06-08",
            recommendation="Only viable in exact Davis v. Passman context (employment discrimination by congressional staffer). Consider FTCA or APA alternatives.",
        ),
    ],
    "bivens_eighth_deliberate_indifference": [
        ViabilityIssue(
            severity="critical",
            category="scotus_decision",
            description="Eighth Amendment Bivens for prisoner conditions may be limited to Carlson v. Green facts.",
            citation="Egbert v. Boule, 596 U.S. 482 (2022)",
            date="2022-06-08",
            recommendation="Plead within Carlson v. Green, 446 U.S. 14 (1980) contours (failure to provide medical treatment). Consider FTCA.",
        ),
    ],

    # Section 1983 — qualified immunity strictness
    "1983_fourth_excessive_force": [
        ViabilityIssue(
            severity="medium",
            category="circuit_decision",
            description="11th Circuit applies strict 'clearly established' standard; factually identical precedent often required.",
            citation="Mercado v. City of Orlando, 407 F.3d 1152 (11th Cir. 2005)",
            date="2005-05-16",
            recommendation="Cite factually analogous 11th Circuit or Supreme Court decisions when opposing qualified immunity.",
        ),
    ],
    "1983_fourth_false_arrest": [
        ViabilityIssue(
            severity="medium",
            category="circuit_decision",
            description="Qualified immunity grants common for false arrest; courts broadly interpret 'arguable probable cause'.",
            citation="Grider v. City of Auburn, 618 F.3d 1240 (11th Cir. 2010)",
            date="2010-08-20",
            recommendation="Show officer lacked even arguable probable cause and cite analogous precedent.",
        ),
    ],
    "1983_monell_municipal_liability": [
        ViabilityIssue(
            severity="medium",
            category="circuit_decision",
            description="Monell pleading standards require specific policy/custom allegations; cannot rely solely on respondeat superior.",
            citation="McDowell v. Brown, 392 F.3d 1283 (11th Cir. 2004)",
            date="2004-12-15",
            recommendation="Plead specific policy, widespread custom, or deliberate indifference to training. Obtain FOIA records of prior complaints.",
        ),
    ],

    # Employment — procedural traps
    "title_vii_disparate_treatment": [
        ViabilityIssue(
            severity="high",
            category="exhaustion_change",
            description="Failure to file EEOC charge within 180/300 days bars claim. Right-to-sue letter required before filing.",
            citation="Fort Bend County v. Davis, 587 U.S. 541 (2019)",
            date="2019-06-03",
            recommendation="Verify EEOC charge was timely filed and right-to-sue letter received. 90-day filing window from receipt is jurisdictional-like.",
        ),
    ],
    "title_vii_hostile_work_environment": [
        ViabilityIssue(
            severity="medium",
            category="circuit_decision",
            description="Continuing violation doctrine may save late-filed claims, but discrete acts still require timely EEOC charge.",
            citation="Nat'l R.R. Passenger Corp. v. Morgan, 536 U.S. 101 (2002)",
            date="2002-06-10",
            recommendation="Distinguish between discrete acts (timely charge required) and hostile environment pattern (continuing violation doctrine applies).",
        ),
    ],
    "adea_age_discrimination": [
        ViabilityIssue(
            severity="medium",
            category="exhaustion_change",
            description="ADEA exhaustion parallels Title VII but mixed motive framework is more limited per Gross v. FBL.",
            citation="Gross v. FBL Financial Services, 557 U.S. 167 (2009)",
            date="2009-06-18",
            recommendation="Plead 'but-for' causation, not merely motivating factor. ADEA requires stronger causal link than Title VII.",
        ),
    ],

    # FTCA
    "ftca_negligence": [
        ViabilityIssue(
            severity="high",
            category="exhaustion_change",
            description="SF-95 administrative claim must be filed within 2 years. Failure is jurisdictional — cannot be waived.",
            citation="McNeil v. United States, 508 U.S. 106 (1993)",
            date="1993-05-17",
            recommendation="Verify SF-95 filed within 2 years of accrual. After denial, file suit within 6 months.",
        ),
        ViabilityIssue(
            severity="medium",
            category="immunity_expansion",
            description="Discretionary function exception (28 U.S.C. 2680(a)) bars many government negligence claims.",
            citation="Berkovitz v. United States, 486 U.S. 531 (1988)",
            date="1988-06-13",
            recommendation="Show government employee violated a mandatory duty (not discretionary judgment).",
        ),
    ],
    "ftca_medical_malpractice": [
        ViabilityIssue(
            severity="high",
            category="exhaustion_change",
            description="SF-95 administrative claim required. State law governs standard of care under FTCA.",
            citation="28 U.S.C. 2674",
            recommendation="File SF-95 within 2 years. Apply forum state's medical malpractice standard (not federal).",
        ),
    ],

    # APA
    "apa_arbitrary_capricious": [
        ViabilityIssue(
            severity="medium",
            category="scotus_decision",
            description="Post-Loper Bright, Chevron deference overruled. Courts now exercise independent judgment on statutory interpretation.",
            citation="Loper Bright Enterprises v. Raimondo, 603 U.S. ___ (2024)",
            date="2024-06-28",
            recommendation="APA challenges may be more viable post-Loper Bright. Argue statutory text independently — Chevron deference no longer applies.",
        ),
    ],

    # PLRA — prisoner claims
    "1983_eighth_deliberate_indifference": [
        ViabilityIssue(
            severity="high",
            category="exhaustion_change",
            description="PLRA requires exhaustion of all available administrative remedies before filing. No exceptions.",
            citation="Ross v. Blake, 578 U.S. 632 (2016)",
            date="2016-06-06",
            recommendation="Exhaust all available prison grievance procedures. If unavailable, document why (Ross v. Blake three exceptions).",
        ),
    ],
}

"""
Deposition Question Generator — Parses facts and claim elements to generate
tailored direct and cross-examination questions.

For each witness, generates questions organized by:
- Foundation (FRE 602 personal knowledge)
- Claim Elements (mapped to specific claim elements)
- Document Authentication (FRE 901)
- Impeachment (prior inconsistent statements, bias)
- Defense Anticipation (from risk.py top vulnerabilities)

Usage:
  ftc deposition -i case.json -w "Officer Brown" --type cross
  ftc deposition -i case.json -w "John Smith" --type direct --claim 1983_fourth_excessive_force
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class DepositionQuestion:
    category: str       # foundation | claim_element | authentication | impeachment | defense_anticipation
    subcategory: str    # e.g. "FRE 602", "excessive_force_element_1", "bias"
    question_text: str
    purpose: str
    follow_ups: list[str] = field(default_factory=list)
    related_claim: str = "general"
    exam_type: str = "cross"  # "direct" | "cross"


@dataclass
class DepositionOutline:
    witness_name: str
    witness_role: str       # plaintiff | defendant | officer | expert | witness
    exam_type: str          # direct | cross
    claim_keys: list[str] = field(default_factory=list)
    total_questions: int = 0
    sections: dict[str, list[DepositionQuestion]] = field(default_factory=dict)
    estimated_duration_minutes: int = 0
    warnings: list[str] = field(default_factory=list)
    generated_at: str = ""


# ── Claim Elements Knowledge Base ────────────────────────────────────────────

CLAIM_ELEMENTS: dict[str, list[dict]] = {
    "1983_fourth_excessive_force": [
        {"element": "State action / color of law",
         "direct": ["Describe the officer's role and duties on the date of the incident."],
         "cross": ["You were acting in your official capacity as a law enforcement officer, correct?",
                    "You were on duty at the time, isn't that right?"]},
        {"element": "Seizure occurred",
         "direct": ["Describe what happened when you encountered the officer.",
                     "Were you free to leave at any point during this encounter?"],
         "cross": ["You physically restrained the plaintiff, correct?",
                    "The plaintiff was not free to leave, isn't that true?"]},
        {"element": "Force was objectively unreasonable (Graham v. Connor factors)",
         "direct": ["Describe the level of force used against you.",
                     "What were you doing immediately before force was applied?",
                     "Did you pose any threat to anyone at that moment?"],
         "cross": ["What crime did you suspect the plaintiff of committing?",
                    "On a scale from 1 to 10, how would you rate the severity of that crime?",
                    "Did the plaintiff have any weapons?",
                    "Was the plaintiff actively resisting arrest?",
                    "Isn't it true that less force could have achieved the same result?"]},
        {"element": "Injury resulted from the force",
         "direct": ["Describe the injuries you sustained.",
                     "What medical treatment did you receive?"],
         "cross": ["You observed injuries on the plaintiff after the use of force, correct?",
                    "An ambulance was called to the scene, isn't that right?"]},
    ],
    "1983_fourth_false_arrest": [
        {"element": "Arrest occurred without probable cause",
         "direct": ["Describe the circumstances of your arrest.",
                     "What were you told was the reason for your arrest?"],
         "cross": ["What specific facts supported probable cause for this arrest?",
                    "Did you obtain an arrest warrant before arresting the plaintiff?",
                    "Isn't it true that the only basis for arrest was a verbal complaint?"]},
        {"element": "State actor made the arrest",
         "direct": ["Identify the person who placed you under arrest."],
         "cross": ["You identified yourself as a police officer before making the arrest, correct?"]},
        {"element": "Resulting deprivation of liberty",
         "direct": ["How long were you detained?", "Where were you taken?"],
         "cross": ["The plaintiff was held in custody for more than 24 hours, correct?"]},
    ],
    "1983_monell_municipal_liability": [
        {"element": "Official policy, custom, or practice",
         "direct": ["Are you aware of the department's use-of-force policy?"],
         "cross": ["The department has a written use-of-force policy, correct?",
                    "How many excessive force complaints were filed against this department in the past three years?",
                    "Were all officers trained on the current use-of-force policy?"]},
        {"element": "Policy was the moving force behind the violation",
         "direct": ["In your experience, how does the department handle similar situations?"],
         "cross": ["Isn't it true that this officer had prior complaints for excessive force?",
                    "Were any prior complaints sustained?",
                    "What disciplinary action was taken, if any?"]},
    ],
    "title_vii_disparate_treatment": [
        {"element": "Membership in protected class",
         "direct": ["What is your race/gender/national origin?"],
         "cross": ["You are aware that the plaintiff is a member of a protected class, correct?"]},
        {"element": "Adverse employment action",
         "direct": ["Describe the employment action taken against you.",
                     "When did this occur?"],
         "cross": ["You terminated the plaintiff's employment, correct?",
                    "What was the stated reason for the termination?"]},
        {"element": "Similarly situated comparators treated differently",
         "direct": ["Were there other employees in similar positions who were not terminated?",
                     "What was their protected class status?"],
         "cross": ["Other employees with similar performance records were retained, correct?",
                    "Those employees were outside the plaintiff's protected class, isn't that true?"]},
        {"element": "Pretext — stated reason is not the real reason",
         "direct": ["Were you given any indication that the real reason differed from what was stated?"],
         "cross": ["The stated reason for termination was documented in writing, correct?",
                    "When was that documentation created — before or after the termination decision?",
                    "Isn't it true that the plaintiff's supervisor made comments about [protected class]?"]},
    ],
    "title_vii_hostile_work_environment": [
        {"element": "Unwelcome conduct based on protected characteristic",
         "direct": ["Describe the conduct you experienced at work.",
                     "How did this conduct relate to your [protected class]?"],
         "cross": ["You were aware of complaints about this conduct, correct?"]},
        {"element": "Severe or pervasive",
         "direct": ["How frequently did this conduct occur?",
                     "How did it affect your ability to perform your job?"],
         "cross": ["You received multiple complaints from the plaintiff about this conduct, correct?",
                    "This conduct occurred over a period of months, isn't that right?"]},
        {"element": "Employer knew or should have known and failed to act",
         "direct": ["Did you report this conduct to your supervisor or HR?", "What happened after you reported?"],
         "cross": ["The plaintiff reported this conduct to HR, correct?",
                    "What investigation was conducted?",
                    "What corrective action was taken?"]},
    ],
    "ftca_negligence": [
        {"element": "Duty of care owed by federal employee",
         "direct": ["Describe the federal employee's role and responsibilities."],
         "cross": ["The federal employee had a duty to follow established protocols, correct?"]},
        {"element": "Breach of duty",
         "direct": ["Describe how the standard of care was violated."],
         "cross": ["The established protocol was not followed, isn't that true?"]},
        {"element": "Causation",
         "direct": ["How did the federal employee's actions cause your injury?"],
         "cross": ["The plaintiff's injuries occurred as a direct result of the employee's actions, correct?"]},
        {"element": "Damages",
         "direct": ["Describe the harm you suffered.", "What treatment have you received?"],
         "cross": ["Medical records document the plaintiff's injuries, correct?"]},
    ],
    "ada_title_i_employment_disability": [
        {"element": "Qualified individual with a disability",
         "direct": ["Describe your disability.", "Were you able to perform the essential functions of your job?"],
         "cross": ["You were aware the plaintiff had a disability, correct?",
                    "The plaintiff was performing their job duties satisfactorily, isn't that true?"]},
        {"element": "Failure to provide reasonable accommodation",
         "direct": ["What accommodation did you request?", "What was the employer's response?"],
         "cross": ["The plaintiff requested an accommodation, correct?",
                    "What interactive process did you engage in to determine a reasonable accommodation?"]},
        {"element": "Adverse action because of disability",
         "direct": ["Do you believe your disability played a role in the adverse action?"],
         "cross": ["The timing of the adverse action coincided with the accommodation request, correct?"]},
    ],
}

# Generic elements for claims not in CLAIM_ELEMENTS
_GENERIC_ELEMENTS: list[dict] = [
    {"element": "Standing / Injury in fact",
     "direct": ["Describe the harm you suffered."],
     "cross": ["The plaintiff claims to have suffered injury, correct?"]},
    {"element": "Causation",
     "direct": ["How did the defendant's actions cause your injury?"],
     "cross": ["The defendant's conduct directly led to the plaintiff's claimed injury, correct?"]},
    {"element": "Damages",
     "direct": ["Describe the losses you have experienced."],
     "cross": ["Medical records / financial documents support the claimed damages, correct?"]},
]


# ── Question Generators ──────────────────────────────────────────────────────

def _determine_witness_role(witness_name: str, case_data: dict) -> str:
    """Determine the witness's role from case data."""
    parties = case_data.get("parties", {})
    for p in parties.get("plaintiffs", []):
        if witness_name.lower() in p.get("name", "").lower():
            return "plaintiff"
    for d in parties.get("defendants", []):
        if witness_name.lower() in d.get("name", "").lower():
            dtype = d.get("type", "")
            if dtype == "officer":
                return "officer"
            return "defendant"
    # Check facts for witness mentions
    for f in case_data.get("facts", []):
        for actor in f.get("actors", []):
            if witness_name.lower() in actor.lower():
                return "witness"
        for w in f.get("witnesses", []):
            if witness_name.lower() in w.lower():
                return "witness"
    return "witness"


def _generate_foundation_questions(witness_name: str, case_data: dict, exam_type: str) -> list[DepositionQuestion]:
    """FRE 602 personal knowledge foundation questions."""
    qs = []

    if exam_type == "direct":
        qs.append(DepositionQuestion(
            category="foundation", subcategory="FRE 602",
            question_text=f"Please state your full name for the record.",
            purpose="Establish witness identity",
            exam_type="direct",
        ))
        qs.append(DepositionQuestion(
            category="foundation", subcategory="FRE 602",
            question_text="What is your current occupation and employer?",
            purpose="Establish witness background",
            exam_type="direct",
        ))
        qs.append(DepositionQuestion(
            category="foundation", subcategory="FRE 602",
            question_text=f"How are you connected to the events at issue in this case?",
            purpose="Establish personal knowledge under FRE 602",
            exam_type="direct",
            follow_ups=["Were you physically present when the events occurred?",
                        "What was your role at that time?"],
        ))
    else:
        qs.append(DepositionQuestion(
            category="foundation", subcategory="FRE 602",
            question_text=f"You have personal knowledge of the events at issue in this lawsuit, correct?",
            purpose="Lock in personal knowledge under FRE 602",
            exam_type="cross",
        ))
        qs.append(DepositionQuestion(
            category="foundation", subcategory="FRE 602",
            question_text="You were physically present at the location where the events occurred, isn't that true?",
            purpose="Establish presence and foundation for testimony",
            exam_type="cross",
            follow_ups=["You could see and hear what was happening?",
                        "Your memory of these events is clear?"],
        ))

    # Add fact-based foundation
    facts = case_data.get("facts", [])
    for f in facts:
        actors = f.get("actors", [])
        witnesses = f.get("witnesses", [])
        if witness_name.lower() in " ".join(actors + witnesses).lower():
            event = f.get("event", "")[:80]
            loc = f.get("location", "")
            d = f.get("date", "")
            if exam_type == "direct":
                qs.append(DepositionQuestion(
                    category="foundation", subcategory="fact_presence",
                    question_text=f"Please describe what happened on {d} at {loc}." if d and loc
                                  else f"Describe the incident involving {event}.",
                    purpose="Elicit firsthand account of key event",
                    exam_type="direct",
                ))
            else:
                qs.append(DepositionQuestion(
                    category="foundation", subcategory="fact_presence",
                    question_text=f"You were present on {d} at {loc}, correct?" if d and loc
                                  else f"You have knowledge of the incident involving {event}, correct?",
                    purpose="Lock in witness to specific event",
                    exam_type="cross",
                ))
            break

    return qs


def _generate_claim_element_questions(
    case_data: dict, claim_key: str, witness_name: str, exam_type: str
) -> list[DepositionQuestion]:
    """Generate questions mapped to specific claim elements."""
    elements = CLAIM_ELEMENTS.get(claim_key, _GENERIC_ELEMENTS)
    qs = []

    for elem in elements:
        questions = elem.get(exam_type, elem.get("cross", []))
        for q_text in questions:
            qs.append(DepositionQuestion(
                category="claim_element",
                subcategory=elem["element"],
                question_text=q_text,
                purpose=f"Establish/challenge element: {elem['element']}",
                related_claim=claim_key,
                exam_type=exam_type,
            ))

    return qs


def _generate_authentication_questions(case_data: dict, witness_name: str) -> list[DepositionQuestion]:
    """FRE 901 document authentication questions."""
    qs = []
    facts = case_data.get("facts", [])

    docs_mentioned = set()
    for f in facts:
        for doc in f.get("documents", []):
            docs_mentioned.add(doc)

    for doc in sorted(docs_mentioned):
        qs.append(DepositionQuestion(
            category="authentication", subcategory="FRE 901",
            question_text=f"I'm going to show you what has been marked as Exhibit ___. Do you recognize this document titled '{doc}'?",
            purpose=f"Authenticate '{doc}' under FRE 901(b)(1)",
            exam_type="cross",
            follow_ups=[
                "Who prepared this document?",
                "Is this a true and correct copy?",
                "Were you involved in creating this document?",
            ],
        ))

    if not docs_mentioned:
        qs.append(DepositionQuestion(
            category="authentication", subcategory="FRE 901",
            question_text="Are there any documents that relate to the events we've been discussing?",
            purpose="Identify potential exhibits for authentication",
            exam_type="cross",
        ))

    return qs


def _generate_impeachment_questions(case_data: dict, witness_name: str, witness_role: str) -> list[DepositionQuestion]:
    """Bias, prior inconsistent statements, and interest questions."""
    qs = []

    # Bias / interest
    if witness_role == "officer":
        qs.append(DepositionQuestion(
            category="impeachment", subcategory="bias",
            question_text="If the jury finds the use of force was excessive, that could affect your employment, correct?",
            purpose="Establish personal interest / bias of officer-witness",
            exam_type="cross",
            follow_ups=[
                "You could face disciplinary action?",
                "This could affect your ability to testify as a witness in other cases?",
            ],
        ))
        qs.append(DepositionQuestion(
            category="impeachment", subcategory="prior_conduct",
            question_text="Have you ever been the subject of a complaint alleging excessive force?",
            purpose="Establish pattern of prior conduct",
            exam_type="cross",
            follow_ups=["How many complaints?", "Were any sustained?"],
        ))
    elif witness_role == "defendant":
        qs.append(DepositionQuestion(
            category="impeachment", subcategory="bias",
            question_text="You have a personal financial interest in the outcome of this case, don't you?",
            purpose="Establish financial interest / bias",
            exam_type="cross",
        ))

    # Prior inconsistent statements
    qs.append(DepositionQuestion(
        category="impeachment", subcategory="prior_statements",
        question_text="Have you given any prior statements — written or verbal — about the events at issue?",
        purpose="Lay foundation for impeachment with prior inconsistent statements (FRE 613)",
        exam_type="cross",
        follow_ups=[
            "To whom did you give that statement?",
            "Was the statement under oath?",
            "Do you have a copy of that statement?",
        ],
    ))

    # Perception / memory
    qs.append(DepositionQuestion(
        category="impeachment", subcategory="perception",
        question_text="Is there anything that would have affected your ability to perceive the events clearly — distance, lighting, obstructions?",
        purpose="Challenge perception and reliability of testimony",
        exam_type="cross",
    ))

    return qs


def _generate_defense_anticipation_questions(
    case_data: dict, claim_keys: list[str], witness_name: str
) -> list[DepositionQuestion]:
    """Questions addressing top vulnerabilities from risk assessment."""
    qs = []

    from .claims import get_claim

    for claim_key in claim_keys:
        meta = get_claim(claim_key)
        if not meta:
            continue

        # Address known immunities
        if "qualified" in meta.immunities:
            qs.append(DepositionQuestion(
                category="defense_anticipation", subcategory="qualified_immunity",
                question_text="Were you aware, at the time, that this conduct could violate the plaintiff's constitutional rights?",
                purpose="Address qualified immunity — establish that the right was clearly established",
                related_claim=claim_key,
                exam_type="cross",
                follow_ups=[
                    "Had you received training on this issue?",
                    "Were you aware of any court decisions addressing this type of conduct?",
                ],
            ))

        # Address exhaustion defenses
        if meta.exhaustion_required:
            qs.append(DepositionQuestion(
                category="defense_anticipation", subcategory="exhaustion",
                question_text=f"Are you aware of any administrative process the plaintiff was required to complete before filing this {meta.name} claim?",
                purpose=f"Address exhaustion requirement ({meta.exhaustion_type})",
                related_claim=claim_key,
                exam_type="cross",
            ))

        # Address top defenses
        for defense in meta.typical_defenses[:2]:
            qs.append(DepositionQuestion(
                category="defense_anticipation", subcategory="anticipated_defense",
                question_text=f"Regarding the defense of '{defense}' — what facts support your position on this issue?",
                purpose=f"Preemptively address anticipated defense: {defense}",
                related_claim=claim_key,
                exam_type="cross",
            ))

    return qs


# ── Main API ─────────────────────────────────────────────────────────────────

def generate_deposition_outline(
    case_data: dict,
    witness_name: str,
    exam_type: str = "cross",
    claim_keys: list[str] | None = None,
    max_questions: int = 50,
) -> DepositionOutline:
    """Generate a complete deposition question outline for a witness.

    Args:
        case_data: The case JSON data
        witness_name: Name of the witness to depose
        exam_type: "direct" or "cross"
        claim_keys: Specific claims to focus on (auto-detects if None)
        max_questions: Maximum total questions

    Returns:
        DepositionOutline with categorized questions
    """
    # Determine witness role
    witness_role = _determine_witness_role(witness_name, case_data)

    # Determine claims
    if not claim_keys:
        claim_keys = case_data.get("claims_requested", [])
        if not claim_keys or claim_keys == ["auto_suggest"]:
            from .suggest import suggest_claims
            suggestions = suggest_claims(case_data, max_results=3)
            claim_keys = [s.claim_key for s in suggestions if not s.showstoppers]

    # Build sections
    sections: dict[str, list[DepositionQuestion]] = {}

    # 1. Foundation
    foundation = _generate_foundation_questions(witness_name, case_data, exam_type)
    if foundation:
        sections["foundation"] = foundation

    # 2. Claim elements
    element_qs = []
    for ck in claim_keys:
        element_qs.extend(_generate_claim_element_questions(case_data, ck, witness_name, exam_type))
    if element_qs:
        sections["claim_element"] = element_qs

    # 3. Authentication (cross-exam typically)
    if exam_type == "cross":
        auth_qs = _generate_authentication_questions(case_data, witness_name)
        if auth_qs:
            sections["authentication"] = auth_qs

    # 4. Impeachment (cross-exam only)
    if exam_type == "cross":
        impeach_qs = _generate_impeachment_questions(case_data, witness_name, witness_role)
        if impeach_qs:
            sections["impeachment"] = impeach_qs

    # 5. Defense anticipation
    defense_qs = _generate_defense_anticipation_questions(case_data, claim_keys, witness_name)
    if defense_qs:
        sections["defense_anticipation"] = defense_qs

    # Count and trim to max
    total = sum(len(qs) for qs in sections.values())
    if total > max_questions:
        # Trim proportionally from largest sections
        ratio = max_questions / total
        for cat in sections:
            limit = max(1, int(len(sections[cat]) * ratio))
            sections[cat] = sections[cat][:limit]
        total = sum(len(qs) for qs in sections.values())

    # Estimate duration (3 min per question average)
    duration = total * 3

    # Warnings
    warnings = []
    if witness_role == "officer" and exam_type == "cross":
        warnings.append("Officer-witness may assert qualified immunity — prepare for privilege objections")
    if not claim_keys:
        warnings.append("No claims identified — questions are generic")
    if any(ck.startswith("bivens_") for ck in claim_keys):
        warnings.append("Bivens claim: post-Egbert viability concerns — verify claim is viable before deposition")

    return DepositionOutline(
        witness_name=witness_name,
        witness_role=witness_role,
        exam_type=exam_type,
        claim_keys=claim_keys,
        total_questions=total,
        sections=sections,
        estimated_duration_minutes=duration,
        warnings=warnings,
        generated_at=str(date.today()),
    )


def format_deposition_outline(outline: DepositionOutline, verbose: bool = False) -> str:
    """Format deposition outline for CLI output."""
    lines = []

    lines.append("")
    lines.append("=" * 70)
    lines.append("         DEPOSITION QUESTION OUTLINE")
    lines.append("=" * 70)
    lines.append(f"  Witness:   {outline.witness_name} ({outline.witness_role})")
    lines.append(f"  Exam:      {outline.exam_type.upper()}")
    lines.append(f"  Claims:    {', '.join(outline.claim_keys) or 'General'}")
    lines.append(f"  Questions: {outline.total_questions}")
    lines.append(f"  Est. time: {outline.estimated_duration_minutes} minutes")

    if outline.warnings:
        lines.append("")
        for w in outline.warnings:
            lines.append(f"  [!!] {w}")

    category_labels = {
        "foundation": "FOUNDATION (FRE 602)",
        "claim_element": "CLAIM ELEMENTS",
        "authentication": "DOCUMENT AUTHENTICATION (FRE 901)",
        "impeachment": "IMPEACHMENT",
        "defense_anticipation": "DEFENSE ANTICIPATION",
    }

    for cat in ("foundation", "claim_element", "authentication", "impeachment", "defense_anticipation"):
        qs = outline.sections.get(cat, [])
        if not qs:
            continue

        lines.append("")
        lines.append(f"  ## {category_labels.get(cat, cat.upper())}")
        lines.append("")

        for i, q in enumerate(qs, 1):
            lines.append(f"   {i}. Q: {q.question_text}")
            if verbose:
                lines.append(f"      Purpose: {q.purpose}")
                if q.subcategory != cat:
                    lines.append(f"      Element: {q.subcategory}")
                if q.follow_ups:
                    for fu in q.follow_ups:
                        lines.append(f"      -> Follow-up: {fu}")
            lines.append("")

    lines.append("=" * 70)
    lines.append(f"  Generated: {outline.generated_at}")
    lines.append("")

    return "\n".join(lines)

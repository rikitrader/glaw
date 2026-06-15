"""
Complaint Drafter - Generates FRCP 8/9(b) compliant complaint sections locally.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional
from .claims import get_claim


def _names_overlap(a: str, b: str) -> bool:
    """Check if all words of the shorter name appear in the longer name."""
    a_words = set(a.split())
    b_words = set(b.split())
    shorter, longer = (a_words, b_words) if len(a_words) <= len(b_words) else (b_words, a_words)
    return bool(shorter) and shorter.issubset(longer)


@dataclass
class JurisdictionAnalysis:
    basis: str  # federal_question, diversity, supplemental
    satisfied: bool
    analysis: str
    citations: list[str]
    venue_proper: bool
    venue_analysis: str
    standing_injury: bool
    standing_causation: bool
    standing_redressability: bool


@dataclass
class ComplaintSection:
    caption: str
    parties: str
    jurisdiction: str
    venue: str
    factual_allegations: list[str]
    counts: list[str]
    prayer_for_relief: str
    jury_demand: bool
    certificate_of_service: str


def analyze_jurisdiction(case_data: dict) -> JurisdictionAnalysis:
    """Analyze subject-matter jurisdiction, venue, and standing."""
    claims = case_data.get("claims_requested", [])
    parties = case_data.get("parties", {})
    facts = case_data.get("facts", [])
    court = case_data.get("court", {})
    relief = case_data.get("relief_requested", [])

    # If auto_suggest, resolve actual claims first
    if not claims or claims == ["auto_suggest"]:
        from .suggest import suggest_claims
        claims = [s.claim_key for s in suggest_claims(case_data, 5) if not s.showstoppers]

    # Check federal question
    has_federal = False
    citations = []
    for ck in claims:
        meta = get_claim(ck)
        if meta and meta.jurisdiction == "federal_question":
            has_federal = True
            citations.append("28 U.S.C. 1331")
            break

    # Check diversity
    basis = "federal_question"
    if has_federal:
        analysis = "Federal question jurisdiction: claims arise under federal law."
    else:
        p_states = {p.get("citizenship") for p in parties.get("plaintiffs", [])}
        d_states = {d.get("citizenship") for d in parties.get("defendants", [])}
        if p_states and d_states and not p_states.intersection(d_states):
            basis = "diversity"
            citations.append("28 U.S.C. 1332")
            analysis = "Diversity jurisdiction: complete diversity and amount in controversy exceeds $75,000."
        else:
            analysis = "Jurisdiction basis requires further analysis."

    # Venue
    court_state = court.get("state", "")
    venue_proper = any(
        d.get("citizenship", "").lower() == court_state.lower()
        for d in parties.get("defendants", [])
    ) or (bool(court_state) and any(
        re.search(rf'\b{re.escape(court_state)}\b', f.get("location", "") or "", re.IGNORECASE)
        for f in facts
    ))

    # Standing
    has_injury = any(f.get("harm") for f in facts)
    defendant_names = {d.get("name", "").lower() for d in parties.get("defendants", [])} - {""}
    has_causation = any(
        f.get("harm") and any(_names_overlap(a.lower(), dn) for a in f.get("actors", []) for dn in defendant_names)
        for f in facts
    ) if defendant_names else len(facts) > 0
    has_redress = len(relief) > 0

    return JurisdictionAnalysis(
        basis=basis,
        satisfied=has_federal or basis == "diversity",
        analysis=analysis,
        citations=citations,
        venue_proper=venue_proper,
        venue_analysis="Venue proper: substantial events in this district." if venue_proper
                       else "Venue requires verification.",
        standing_injury=has_injury,
        standing_causation=has_causation,
        standing_redressability=has_redress,
    )


def generate_caption(case_data: dict) -> str:
    """Generate complaint caption."""
    court = case_data.get("court", {})
    parties = case_data.get("parties", {})
    plaintiff = (parties.get("plaintiffs", [{}])[0]).get("name", "[PLAINTIFF]")
    defendant = (parties.get("defendants", [{}])[0]).get("name", "[DEFENDANT]")

    return f"""
UNITED STATES DISTRICT COURT
{court.get('district', '[DISTRICT]').upper()}
{court.get('division', '').upper()} DIVISION

{plaintiff.upper()},
                                    Plaintiff,

v.                                              Case No. __________

{defendant.upper()},
                                    Defendant.
_______________________________________/
"""


def generate_parties_section(case_data: dict) -> str:
    """Generate PARTIES section."""
    parties = case_data.get("parties", {})
    lines = ["PARTIES\n"]
    n = 1
    for p in parties.get("plaintiffs", []):
        etype = p.get("entity_type", "individual")
        cit = p.get("citizenship", "[STATE]")
        if etype == "individual":
            desc = f"a citizen of the State of {cit}"
        elif etype == "corporation":
            desc = f"a corporation with principal place of business in {cit}"
        else:
            desc = f"an entity located in {cit}"
        lines.append(f"     {n}. Plaintiff {p.get('name', '[NAME]')} is {desc}.")
        n += 1
    for d in parties.get("defendants", []):
        dtype = d.get("type", "private")
        if dtype == "officer":
            cap = d.get("capacity", "individual")
            desc = f"an individual employed as {d.get('role_title', 'a government official')}, sued in {cap} capacity"
        elif dtype == "local":
            desc = f"a municipal corporation organized under the laws of {d.get('citizenship', '[STATE]')}"
        elif dtype == "federal":
            desc = "a federal agency of the United States"
        else:
            desc = f"an entity located in {d.get('citizenship', '[STATE]')}"
        lines.append(f"     {n}. Defendant {d.get('name', '[NAME]')} is {desc}.")
        n += 1
    return "\n".join(lines)


def generate_factual_allegations(case_data: dict) -> list[str]:
    """Generate FACTUAL ALLEGATIONS section."""
    facts = case_data.get("facts", [])
    lines = ["FACTUAL ALLEGATIONS\n"]
    for i, f in enumerate(facts, 1):
        text = ""
        if f.get("date"):
            text += f"On or about {f['date']}, "
        if f.get("location"):
            text += f"at {f['location']}, "
        text += f.get("event", "[EVENT]")
        if f.get("harm"):
            text += f". As a result, {f['harm']}"
        lines.append(f"     {i}. {text}.")
    return lines


def generate_count(case_data: dict, claim_key: str, count_num: int) -> str:
    """Generate a single COUNT section."""
    meta = get_claim(claim_key)
    if not meta:
        return f"COUNT {count_num}: [UNKNOWN CLAIM: {claim_key}]"

    plaintiff = (case_data.get("parties", {}).get("plaintiffs", [{}])[0]).get("name", "Plaintiff")
    defendant = (case_data.get("parties", {}).get("defendants", [{}])[0]).get("name", "Defendant")

    lines = [
        f"\n                             COUNT {count_num}",
        f"                    {meta.name.upper()}",
        f"                   ({meta.source})\n",
    ]
    if count_num > 1:
        lines.append(f"     Plaintiff re-alleges and incorporates by reference all preceding paragraphs.\n")

    # Generate allegations based on claim type
    lines.append(f"     As a direct and proximate result of {defendant}'s conduct, {plaintiff} suffered injuries and damages.")
    lines.append(f"\n     [DEVELOP SPECIFIC ELEMENT-BY-ELEMENT ALLEGATIONS FOR {meta.name}]")

    return "\n".join(lines)


def generate_prayer(case_data: dict) -> str:
    """Generate PRAYER FOR RELIEF."""
    relief = case_data.get("relief_requested", [])
    items = []
    if "money" in relief:
        items.append("a. Compensatory damages in an amount to be determined at trial;")
        items.append("b. Punitive damages in an amount to be determined at trial;")
    if "injunction" in relief:
        items.append(f"{chr(97 + len(items))}. Preliminary and permanent injunctive relief;")
    if "declaratory" in relief:
        items.append(f"{chr(97 + len(items))}. A declaratory judgment;")
    items.append(f"{chr(97 + len(items))}. Pre-judgment and post-judgment interest;")
    if "fees" in relief:
        items.append(f"{chr(97 + len(items))}. Reasonable attorneys' fees and costs;")
    items.append(f"{chr(97 + len(items))}. Such other and further relief as this Court deems just and proper.")

    return "PRAYER FOR RELIEF\n\n     WHEREFORE, Plaintiff respectfully requests judgment as follows:\n\n" + "\n".join(f"     {i}" for i in items)


def generate_complaint(case_data: dict) -> str:
    """Generate complete complaint skeleton."""
    claims = case_data.get("claims_requested", [])
    if not claims or claims == ["auto_suggest"]:
        from .suggest import suggest_claims
        suggestions = suggest_claims(case_data, 3)
        claims = [s.claim_key for s in suggestions if not s.showstoppers]
        if not claims and suggestions:
            claims = [suggestions[0].claim_key]

    sections = [
        generate_caption(case_data),
        "\n                              COMPLAINT\n",
        "     Plaintiff hereby sues Defendant(s) and alleges as follows:\n",
        generate_parties_section(case_data),
    ]

    jx = analyze_jurisdiction(case_data)
    sections.append(f"\nJURISDICTION\n\n     This Court has jurisdiction pursuant to {', '.join(jx.citations) or '[CITE]'} because {jx.analysis}")
    sections.append(f"\nVENUE\n\n     Venue is proper pursuant to 28 U.S.C. 1391(b) because a substantial part of events occurred in this District.")
    sections.append("\n" + "\n".join(generate_factual_allegations(case_data)))
    sections.append("\n                       CAUSES OF ACTION\n")

    for i, ck in enumerate(claims, 1):
        sections.append(generate_count(case_data, ck, i))

    sections.append("\n" + generate_prayer(case_data))
    sections.append("\n                           JURY DEMAND\n")
    sections.append("     Plaintiff demands a trial by jury on all issues so triable.")
    sections.append("\n                                        Respectfully submitted,")
    sections.append("                                        /s/ [ATTORNEY NAME]")

    return "\n".join(sections)

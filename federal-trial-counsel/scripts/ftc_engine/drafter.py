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
    failures: list[str] = field(default_factory=list)


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

    # Check diversity. Citizenship cannot be inferred from an address, and an
    # amount is not assumed merely because damages are requested.
    basis = "federal_question" if has_federal else "unverified"
    failures: list[str] = []
    if has_federal:
        analysis = "Federal question jurisdiction: claims arise under federal law."
    else:
        p_states = {p.get("domicile") for p in parties.get("plaintiffs", []) if p.get("domicile")}
        d_states = {d.get("domicile") for d in parties.get("defendants", []) if d.get("domicile")}
        amount = case_data.get("amount_in_controversy", {})
        amount_value = amount.get("value") if isinstance(amount, dict) else None
        try:
            amount_ok = float(amount_value) > 75000
        except (TypeError, ValueError):
            amount_ok = False
        parties_complete = (
            bool(parties.get("plaintiffs")) and bool(parties.get("defendants"))
            and len(p_states) == len(parties.get("plaintiffs", []))
            and len(d_states) == len(parties.get("defendants", []))
        )
        diversity_ok = parties_complete and not p_states.intersection(d_states) and amount_ok
        if diversity_ok:
            basis = "diversity"
            citations.append("28 U.S.C. 1332")
            analysis = "Diversity jurisdiction: complete diversity and amount in controversy exceeds $75,000."
        else:
            if not parties_complete:
                failures.append("every individual party requires domicile; residence is insufficient")
            if p_states.intersection(d_states):
                failures.append("opposing parties share citizenship")
            if not amount_ok:
                failures.append("a supported amount in controversy exceeding $75,000 is required")
            analysis = "Jurisdiction is not established: " + "; ".join(failures)

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
        failures=failures,
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

    element_map = case_data.get("claim_elements", {}).get(claim_key, [])
    if element_map:
        for index, item in enumerate(element_map, start=1):
            if not isinstance(item, dict) or not item.get("element") or not item.get("allegation") or not item.get("source_ids"):
                lines.append(f"     [FACT REQUIRED: verified allegation and source IDs for element {index}]")
                continue
            sources = ", ".join(str(value) for value in item["source_ids"])
            lines.append(f"     {item['allegation']} (Sources: {sources})")
    else:
        lines.append(f"     [FACT REQUIRED: source-backed element-to-fact map for {meta.name}]")

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
    if jx.satisfied:
        sections.append(f"\nJURISDICTION\n\n     This Court has jurisdiction pursuant to {', '.join(jx.citations)} because {jx.analysis}")
    else:
        sections.append(f"\nJURISDICTION\n\n     [JURISDICTION REVIEW REQUIRED: {jx.analysis}]")
    if jx.venue_proper:
        sections.append("\nVENUE\n\n     Venue is alleged under 28 U.S.C. 1391(b), subject to counsel verification of the supporting venue facts.")
    else:
        sections.append("\nVENUE\n\n     [VENUE REVIEW REQUIRED: district-specific venue facts have not been established.]")
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

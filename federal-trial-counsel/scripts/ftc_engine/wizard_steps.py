"""
Wizard step handlers — one collector function per workflow step.

Each collector takes (state, case_data), prompts the user via wizard_ui
primitives, persists via case_manager.save_case_data + advance_step, and
returns the updated case_data.

The 12 steps:
  court → plaintiffs → defendants → facts → claims → relief →
  exhaustion → limitations → goals → review → documents → generate

Steps 11 (documents) and 12 (generate) live in wizard_state.py since they
operate on the document catalog + pipeline; this module imports them back
into STEP_COLLECTORS so the dispatch map stays complete.
"""
from __future__ import annotations

from .case_manager import (
    CaseState,
    WORKFLOW_STEPS,
    save_state,
    save_case_data,
    advance_step,
)
from .wizard_ui import (
    _prompt,
    _prompt_choice,
    _prompt_multi_choice,
    _prompt_yes_no,
    _prompt_date,
    _print_header,
)
from .wizard_state import collect_document_selection, execute_pipeline


# ── Section collectors ──────────────────────────────────────────────────────

def collect_court(state: CaseState, case_data: dict) -> dict:
    """Collect court and jurisdiction information."""
    _print_header("STEP 1: COURT & JURISDICTION")

    from .districts import list_districts
    districts = list_districts()
    district_names = [f"{d.name} ({d.code})" for d in districts]
    district_names.append("Other (enter manually)")

    choice = _prompt_choice("Select district", district_names)
    if "Other" in choice:
        district = _prompt("District name", required=True,
                           description="e.g. Middle District of Florida")
        state_name = _prompt("State", required=True)
    else:
        # Parse selected district
        idx = district_names.index(choice)
        d = districts[idx]
        district = d.name
        state_name = d.state

    division = _prompt("Division", description="e.g. Tampa, Orlando")

    case_data["court"] = {
        "district": district,
        "division": division,
        "state": state_name,
    }
    save_case_data(state.case_number, case_data)
    advance_step(state, "court")
    return case_data


def collect_plaintiffs(state: CaseState, case_data: dict) -> dict:
    """Collect plaintiff information — one or more."""
    _print_header("STEP 2: PLAINTIFF INFORMATION")
    plaintiffs: list[dict] = []
    adding = True

    while adding:
        print(f"\n  --- Plaintiff #{len(plaintiffs) + 1} ---")
        p: dict = {}
        p["name"] = _prompt("Full name", required=True)
        entity_choice = _prompt_choice("Entity type", [
            "individual", "corporation", "llc", "partnership", "municipality",
        ])
        p["entity_type"] = entity_choice

        p["citizenship"] = _prompt("Citizenship / State of domicile", required=True)

        if entity_choice in ("corporation", "llc"):
            p["state_of_incorporation"] = _prompt("State of incorporation")
            p["principal_place_of_business"] = _prompt("Principal place of business")

        p["address"] = _prompt("Address")
        p["phone"] = _prompt("Phone")
        p["email"] = _prompt("Email")

        plaintiffs.append(p)
        adding = _prompt_yes_no("Add another plaintiff?")

    case_data["parties"]["plaintiffs"] = plaintiffs
    save_case_data(state.case_number, case_data)
    advance_step(state, "plaintiffs")
    return case_data


def collect_defendants(state: CaseState, case_data: dict) -> dict:
    """Collect defendant information — one or more."""
    _print_header("STEP 3: DEFENDANT INFORMATION")
    defendants: list[dict] = []
    adding = True

    while adding:
        print(f"\n  --- Defendant #{len(defendants) + 1} ---")
        d: dict = {}
        d["name"] = _prompt("Full name", required=True)
        d["entity_type"] = _prompt_choice("Entity type", [
            "individual", "corporation", "llc", "municipality",
            "federal_agency", "state_agency",
        ])
        d["type"] = _prompt_choice("Defendant type", [
            "officer", "local", "federal", "state", "private",
        ])
        d["capacity"] = _prompt_choice("Capacity sued in", [
            "individual", "official", "both",
        ])
        d["citizenship"] = _prompt("Citizenship / State", required=True)
        d["role_title"] = _prompt("Role/title", description="e.g. police officer")

        if d["entity_type"] in ("corporation", "llc"):
            d["state_of_incorporation"] = _prompt("State of incorporation")
            d["principal_place_of_business"] = _prompt("Principal place of business")

        defendants.append(d)
        adding = _prompt_yes_no("Add another defendant?")

    case_data["parties"]["defendants"] = defendants
    save_case_data(state.case_number, case_data)
    advance_step(state, "defendants")
    return case_data


def collect_facts(state: CaseState, case_data: dict) -> dict:
    """Collect factual allegations — one or more."""
    _print_header("STEP 4: FACTUAL ALLEGATIONS")
    facts: list[dict] = case_data.get("facts", [])
    adding = True

    while adding:
        print(f"\n  --- Fact #{len(facts) + 1} ---")
        f: dict = {}
        f["date"] = _prompt_date("Date of event")
        f["location"] = _prompt("Location")
        f["event"] = _prompt("What happened?", required=True,
                             description="Describe the event")
        actors = _prompt("Who was involved?", description="comma-separated")
        f["actors"] = [a.strip() for a in actors.split(",") if a.strip()] if actors else []
        f["harm"] = _prompt("What harm resulted?")
        docs = _prompt("Supporting documents?", description="comma-separated")
        f["documents"] = [d.strip() for d in docs.split(",") if d.strip()] if docs else []
        witnesses = _prompt("Witnesses?", description="comma-separated")
        f["witnesses"] = [w.strip() for w in witnesses.split(",") if w.strip()] if witnesses else []
        evidence = _prompt("Evidence?", description="comma-separated")
        f["evidence"] = [e.strip() for e in evidence.split(",") if e.strip()] if evidence else []
        f["damages_estimate"] = _prompt("Damages estimate?", description="e.g. $150,000")

        facts.append(f)
        adding = _prompt_yes_no("Add another fact?")

    case_data["facts"] = facts
    save_case_data(state.case_number, case_data)
    advance_step(state, "facts")
    return case_data


def collect_claims(state: CaseState, case_data: dict) -> dict:
    """Suggest and select claims based on case facts."""
    _print_header("STEP 5: CLAIMS SELECTION")

    from .suggest import suggest_claims
    from .claims import list_categories, get_claims_by_category

    # Auto-suggest
    suggestions = suggest_claims(case_data)
    if suggestions:
        print("\n  Auto-suggested claims based on your facts:\n")
        for i, s in enumerate(suggestions, 1):
            print(f"    {i}. [{s.score:.0f}] {s.claim_key} — {s.claim_name}")
        print()

        if _prompt_yes_no("Accept these suggestions?", default=True):
            case_data["claims_requested"] = [s.claim_key for s in suggestions]
        else:
            case_data["claims_requested"] = []
    else:
        print("\n  No claims auto-suggested from facts. Select manually.")
        case_data["claims_requested"] = []

    # Manual addition
    if _prompt_yes_no("Browse claim categories to add more?"):
        categories = list_categories()
        while True:
            cat_choice = _prompt_choice("Category", categories + ["Done — finish selection"])
            if "Done" in cat_choice:
                break
            claims = get_claims_by_category(cat_choice)
            keys = list(claims.keys())
            names = [f"{k} — {claims[k].name}" for k in keys]
            selected = _prompt_multi_choice(f"Claims in {cat_choice}", names)
            for sel in selected:
                key = sel.split(" — ")[0]
                if key not in case_data["claims_requested"]:
                    case_data["claims_requested"].append(key)

    print(f"\n  Selected {len(case_data['claims_requested'])} claim(s).")
    save_case_data(state.case_number, case_data)
    advance_step(state, "claims")
    return case_data


def collect_relief(state: CaseState, case_data: dict) -> dict:
    """Select relief types."""
    _print_header("STEP 6: RELIEF REQUESTED")
    options = [
        "money — Compensatory and/or punitive damages",
        "injunction — Court order to stop/require action",
        "declaratory — Declaration of rights",
        "fees — Attorney fees and costs",
        "restoration — Reinstatement / position restoration",
    ]
    selected = _prompt_multi_choice("Select relief types", options,
                                    preselected=[1, 4])
    case_data["relief_requested"] = [s.split(" — ")[0] for s in selected]
    save_case_data(state.case_number, case_data)
    advance_step(state, "relief")
    return case_data


def collect_exhaustion(state: CaseState, case_data: dict) -> dict:
    """Check administrative exhaustion based on selected claims."""
    _print_header("STEP 7: ADMINISTRATIVE EXHAUSTION")
    claims = case_data.get("claims_requested", [])
    exhaustion: dict = {}

    # Check what's needed
    needs_eeoc = any(c.startswith(("title_vii", "adea", "ada_")) for c in claims)
    needs_ftca = any(c.startswith("ftca_") for c in claims)
    needs_erisa = any(c.startswith("erisa_") for c in claims)
    needs_apa = any(c.startswith("apa_") for c in claims)

    if not any([needs_eeoc, needs_ftca, needs_erisa, needs_apa]):
        print("\n  No exhaustion requirements for your selected claims.")
    else:
        if needs_eeoc:
            exhaustion["eeoc_charge_filed"] = _prompt_yes_no(
                "EEOC charge filed? (required for Title VII/ADEA/ADA)")
            if exhaustion["eeoc_charge_filed"]:
                exhaustion["eeoc_right_to_sue"] = _prompt_yes_no(
                    "Right-to-sue letter received?")
        if needs_ftca:
            exhaustion["ftca_admin_claim_filed"] = _prompt_yes_no(
                "SF-95 administrative claim filed? (required for FTCA)")
        if needs_erisa:
            exhaustion["erisa_appeal_done"] = _prompt_yes_no(
                "Internal ERISA appeal completed?")
        if needs_apa:
            exhaustion["agency_final_action"] = _prompt_yes_no(
                "Agency final action received?")

    case_data["exhaustion"] = exhaustion
    save_case_data(state.case_number, case_data)
    advance_step(state, "exhaustion")
    return case_data


def collect_limitations(state: CaseState, case_data: dict) -> dict:
    """Collect statute of limitations info."""
    _print_header("STEP 8: STATUTE OF LIMITATIONS")
    key_dates: dict = {}

    injury_date = _prompt_date("Date of injury/incident")
    if injury_date:
        key_dates["injury_date"] = injury_date

    tolling = _prompt("Tolling factors?",
                      description="comma-separated, e.g. minority, mental incapacity")
    tolling_list = [t.strip() for t in tolling.split(",") if t.strip()] if tolling else []

    case_data["limitations"] = {
        "key_dates": key_dates,
        "tolling_factors": tolling_list,
    }
    save_case_data(state.case_number, case_data)
    advance_step(state, "limitations")
    return case_data


def collect_goals(state: CaseState, case_data: dict) -> dict:
    """Collect case goals."""
    _print_header("STEP 9: CASE GOALS")
    goals: dict = {}
    goals["primary"] = _prompt("Primary goal",
                               description="e.g. Obtain compensation for injuries")
    goals["secondary"] = _prompt("Secondary goal",
                                 description="e.g. Hold officer accountable")
    case_data["goals"] = goals
    save_case_data(state.case_number, case_data)
    advance_step(state, "goals")
    return case_data


# ── Case summary review ────────────────────────────────────────────────────

def show_case_summary(case_data: dict) -> None:
    """Display complete case summary for review."""
    _print_header("STEP 10: CASE SUMMARY REVIEW")

    court = case_data.get("court", {})
    parties = case_data.get("parties", {})
    facts = case_data.get("facts", [])
    claims = case_data.get("claims_requested", [])
    relief = case_data.get("relief_requested", [])
    exhaustion = case_data.get("exhaustion", {})
    limitations = case_data.get("limitations", {})
    goals = case_data.get("goals", {})

    print(f"\n  Court:       {court.get('district', '—')} / {court.get('division', '—')}")
    print(f"  State:       {court.get('state', '—')}")
    print()

    # Plaintiffs
    pls = parties.get("plaintiffs", [])
    for p in pls:
        print(f"  Plaintiff:   {p.get('name', '—')} ({p.get('entity_type', '—')}, {p.get('citizenship', '—')})")

    # Defendants
    defs = parties.get("defendants", [])
    for d in defs:
        cap = d.get("capacity", "—")
        print(f"  Defendant:   {d.get('name', '—')} ({d.get('type', '—')}, {cap}, {d.get('citizenship', '—')})")

    print(f"\n  Facts:       {len(facts)} allegation(s)")
    print(f"  Claims:      {', '.join(claims) if claims else '—'}")
    print(f"  Relief:      {', '.join(relief) if relief else '—'}")

    # Exhaustion
    if exhaustion:
        exh_items = [f"{k}={'Y' if v else 'N'}" for k, v in exhaustion.items()]
        print(f"  Exhaustion:  {', '.join(exh_items)}")
    else:
        print("  Exhaustion:  N/A")

    # SOL
    injury = limitations.get("key_dates", {}).get("injury_date", "")
    print(f"  Injury date: {injury or '—'}")

    # Goals
    print(f"  Primary:     {goals.get('primary', '—')}")
    print(f"  Secondary:   {goals.get('secondary', '—')}")
    print()


def review_case(state: CaseState, case_data: dict) -> dict:
    """Show summary, let user go back to fix sections."""
    show_case_summary(case_data)

    if _prompt_yes_no("Is this correct?", default=True):
        advance_step(state, "review")
        return case_data

    # Let user go back
    step_labels = [f"{k} — {label}" for k, label in WORKFLOW_STEPS[:9]]
    choice = _prompt_choice("Go back to which section?", step_labels)
    go_back = choice.split(" — ")[0]
    # Remove from completed so it gets re-run
    if go_back in state.completed_steps:
        state.completed_steps.remove(go_back)
    state.current_step = go_back
    if go_back not in state.pending_steps:
        state.pending_steps.append(go_back)
    save_state(state)
    return case_data


# ── Step collectors map ────────────────────────────────────────────────────

STEP_COLLECTORS = {
    "court": collect_court,
    "plaintiffs": collect_plaintiffs,
    "defendants": collect_defendants,
    "facts": collect_facts,
    "claims": collect_claims,
    "relief": collect_relief,
    "exhaustion": collect_exhaustion,
    "limitations": collect_limitations,
    "goals": collect_goals,
    "review": review_case,
    "documents": collect_document_selection,
    "generate": execute_pipeline,
}

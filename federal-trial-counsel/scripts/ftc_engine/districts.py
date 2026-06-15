"""
District Portability Layer — Configuration system to swap Local Rules and
standard orders for any Federal District.

Replaces hardcoded M.D. Fla. references throughout the engine with a
configurable district context. Supports 7 built-in districts with extensible
data structures for additional districts.

Usage:
  ftc district list                  # List all available districts
  ftc district set sdfl              # Switch to S.D. Florida
  ftc district info ndcal            # Show N.D. California details
  ftc district current               # Show active district
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class JudgeInfo:
    name: str
    title: str  # "District Judge", "Magistrate Judge", "Senior Judge"
    division: str
    preferences_url: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass
class DistrictConfig:
    code: str                           # "mdfl", "sdfl", "ndcal"
    name: str                           # "Middle District of Florida"
    circuit: str                        # "11th Circuit"
    circuit_number: int                 # 11
    state: str                          # "Florida"
    divisions: list[str] = field(default_factory=list)

    # Page limits
    motion_page_limit: int = 25
    response_page_limit: int = 25
    reply_page_limit: int = 10

    # Timing
    response_days: int = 21
    reply_days: int = 7

    # Discovery
    interrogatory_limit: int = 25
    deposition_limit: int = 10
    meet_and_confer_required: bool = True
    meet_and_confer_method: str = "phone_or_in_person"  # "any", "written_ok"

    # ADR
    mediation_required: bool = False

    # SOL
    sol_state: str = ""                 # State whose personal-injury SOL applies to 1983
    sol_personal_injury_years: float = 4.0

    # Formatting
    font_name: str = "Times New Roman"
    font_size_pt: int = 12
    line_spacing: float = 2.0
    margin_inches: float = 1.0

    # CM/ECF
    cm_ecf_required: bool = True
    filing_format: str = "pdf"          # "pdf", "pdf_or_docx"

    # Court info
    court_address: str = ""
    clerk_phone: str = ""

    # Local rule prefix
    local_rule_prefix: str = "Local Rule"

    # Misc
    special_rules: list[str] = field(default_factory=list)
    judges: list[JudgeInfo] = field(default_factory=list)
    last_updated: str = "2025-01"


@dataclass
class DistrictContext:
    """Active district configuration for the current session."""
    config: DistrictConfig
    division: str = ""
    active_judge: Optional[JudgeInfo] = None


# ── Built-in District Database ───────────────────────────────────────────────

DISTRICTS: dict[str, DistrictConfig] = {
    "mdfl": DistrictConfig(
        code="mdfl",
        name="Middle District of Florida",
        circuit="11th Circuit",
        circuit_number=11,
        state="Florida",
        divisions=["Tampa", "Orlando", "Jacksonville", "Fort Myers", "Ocala"],
        motion_page_limit=25,
        response_page_limit=25,
        reply_page_limit=10,
        response_days=21,
        reply_days=7,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="phone_or_in_person",
        mediation_required=True,
        sol_state="Florida",
        sol_personal_injury_years=4.0,
        court_address="401 W. Central Blvd., Suite 1100, Orlando, FL 32801",
        clerk_phone="(407) 835-4200",
        local_rule_prefix="Local Rule",
        special_rules=[
            "Local Rule 3.01(g): meet-and-confer must be in person or by phone, NOT email",
            "Local Rule 9.01: mediation required for all cases",
            "Local Rule 6.01: magistrate consent required for dispositive matters",
            "Pro se handbook available at flmd.uscourts.gov",
        ],
    ),

    "sdfl": DistrictConfig(
        code="sdfl",
        name="Southern District of Florida",
        circuit="11th Circuit",
        circuit_number=11,
        state="Florida",
        divisions=["Miami", "Fort Lauderdale", "West Palm Beach", "Key West"],
        motion_page_limit=20,
        response_page_limit=20,
        reply_page_limit=10,
        response_days=14,
        reply_days=7,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="phone_or_in_person",
        mediation_required=True,
        sol_state="Florida",
        sol_personal_injury_years=4.0,
        court_address="400 N. Miami Ave., Miami, FL 33128",
        clerk_phone="(305) 523-5100",
        local_rule_prefix="Local Rule",
        special_rules=[
            "Local Rule 7.1(a)(3): motions limited to 20 pages",
            "Local Rule 16.1: mediation required within 150 days of answer",
            "Local Rule 7.1: separate statement of undisputed facts for summary judgment",
            "Local Rule 88.9: assigned duty judges handle emergency motions",
        ],
    ),

    "ndcal": DistrictConfig(
        code="ndcal",
        name="Northern District of California",
        circuit="9th Circuit",
        circuit_number=9,
        state="California",
        divisions=["San Francisco", "San Jose", "Oakland", "Eureka"],
        motion_page_limit=25,
        response_page_limit=25,
        reply_page_limit=15,
        response_days=14,
        reply_days=7,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="any",
        mediation_required=False,
        sol_state="California",
        sol_personal_injury_years=2.0,
        court_address="450 Golden Gate Ave., San Francisco, CA 94102",
        clerk_phone="(415) 522-2000",
        local_rule_prefix="Civil L.R.",
        special_rules=[
            "Civil L.R. 7-2: no hearing on motion unless ordered by judge",
            "Civil L.R. 7-4: tentative rulings issued before hearings",
            "Civil L.R. 36-1: early neutral evaluation (ENE) program",
            "ADR required under Civil L.R. 16-8",
            "Patent Local Rules for IP cases",
        ],
    ),

    "sdny": DistrictConfig(
        code="sdny",
        name="Southern District of New York",
        circuit="2nd Circuit",
        circuit_number=2,
        state="New York",
        divisions=["Manhattan", "White Plains"],
        motion_page_limit=25,
        response_page_limit=25,
        reply_page_limit=10,
        response_days=14,
        reply_days=7,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="any",
        mediation_required=False,
        sol_state="New York",
        sol_personal_injury_years=3.0,
        court_address="500 Pearl St., New York, NY 10007",
        clerk_phone="(212) 805-0136",
        local_rule_prefix="Local Civil Rule",
        special_rules=[
            "Local Civil Rule 6.1: letter motions for non-dispositive issues",
            "Local Civil Rule 33.3: Uniform Interrogatories adopted by individual judges",
            "Local Civil Rule 56.1: Rule 56.1 Statement required for summary judgment",
            "Individual judge practices vary significantly — check judge's webpage",
            "Most judges require pre-motion conference before filing MTD or SJ",
        ],
    ),

    "edva": DistrictConfig(
        code="edva",
        name="Eastern District of Virginia",
        circuit="4th Circuit",
        circuit_number=4,
        state="Virginia",
        divisions=["Alexandria", "Norfolk", "Newport News", "Richmond"],
        motion_page_limit=30,
        response_page_limit=30,
        reply_page_limit=15,
        response_days=11,
        reply_days=3,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="any",
        mediation_required=False,
        sol_state="Virginia",
        sol_personal_injury_years=2.0,
        court_address="401 Courthouse Sq., Alexandria, VA 22314",
        clerk_phone="(703) 299-2100",
        local_rule_prefix="Local Rule",
        special_rules=[
            "Known as the 'Rocket Docket' — fastest federal court in the U.S.",
            "Local Rule 7(F): 11-day response period, 3-day reply period",
            "Discovery typically completed within 5 months",
            "Trial dates set early and rarely continued",
            "Cases move from complaint to trial in 8-12 months",
        ],
    ),

    "ndill": DistrictConfig(
        code="ndill",
        name="Northern District of Illinois",
        circuit="7th Circuit",
        circuit_number=7,
        state="Illinois",
        divisions=["Chicago", "Rockford"],
        motion_page_limit=15,
        response_page_limit=15,
        reply_page_limit=10,
        response_days=21,
        reply_days=14,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="any",
        mediation_required=False,
        sol_state="Illinois",
        sol_personal_injury_years=2.0,
        court_address="219 S. Dearborn St., Chicago, IL 60604",
        clerk_phone="(312) 435-5670",
        local_rule_prefix="LR",
        special_rules=[
            "LR 7.1: motions limited to 15 pages (strictly enforced)",
            "LR 56.1: Local Rule 56.1 statements required for summary judgment",
            "LR 83.11: initial status report required within 14 days of answer",
            "Seventh Circuit limits briefing to 30 pages on appeal",
        ],
    ),

    "ddc": DistrictConfig(
        code="ddc",
        name="District of Columbia",
        circuit="D.C. Circuit",
        circuit_number=0,  # D.C. has no numbered circuit
        state="District of Columbia",
        divisions=["Washington"],
        motion_page_limit=45,
        response_page_limit=45,
        reply_page_limit=25,
        response_days=14,
        reply_days=7,
        interrogatory_limit=25,
        deposition_limit=10,
        meet_and_confer_required=True,
        meet_and_confer_method="any",
        mediation_required=False,
        sol_state="District of Columbia",
        sol_personal_injury_years=3.0,
        court_address="333 Constitution Ave., NW, Washington, DC 20001",
        clerk_phone="(202) 354-3000",
        local_rule_prefix="LCvR",
        special_rules=[
            "LCvR 7(a): generous 45-page limit for motions",
            "LCvR 7(d): meet-and-confer required before filing any motion",
            "Primary venue for APA/federal agency challenges",
            "Heavy administrative law docket — specialized APA expertise on bench",
            "D.C. Circuit highly influential for federal regulatory law",
        ],
    ),
}


# ── State SOL lookup ─────────────────────────────────────────────────────────

# Personal injury SOL by state (years) — used to override 1983/Bivens SOL
_STATE_PI_SOL_YEARS: dict[str, float] = {
    "Alabama": 2.0, "Alaska": 2.0, "Arizona": 2.0, "Arkansas": 3.0,
    "California": 2.0, "Colorado": 2.0, "Connecticut": 2.0, "Delaware": 2.0,
    "District of Columbia": 3.0, "Florida": 4.0, "Georgia": 2.0,
    "Hawaii": 2.0, "Idaho": 2.0, "Illinois": 2.0, "Indiana": 2.0,
    "Iowa": 2.0, "Kansas": 2.0, "Kentucky": 1.0, "Louisiana": 1.0,
    "Maine": 6.0, "Maryland": 3.0, "Massachusetts": 3.0, "Michigan": 3.0,
    "Minnesota": 2.0, "Mississippi": 3.0, "Missouri": 5.0, "Montana": 3.0,
    "Nebraska": 4.0, "Nevada": 2.0, "New Hampshire": 3.0, "New Jersey": 2.0,
    "New Mexico": 3.0, "New York": 3.0, "North Carolina": 3.0,
    "North Dakota": 6.0, "Ohio": 2.0, "Oklahoma": 2.0, "Oregon": 2.0,
    "Pennsylvania": 2.0, "Rhode Island": 3.0, "South Carolina": 3.0,
    "South Dakota": 3.0, "Tennessee": 1.0, "Texas": 2.0, "Utah": 4.0,
    "Vermont": 3.0, "Virginia": 2.0, "Washington": 3.0,
    "West Virginia": 2.0, "Wisconsin": 3.0, "Wyoming": 4.0,
}

# Claims that borrow state personal-injury SOL (1983/Bivens)
_STATE_SOL_CLAIMS = {
    "1983_first_amendment_retaliation",
    "1983_first_amendment_speech_restriction",
    "1983_fourth_excessive_force",
    "1983_fourth_false_arrest",
    "1983_fourth_unlawful_search_seizure",
    "1983_fourteenth_procedural_due_process",
    "1983_fourteenth_substantive_due_process",
    "1983_fourteenth_equal_protection",
    "1983_monell_municipal_liability",
    "1985_conspiracy",
    "1983_eighth_deliberate_indifference",
    "bivens_fourth_search_seizure",
    "bivens_fifth_due_process",
    "bivens_eighth_deliberate_indifference",
    "lanham_trademark_infringement",
    "erisa_502a1b_benefits",
    "erisa_502a3_equitable_relief",
}


# ── Config persistence ───────────────────────────────────────────────────────

_CONFIG_DIR = Path.home() / ".ftc"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_config() -> dict:
    """Load persistent configuration."""
    if _CONFIG_FILE.exists():
        try:
            return json.loads(_CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_config(config: dict):
    """Save persistent configuration."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(config, indent=2))


# ── Public API ───────────────────────────────────────────────────────────────

def get_district(code: str) -> DistrictConfig | None:
    """Look up a district by its short code (case-insensitive)."""
    return DISTRICTS.get(code.lower())


def list_districts() -> list[DistrictConfig]:
    """Return all available district configurations, sorted by code."""
    return sorted(DISTRICTS.values(), key=lambda d: d.code)


def get_active_district() -> DistrictContext:
    """Return the currently active district. Default: mdfl/Orlando."""
    config = _load_config()
    code = config.get("active_district", "mdfl")
    division = config.get("active_division", "")

    district = get_district(code) or DISTRICTS["mdfl"]
    if not division and district.divisions:
        division = district.divisions[0]

    return DistrictContext(config=district, division=division)


def set_active_district(code: str, division: str | None = None) -> DistrictContext:
    """Set the active district. Persists to ~/.ftc/config.json.

    Args:
        code: District code (e.g., "sdfl", "ndcal")
        division: Optional division within the district

    Returns:
        The new DistrictContext

    Raises:
        ValueError: If district code is unknown
    """
    district = get_district(code)
    if not district:
        available = ", ".join(sorted(DISTRICTS.keys()))
        raise ValueError(f"Unknown district: {code}. Available: {available}")

    if division and division not in district.divisions:
        raise ValueError(
            f"Unknown division '{division}' for {district.name}. "
            f"Available: {', '.join(district.divisions)}"
        )

    if not division and district.divisions:
        division = district.divisions[0]

    config = _load_config()
    config["active_district"] = code.lower()
    config["active_division"] = division or ""
    _save_config(config)

    return DistrictContext(config=district, division=division or "")


def get_sol_days_for_district(claim_key: str, district_code: str | None = None) -> int:
    """Get SOL days for a claim, adjusted for the district's state SOL.

    For 1983/Bivens claims that borrow the forum state's personal-injury SOL,
    this returns the correct value based on the district's state.

    Args:
        claim_key: The claim key (e.g., "1983_fourth_excessive_force")
        district_code: Optional district code. Uses active district if None.

    Returns:
        SOL period in days
    """
    from .sol import SOL_DAYS

    # If not a state-SOL-borrowing claim, return the standard value
    if claim_key not in _STATE_SOL_CLAIMS:
        return SOL_DAYS.get(claim_key, 1461)

    # Get the district's state
    if district_code:
        district = get_district(district_code)
    else:
        district = get_active_district().config

    if not district:
        return SOL_DAYS.get(claim_key, 1461)

    # Look up the state's personal-injury SOL
    years = _STATE_PI_SOL_YEARS.get(district.sol_state or district.state, 4.0)
    return int(years * 365.25)


def get_page_limits(district_code: str | None = None) -> dict[str, int]:
    """Return motion/response/reply page limits for a district.

    Args:
        district_code: Optional district code. Uses active district if None.

    Returns:
        Dict with keys: motion, response, reply
    """
    if district_code:
        district = get_district(district_code)
    else:
        district = get_active_district().config

    if not district:
        district = DISTRICTS["mdfl"]

    return {
        "motion": district.motion_page_limit,
        "response": district.response_page_limit,
        "reply": district.reply_page_limit,
    }


def get_formatting_config(district_code: str | None = None) -> dict:
    """Return formatting configuration for a district.

    Args:
        district_code: Optional district code. Uses active district if None.

    Returns:
        Dict with keys: font_name, font_size_pt, line_spacing, margin_inches
    """
    if district_code:
        district = get_district(district_code)
    else:
        district = get_active_district().config

    if not district:
        district = DISTRICTS["mdfl"]

    return {
        "font_name": district.font_name,
        "font_size_pt": district.font_size_pt,
        "line_spacing": district.line_spacing,
        "margin_inches": district.margin_inches,
    }


def get_district_name(district_code: str | None = None) -> str:
    """Get the human-readable name of a district.

    Args:
        district_code: Optional district code. Uses active district if None.

    Returns:
        District name (e.g., "Middle District of Florida")
    """
    if district_code:
        district = get_district(district_code)
    else:
        district = get_active_district().config

    if not district:
        return "Middle District of Florida"

    return district.name


def format_district_info(config: DistrictConfig) -> str:
    """Format district info for CLI display."""
    lines = []
    lines.append(f"District:    {config.name} ({config.code.upper()})")
    lines.append(f"Circuit:     {config.circuit}")
    lines.append(f"State:       {config.state}")
    lines.append(f"Divisions:   {', '.join(config.divisions)}")
    lines.append(f"Court:       {config.court_address}")
    lines.append(f"Clerk:       {config.clerk_phone}")
    lines.append("")
    lines.append("Procedural Rules:")
    lines.append(f"  Motion page limit:      {config.motion_page_limit} pages")
    lines.append(f"  Response page limit:    {config.response_page_limit} pages")
    lines.append(f"  Reply page limit:       {config.reply_page_limit} pages")
    lines.append(f"  Response deadline:      {config.response_days} days")
    lines.append(f"  Reply deadline:         {config.reply_days} days")
    lines.append(f"  Interrogatory limit:    {config.interrogatory_limit}")
    lines.append(f"  Deposition limit:       {config.deposition_limit}")
    lines.append(f"  Meet & confer:          {'Required' if config.meet_and_confer_required else 'Not required'} ({config.meet_and_confer_method})")
    lines.append(f"  Mediation:              {'Required' if config.mediation_required else 'Not required'}")
    lines.append(f"  Local rule prefix:      {config.local_rule_prefix}")
    lines.append("")
    lines.append("SOL / Formatting:")
    lines.append(f"  State PI SOL:           {config.sol_personal_injury_years} years ({config.sol_state or config.state})")
    lines.append(f"  Font:                   {config.font_name} {config.font_size_pt}pt")
    lines.append(f"  Line spacing:           {config.line_spacing}")
    lines.append(f"  Margins:                {config.margin_inches}\" all sides")
    lines.append(f"  CM/ECF:                 {'Required' if config.cm_ecf_required else 'Optional'}")
    lines.append(f"  Filing format:          {config.filing_format.upper()}")

    if config.special_rules:
        lines.append("")
        lines.append("Special Rules:")
        for rule in config.special_rules:
            lines.append(f"  * {rule}")

    if config.judges:
        lines.append("")
        lines.append("Judges:")
        for j in config.judges:
            lines.append(f"  {j.title} {j.name} ({j.division})")
            for note in j.notes:
                lines.append(f"    - {note}")

    lines.append("")
    lines.append(f"Last updated: {config.last_updated}")

    return "\n".join(lines)


def format_district_list() -> str:
    """Format all districts as a table for CLI display."""
    lines = []
    lines.append(f"{'Code':<8} {'District':<35} {'Circuit':<15} {'State SOL':>10}")
    lines.append("-" * 70)
    for d in list_districts():
        lines.append(f"{d.code:<8} {d.name:<35} {d.circuit:<15} {d.sol_personal_injury_years:>7.0f}y")
    return "\n".join(lines)

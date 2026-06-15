"""
Filing Calendar — Generates a complete map of all legal documents with
filing dates, deadlines, and dependencies for a federal case.

Produces a chronological document map showing:
- Pre-filing documents (JS-44, summons, etc.)
- Initial pleadings and service deadlines
- Response/reply deadlines
- Discovery deadlines
- Dispositive motion deadlines
- Trial-related deadlines

Integrates with districts (for response days), claims, and sol modules.

Usage:
  ftc calendar -i case.json
  ftc calendar -i case.json --filing-date 2026-03-01
  ftc calendar -i case.json --format detailed
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta, datetime
from typing import Optional


@dataclass
class CalendarEntry:
    document: str                    # "Complaint", "Summons", "Answer/MTD"
    category: str                    # pre_filing | pleading | service | discovery | dispositive | trial | post_trial
    deadline: date
    relative_days: int               # Days from filing date
    description: str                 # What needs to happen
    rule_authority: str = ""         # "FRCP 4(m)", "Local Rule 3.01"
    status: str = "pending"          # pending | filed | overdue
    depends_on: str = ""             # What triggers this deadline
    priority: str = "high"           # critical | high | medium | low
    notes: list[str] = field(default_factory=list)


@dataclass
class FilingCalendar:
    case_name: str
    filing_date: date
    district_code: str
    entries: list[CalendarEntry] = field(default_factory=list)
    total_documents: int = 0
    critical_deadlines: int = 0
    estimated_trial_date: str = ""
    generated_at: str = ""


# ── Calendar Generation ─────────────────────────────────────────────────────

def _get_district_timings(district_code: str | None) -> dict:
    """Get district-specific timing rules."""
    from .districts import get_district, get_active_district

    if district_code:
        config = get_district(district_code)
    else:
        ctx = get_active_district()
        config = ctx.config

    if not config:
        return {
            "response_days": 21, "reply_days": 7,
            "motion_page_limit": 25, "district_name": "Unknown District",
            "mediation_required": False,
        }

    return {
        "response_days": config.response_days,
        "reply_days": config.reply_days,
        "motion_page_limit": config.motion_page_limit,
        "district_name": config.name,
        "mediation_required": config.mediation_required,
    }


def _build_pre_filing_entries(filing_date: date) -> list[CalendarEntry]:
    """Documents needed before or at filing."""
    entries = []

    entries.append(CalendarEntry(
        document="JS-44 Civil Cover Sheet",
        category="pre_filing",
        deadline=filing_date,
        relative_days=0,
        description="Complete and file with the complaint",
        rule_authority="Local Rule / CM/ECF requirement",
        priority="high",
        notes=["Required for all new civil actions in federal court"],
    ))

    entries.append(CalendarEntry(
        document="Complaint",
        category="pleading",
        deadline=filing_date,
        relative_days=0,
        description="File initial complaint via CM/ECF",
        rule_authority="FRCP 3 (commencement), FRCP 8 (pleading standard)",
        priority="critical",
        notes=["Must meet Twombly/Iqbal plausibility standard"],
    ))

    entries.append(CalendarEntry(
        document="Summons (per defendant)",
        category="pre_filing",
        deadline=filing_date,
        relative_days=0,
        description="Issue summons for each defendant",
        rule_authority="FRCP 4(b)",
        priority="high",
        notes=["Clerk issues summons upon filing"],
    ))

    return entries


def _build_service_entries(filing_date: date, case_data: dict) -> list[CalendarEntry]:
    """Service-related deadlines."""
    entries = []
    defendants = case_data.get("parties", {}).get("defendants", [])

    service_deadline = filing_date + timedelta(days=90)

    for d in defendants:
        d_name = d.get("name", "Defendant")
        d_type = d.get("type", "private")

        if d_type == "federal":
            entries.append(CalendarEntry(
                document=f"Service on {d_name} (Federal)",
                category="service",
                deadline=service_deadline,
                relative_days=90,
                description="Serve U.S. Attorney + agency + Attorney General per FRCP 4(i)",
                rule_authority="FRCP 4(i)",
                priority="critical",
                depends_on="Complaint filing",
                notes=["Must serve: (1) civil process clerk for USAO, (2) agency, (3) AG by certified mail"],
            ))
        else:
            entries.append(CalendarEntry(
                document=f"Service on {d_name}",
                category="service",
                deadline=service_deadline,
                relative_days=90,
                description=f"Complete service of process on {d_name}",
                rule_authority="FRCP 4(c)-(e), 4(m)",
                priority="critical",
                depends_on="Complaint filing",
                notes=["Failure to serve within 90 days may result in dismissal without prejudice"],
            ))

    return entries


def _build_response_entries(
    filing_date: date, case_data: dict, timings: dict
) -> list[CalendarEntry]:
    """Answer/MTD and reply deadlines."""
    entries = []
    defendants = case_data.get("parties", {}).get("defendants", [])
    resp_days = timings["response_days"]

    for d in defendants:
        d_name = d.get("name", "Defendant")
        d_type = d.get("type", "private")
        actual_days = 60 if d_type == "federal" else resp_days

        # Assume service on day 30 (reasonable estimate)
        est_service = filing_date + timedelta(days=30)
        answer_deadline = est_service + timedelta(days=actual_days)

        entries.append(CalendarEntry(
            document=f"Answer/MTD from {d_name}",
            category="pleading",
            deadline=answer_deadline,
            relative_days=(answer_deadline - filing_date).days,
            description=f"Defendant's answer or Rule 12 motion due ({actual_days}d from service)",
            rule_authority="FRCP 12(a)(1)" if d_type != "federal" else "FRCP 12(a)(2)-(3)",
            priority="high",
            depends_on=f"Service on {d_name}",
            notes=[f"{actual_days} days from service" + (" (60 days for U.S. government)" if d_type == "federal" else "")],
        ))

    return entries


def _build_corporate_disclosure_entries(filing_date: date, case_data: dict) -> list[CalendarEntry]:
    """FRCP 7.1 corporate disclosure deadlines."""
    entries = []
    all_parties = (
        case_data.get("parties", {}).get("plaintiffs", []) +
        case_data.get("parties", {}).get("defendants", [])
    )

    for p in all_parties:
        etype = p.get("entity_type", "").lower()
        if etype in ("corporation", "llc", "partnership", "limited_liability_company", "corporate"):
            entries.append(CalendarEntry(
                document=f"Corporate Disclosure — {p['name']}",
                category="pleading",
                deadline=filing_date,
                relative_days=0,
                description=f"FRCP 7.1 corporate disclosure for {p['name']}",
                rule_authority="FRCP 7.1",
                priority="high",
                notes=["Due with first filing. Identifies parent corps and 10%+ public holders."],
            ))

    return entries


def _build_discovery_entries(filing_date: date, timings: dict) -> list[CalendarEntry]:
    """Standard discovery milestones."""
    entries = []

    # Rule 26(f) conference — typically 21 days before scheduling conference
    r26f_date = filing_date + timedelta(days=90)
    entries.append(CalendarEntry(
        document="Rule 26(f) Conference",
        category="discovery",
        deadline=r26f_date,
        relative_days=90,
        description="Parties' planning meeting — discuss discovery, ESI, scheduling",
        rule_authority="FRCP 26(f)",
        priority="high",
        notes=["Must occur at least 21 days before scheduling conference"],
    ))

    # Initial disclosures — 14 days after Rule 26(f)
    init_disc = r26f_date + timedelta(days=14)
    entries.append(CalendarEntry(
        document="Initial Disclosures (Rule 26(a)(1))",
        category="discovery",
        deadline=init_disc,
        relative_days=(init_disc - filing_date).days,
        description="Exchange witness lists, documents, damages computation, insurance",
        rule_authority="FRCP 26(a)(1)",
        priority="critical",
        notes=["14 days after Rule 26(f) conference unless otherwise ordered"],
    ))

    # Fact discovery cutoff (estimate: 6 months from filing)
    fact_disc = filing_date + timedelta(days=180)
    entries.append(CalendarEntry(
        document="Fact Discovery Cutoff",
        category="discovery",
        deadline=fact_disc,
        relative_days=180,
        description="All fact discovery (depositions, interrogatories, RFPs, RFAs) must be completed",
        rule_authority="FRCP 16(b); Scheduling Order",
        priority="critical",
        notes=["Date set by scheduling order; this is an estimate"],
    ))

    # Expert disclosures (estimate: 7 months)
    expert_disc = filing_date + timedelta(days=210)
    entries.append(CalendarEntry(
        document="Expert Disclosures (Rule 26(a)(2))",
        category="discovery",
        deadline=expert_disc,
        relative_days=210,
        description="Disclose expert witnesses with written reports",
        rule_authority="FRCP 26(a)(2)",
        priority="high",
        notes=["Date set by scheduling order; rebuttal experts due 30 days after"],
    ))

    # Rebuttal expert disclosures
    rebuttal = expert_disc + timedelta(days=30)
    entries.append(CalendarEntry(
        document="Rebuttal Expert Disclosures",
        category="discovery",
        deadline=rebuttal,
        relative_days=(rebuttal - filing_date).days,
        description="Rebuttal expert witness disclosures due",
        rule_authority="FRCP 26(a)(2)(D)(ii)",
        priority="high",
        depends_on="Expert Disclosures",
    ))

    # Mediation (if required)
    if timings.get("mediation_required"):
        med_date = filing_date + timedelta(days=150)
        entries.append(CalendarEntry(
            document="Court-Ordered Mediation",
            category="discovery",
            deadline=med_date,
            relative_days=150,
            description="Mediation conference per local rule requirement",
            rule_authority="Local Rule",
            priority="high",
            notes=["Required by district; date set by scheduling order"],
        ))

    return entries


def _build_dispositive_entries(filing_date: date) -> list[CalendarEntry]:
    """Summary judgment and Daubert deadlines."""
    entries = []

    # Dispositive motions (estimate: 8-9 months)
    disp_date = filing_date + timedelta(days=270)
    entries.append(CalendarEntry(
        document="Dispositive Motions Deadline",
        category="dispositive",
        deadline=disp_date,
        relative_days=270,
        description="Last day to file summary judgment (FRCP 56) and Daubert motions",
        rule_authority="FRCP 56; Scheduling Order",
        priority="critical",
        notes=["Date set by scheduling order; this is an estimate",
               "Opposition due per local rule response days"],
    ))

    return entries


def _build_trial_entries(filing_date: date) -> list[CalendarEntry]:
    """Trial-related deadlines."""
    entries = []

    # Pretrial conference (estimate: 11 months)
    pretrial = filing_date + timedelta(days=330)
    entries.append(CalendarEntry(
        document="Final Pretrial Conference",
        category="trial",
        deadline=pretrial,
        relative_days=330,
        description="File joint pretrial statement; exchange exhibit/witness lists",
        rule_authority="FRCP 16(e)",
        priority="critical",
        notes=["Pretrial order supersedes pleadings (FRCP 16(d))"],
    ))

    # Motions in limine (typically 14-21 days before trial)
    mil_date = filing_date + timedelta(days=345)
    entries.append(CalendarEntry(
        document="Motions in Limine",
        category="trial",
        deadline=mil_date,
        relative_days=345,
        description="File motions to exclude/admit evidence",
        rule_authority="FRE 104; Local Rule",
        priority="high",
        notes=["Typically due 14-21 days before trial per local rule"],
    ))

    # Trial (estimate: 12 months)
    trial = filing_date + timedelta(days=365)
    entries.append(CalendarEntry(
        document="TRIAL",
        category="trial",
        deadline=trial,
        relative_days=365,
        description="Trial date (estimate — set by scheduling order)",
        rule_authority="FRCP 16(b)",
        priority="critical",
        notes=["Actual date set by scheduling order; may vary significantly"],
    ))

    return entries


def _build_post_trial_entries(filing_date: date) -> list[CalendarEntry]:
    """Post-trial deadlines."""
    entries = []
    trial_date = filing_date + timedelta(days=365)

    entries.append(CalendarEntry(
        document="Post-Trial Motions (JMOL/New Trial)",
        category="post_trial",
        deadline=trial_date + timedelta(days=28),
        relative_days=393,
        description="Renewed JMOL (FRCP 50(b)) or New Trial (FRCP 59) motions",
        rule_authority="FRCP 50(b), FRCP 59(b)",
        priority="critical",
        depends_on="TRIAL",
        notes=["28 days from entry of judgment"],
    ))

    entries.append(CalendarEntry(
        document="Notice of Appeal",
        category="post_trial",
        deadline=trial_date + timedelta(days=30),
        relative_days=395,
        description="File notice of appeal to the Circuit Court",
        rule_authority="FRAP 4(a)(1)(A)",
        priority="critical",
        depends_on="TRIAL",
        notes=["30 days from entry of judgment (60 days if US is a party)"],
    ))

    return entries


# ── Main API ────────────────────────────────────────────────────────────────

def generate_filing_calendar(
    case_data: dict,
    filing_date_str: str | None = None,
    district_code: str | None = None,
) -> FilingCalendar:
    """Generate a complete filing calendar for a case.

    Args:
        case_data: The case JSON data
        filing_date_str: Filing date in YYYY-MM-DD (defaults to today)
        district_code: District code for timing rules (uses active district if None)

    Returns:
        FilingCalendar with all entries sorted chronologically
    """
    # Parse filing date
    if filing_date_str:
        try:
            filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
        except ValueError:
            filing_date = date.today()
    else:
        filing_date = date.today()

    # Get district timings
    timings = _get_district_timings(district_code)

    # Build all entries
    entries = []
    entries.extend(_build_pre_filing_entries(filing_date))
    entries.extend(_build_service_entries(filing_date, case_data))
    entries.extend(_build_response_entries(filing_date, case_data, timings))
    entries.extend(_build_corporate_disclosure_entries(filing_date, case_data))
    entries.extend(_build_discovery_entries(filing_date, timings))
    entries.extend(_build_dispositive_entries(filing_date))
    entries.extend(_build_trial_entries(filing_date))
    entries.extend(_build_post_trial_entries(filing_date))

    # Sort by deadline
    entries.sort(key=lambda e: e.deadline)

    # Mark overdue
    today = date.today()
    for e in entries:
        if e.deadline < today:
            e.status = "overdue"

    # Case name
    parties = case_data.get("parties", {})
    p_name = parties.get("plaintiffs", [{}])[0].get("name", "Plaintiff") if parties.get("plaintiffs") else "Plaintiff"
    d_name = parties.get("defendants", [{}])[0].get("name", "Defendant") if parties.get("defendants") else "Defendant"

    critical_count = sum(1 for e in entries if e.priority == "critical")

    return FilingCalendar(
        case_name=f"{p_name} v. {d_name}",
        filing_date=filing_date,
        district_code=district_code or "active",
        entries=entries,
        total_documents=len(entries),
        critical_deadlines=critical_count,
        estimated_trial_date=str(filing_date + timedelta(days=365)),
        generated_at=str(date.today()),
    )


def format_filing_calendar(calendar: FilingCalendar, fmt: str = "table") -> str:
    """Format filing calendar for CLI output.

    Args:
        calendar: The FilingCalendar to format
        fmt: "table" for compact view, "detailed" for full details
    """
    lines = []

    lines.append("")
    lines.append("=" * 78)
    lines.append("         CASE FILING CALENDAR — COMPLETE DOCUMENT MAP")
    lines.append("=" * 78)
    lines.append(f"  Case:     {calendar.case_name}")
    lines.append(f"  Filed:    {calendar.filing_date}")
    lines.append(f"  District: {calendar.district_code}")
    lines.append(f"  Documents: {calendar.total_documents}")
    lines.append(f"  Critical:  {calendar.critical_deadlines} deadlines")
    lines.append(f"  Est. Trial: {calendar.estimated_trial_date}")

    if fmt == "table":
        lines.append("")
        lines.append(f"  {'Date':<12} {'Days':>5}  {'Pri':>3}  {'Document':<35} {'Rule'}")
        lines.append("  " + "-" * 76)
        for e in calendar.entries:
            pri_icon = {"critical": "!!", "high": ">>", "medium": "..", "low": "  "}.get(e.priority, "  ")
            status_mark = " [OVERDUE]" if e.status == "overdue" else ""
            lines.append(
                f"  {e.deadline!s:<12} {e.relative_days:>5}d [{pri_icon}] {e.document[:35]:<35} {e.rule_authority[:20]}{status_mark}"
            )
    else:
        current_category = ""
        category_labels = {
            "pre_filing": "PRE-FILING DOCUMENTS",
            "pleading": "PLEADINGS",
            "service": "SERVICE OF PROCESS",
            "discovery": "DISCOVERY",
            "dispositive": "DISPOSITIVE MOTIONS",
            "trial": "TRIAL",
            "post_trial": "POST-TRIAL",
        }

        for e in calendar.entries:
            if e.category != current_category:
                current_category = e.category
                lines.append("")
                lines.append(f"  ## {category_labels.get(e.category, e.category.upper())}")
                lines.append("")

            pri_icon = {"critical": "!!", "high": ">>", "medium": "..", "low": "  "}.get(e.priority, "  ")
            lines.append(f"  [{pri_icon}] {e.document}")
            lines.append(f"       Deadline:    {e.deadline} (Day {e.relative_days})")
            lines.append(f"       Description: {e.description}")
            lines.append(f"       Authority:   {e.rule_authority}")
            if e.depends_on:
                lines.append(f"       Depends on:  {e.depends_on}")
            for note in e.notes:
                lines.append(f"       Note: {note}")
            lines.append("")

    lines.append("")
    lines.append("=" * 78)
    lines.append(f"  Generated: {calendar.generated_at}")
    lines.append("  NOTE: Discovery and trial dates are estimates. Actual dates set by scheduling order.")
    lines.append("")

    return "\n".join(lines)

"""
Post-Generation Questions Engine — Context-aware verification and next-step prompts.

After every document generation (analyze, draft, export), this module produces
targeted questions organized into four categories:

1. PRE-FILING VERIFICATION — Did you check jurisdiction, service, formatting?
2. STRATEGIC FOLLOW-UPS — Alternative claims, defenses to anticipate, discovery needs?
3. CLIENT COMMUNICATION — Does the client understand risks, costs, timeline?
4. PROCEDURAL NEXT STEPS — Deadlines, filings, conferences to calendar?

Questions are context-sensitive: they adapt based on claim types, risk scores,
SOL status, jurisdiction basis, and document type being generated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Question:
    category: str  # prefiling | strategic | client | procedural
    priority: str  # critical | high | medium
    text: str
    context: str = ""  # why this question matters


@dataclass
class QuestionSet:
    document_type: str
    generated_at: str
    questions: list[Question] = field(default_factory=list)

    @property
    def critical(self) -> list[Question]:
        return [q for q in self.questions if q.priority == "critical"]

    @property
    def by_category(self) -> dict[str, list[Question]]:
        cats: dict[str, list[Question]] = {}
        for q in self.questions:
            cats.setdefault(q.category, []).append(q)
        return cats


# ── District-aware helper ────────────────────────────────────────────────────

def _get_district_name() -> str:
    """Get active district name for district-aware question text."""
    try:
        from .districts import get_active_district
        return get_active_district().config.name
    except Exception:
        return "M.D. Fla."


# ── Question generators by category ─────────────────────────────────────────

def _prefiling_questions(case_data: dict, doc_type: str, risk_scores: dict | None = None) -> list[Question]:
    """Verification questions before filing any document."""
    qs: list[Question] = []

    # Always ask
    qs.append(Question(
        category="prefiling",
        priority="critical",
        text=f"Has the complaint/motion been reviewed by a licensed attorney admitted to the {_get_district_name()} bar?",
        context="All filings must be signed by a member of the bar (Local Rule 2.01) or the pro se litigant.",
    ))

    qs.append(Question(
        category="prefiling",
        priority="critical",
        text="Have all facts been verified with the client and supporting documents?",
        context="Rule 11 requires reasonable inquiry into factual contentions. Sanctions apply for frivolous filings.",
    ))

    # Jurisdiction-specific
    parties = case_data.get("parties", {})
    plaintiffs = parties.get("plaintiffs", [])
    defendants = parties.get("defendants", [])

    if any(p.get("entity_type") == "corporation" for p in plaintiffs + defendants):
        qs.append(Question(
            category="prefiling",
            priority="high",
            text="Has the Corporate Disclosure Statement (FRCP 7.1) been prepared for all corporate parties?",
            context="Required within first filing by a corporate party. Identifies parent corporations and publicly held entities owning 10%+ stock.",
        ))

    court = case_data.get("court", {})
    if court.get("state") and not case_data.get("case_number"):
        qs.append(Question(
            category="prefiling",
            priority="high",
            text="Has the Civil Cover Sheet (JS-44) been completed?",
            context="Required for all new civil actions filed in federal court.",
        ))

    # Service
    if doc_type in ("complaint", "analyze", "draft"):
        qs.append(Question(
            category="prefiling",
            priority="high",
            text="Has a plan been established for service of process within the 90-day deadline (FRCP 4(m))?",
            context="Failure to serve within 90 days may result in dismissal without prejudice.",
        ))

    # Risk-based
    if risk_scores:
        high_risk = [k for k, v in risk_scores.items() if v.get("score", 0) >= 70]
        if high_risk:
            qs.append(Question(
                category="prefiling",
                priority="critical",
                text=f"Claims {', '.join(high_risk)} scored HIGH MTD risk (70+). Have you strengthened factual allegations for these claims or considered dropping them?",
                context="High-risk claims may invite a successful Rule 12(b)(6) motion and could undermine stronger claims.",
            ))

    # Formatting
    qs.append(Question(
        category="prefiling",
        priority="medium",
        text=f"Does the document comply with {_get_district_name()} Local Rule formatting (Times New Roman 12pt, double-spaced, 1\" margins, page limits)?",
        context="Non-compliant filings may be stricken or returned. Use 'ftc export' for court-formatted .docx output.",
    ))

    return qs


def _strategic_questions(case_data: dict, suggestions: list | None = None, risk_scores: dict | None = None) -> list[Question]:
    """Strategic follow-up questions about case theory and approach."""
    qs: list[Question] = []

    claims = case_data.get("claims_requested", [])

    # Alternative claims
    if suggestions:
        dropped = [s for s in suggestions if s.get("score", 0) >= 60 and s.get("key") not in claims and not s.get("showstoppers")]
        if dropped:
            keys = [s["key"] for s in dropped[:3]]
            qs.append(Question(
                category="strategic",
                priority="high",
                text=f"These viable claims were not included: {', '.join(keys)}. Should any be added as additional or alternative counts?",
                context="Including additional viable claims provides fallback positions if primary claims are dismissed.",
            ))

    # Defense anticipation
    qs.append(Question(
        category="strategic",
        priority="high",
        text="Have you identified and preemptively addressed the top 3 likely defenses in the complaint/motion?",
        context="Proactive pleading that anticipates defenses (qualified immunity, exhaustion, preemption) strengthens the filing.",
    ))

    # Discovery needs
    facts = case_data.get("facts", [])
    facts_with_docs = [f for f in facts if f.get("documents")]
    if len(facts) > 0 and len(facts_with_docs) < len(facts) / 2:
        qs.append(Question(
            category="strategic",
            priority="high",
            text="More than half of the alleged facts lack supporting documents. Has a discovery plan been developed to obtain missing evidence?",
            context="Undocumented factual allegations are vulnerable at summary judgment. Early discovery planning is critical.",
        ))

    # Settlement leverage
    relief = case_data.get("relief_requested", [])
    if "money" in relief:
        qs.append(Question(
            category="strategic",
            priority="medium",
            text="Has an initial settlement demand range been calculated based on damages modeling?",
            context="Early settlement posture informs litigation strategy and budget allocation.",
        ))

    # Injunctive relief urgency
    if "injunction" in relief:
        qs.append(Question(
            category="strategic",
            priority="critical",
            text="If seeking injunctive relief, does the timeline require an emergency TRO motion (FRCP 65(b)) before the standard preliminary injunction?",
            context="TROs can be obtained ex parte with showing of immediate irreparable harm. Standard PI requires noticed hearing.",
        ))

    # Multi-defendant strategy
    defendants = case_data.get("parties", {}).get("defendants", [])
    if len(defendants) > 1:
        qs.append(Question(
            category="strategic",
            priority="medium",
            text=f"With {len(defendants)} defendants, has joint-and-several liability been analyzed? Should any defendants be pursued via crossclaim or third-party complaint?",
            context="Multi-defendant cases require strategic decisions about which defendants to prioritize and how to structure claims.",
        ))

    return qs


def _client_questions(case_data: dict, risk_scores: dict | None = None) -> list[Question]:
    """Client communication and expectation-setting questions."""
    qs: list[Question] = []

    qs.append(Question(
        category="client",
        priority="high",
        text=f"Has the client been informed of the estimated timeline (12-24 months typical for {_get_district_name()}) and litigation costs?",
        context="Client expectations about duration and expense should be set early to avoid dissatisfaction.",
    ))

    qs.append(Question(
        category="client",
        priority="high",
        text="Has the client been advised of the risks of adverse outcomes, including fee-shifting statutes and Rule 11 sanctions?",
        context="Federal fee-shifting (42 U.S.C. 1988, EAJA, etc.) can expose clients to paying opponent's fees in certain claim types.",
    ))

    # Pro se specific
    budget = case_data.get("budget", {})
    if budget.get("type") == "pro_se" or case_data.get("pro_se"):
        qs.append(Question(
            category="client",
            priority="critical",
            text="Has the pro se litigant been informed of the heightened procedural requirements in federal court (CM/ECF, local rules, FRCP deadlines)?",
            context="Pro se litigants are held to the same procedural rules as attorneys. Missing deadlines can be fatal.",
        ))
        qs.append(Question(
            category="client",
            priority="high",
            text=f"Has the pro se litigant been directed to the {_get_district_name()} Pro Se Handbook and Legal Aid resources?",
            context="The court provides a Pro Se Handbook with essential filing instructions.",
        ))

    # Preservation
    qs.append(Question(
        category="client",
        priority="critical",
        text="Has the client been instructed to preserve all relevant documents, emails, text messages, and electronic data?",
        context="Spoliation of evidence can lead to adverse inference instructions and Rule 37(e) sanctions.",
    ))

    # Counterclaim risk
    claims = case_data.get("claims_requested", [])
    if claims:
        qs.append(Question(
            category="client",
            priority="medium",
            text="Has the client been warned about potential counterclaims from the defendant?",
            context="Filing a lawsuit opens the door to compulsory counterclaims (FRCP 13(a)) that may expose the client to liability.",
        ))

    return qs


def _procedural_questions(case_data: dict, sol_results: list | None = None) -> list[Question]:
    """Procedural next steps and deadline questions."""
    qs: list[Question] = []

    # SOL urgency
    if sol_results:
        urgent = [r for r in sol_results if r.get("status") == "urgent"]
        expired = [r for r in sol_results if r.get("status") == "expired"]

        if expired:
            keys = [r.get("claim_key", "unknown") for r in expired]
            qs.append(Question(
                category="procedural",
                priority="critical",
                text=f"EXPIRED SOL on claims: {', '.join(keys)}. Have tolling doctrines (discovery rule, equitable tolling, fraudulent concealment) been analyzed?",
                context="Expired claims must be dropped unless a tolling doctrine applies. Filing expired claims risks Rule 11 sanctions.",
            ))

        if urgent:
            keys = [r.get("claim_key", "unknown") for r in urgent]
            days = [str(r.get("days_remaining", "?")) for r in urgent]
            qs.append(Question(
                category="procedural",
                priority="critical",
                text=f"URGENT SOL: {', '.join(f'{k} ({d}d)' for k, d in zip(keys, days))}. Is the filing timeline expedited to beat these deadlines?",
                context="Claims approaching SOL deadline require immediate filing. Consider filing with leave to amend if investigation is incomplete.",
            ))

    # Key deadlines
    case_status = case_data.get("case_status")

    if case_status in (None, "pre-filing", "new"):
        qs.append(Question(
            category="procedural",
            priority="high",
            text="After filing, have you calendared: (1) 90-day service deadline, (2) Corporate Disclosure Statement, (3) Rule 26(f) conference?",
            context="These are the first three critical deadlines after filing a federal complaint.",
        ))

    if case_status == "recently_filed":
        qs.append(Question(
            category="procedural",
            priority="critical",
            text="Is the 21-day answer deadline calendared? If filing a Rule 12 motion, remember it tolls the answer deadline (FRCP 12(a)(4)).",
            context="Missing the answer deadline can result in default judgment under FRCP 55.",
        ))

    if case_status in ("discovery", "active"):
        qs.append(Question(
            category="procedural",
            priority="high",
            text="Are all scheduling order deadlines calendared (discovery cutoff, expert disclosures, dispositive motions)?",
            context="Failure to meet scheduling order deadlines requires a showing of good cause to modify (FRCP 16(b)(4)).",
        ))

    # Meet and confer
    qs.append(Question(
        category="procedural",
        priority="medium",
        text=f"If filing any discovery motion, has the meet-and-confer requirement been satisfied ({_get_district_name()} Local Rules)?",
        context="Discovery motions filed without certification of good-faith conferral will be denied.",
    ))

    # Export reminder
    qs.append(Question(
        category="procedural",
        priority="medium",
        text="Has the final document been exported to .docx format for CM/ECF filing? Use: ftc export --draft -i case.json -o complaint.docx",
        context="CM/ECF requires PDF upload. Export to .docx first, then convert to PDF in Word/Google Docs.",
    ))

    return qs


# ── Main API ─────────────────────────────────────────────────────────────────

def generate_questions(
    case_data: dict,
    doc_type: str = "analyze",
    suggestions: list[dict] | None = None,
    risk_scores: dict | None = None,
    sol_results: list[dict] | None = None,
) -> QuestionSet:
    """Generate context-aware post-generation questions.

    Args:
        case_data: The case JSON data
        doc_type: Type of document generated (analyze, draft, export, suggest, risk)
        suggestions: Claim suggestions with keys and scores (from suggest_claims)
        risk_scores: Dict of claim_key -> {score, level} (from calculate_mtd_risk)
        sol_results: List of SOL results with status and days_remaining

    Returns:
        QuestionSet with categorized, prioritized questions
    """
    all_questions: list[Question] = []

    # Always include pre-filing verification
    all_questions.extend(_prefiling_questions(case_data, doc_type, risk_scores))

    # Strategic questions for analysis and drafting
    if doc_type in ("analyze", "draft", "suggest"):
        all_questions.extend(_strategic_questions(case_data, suggestions, risk_scores))

    # Client communication questions
    all_questions.extend(_client_questions(case_data, risk_scores))

    # Procedural questions
    all_questions.extend(_procedural_questions(case_data, sol_results))

    # Sort: critical first, then high, then medium
    priority_order = {"critical": 0, "high": 1, "medium": 2}
    all_questions.sort(key=lambda q: priority_order.get(q.priority, 99))

    return QuestionSet(
        document_type=doc_type,
        generated_at=str(date.today()),
        questions=all_questions,
    )


def format_questions(qs: QuestionSet, verbose: bool = False) -> str:
    """Format questions for CLI output."""
    lines: list[str] = []

    lines.append("")
    lines.append("=" * 70)
    lines.append("         POST-GENERATION VERIFICATION QUESTIONS")
    lines.append("=" * 70)

    critical_count = len(qs.critical)
    total = len(qs.questions)
    lines.append(f"  {total} questions ({critical_count} CRITICAL)")
    lines.append("")

    category_labels = {
        "prefiling": "PRE-FILING VERIFICATION",
        "strategic": "STRATEGIC FOLLOW-UPS",
        "client": "CLIENT COMMUNICATION",
        "procedural": "PROCEDURAL NEXT STEPS",
    }

    priority_icons = {
        "critical": "!!",
        "high": ">>",
        "medium": "..",
    }

    for cat in ("prefiling", "strategic", "client", "procedural"):
        cat_qs = qs.by_category.get(cat, [])
        if not cat_qs:
            continue

        lines.append(f"  ## {category_labels.get(cat, cat.upper())}")
        lines.append("")

        for i, q in enumerate(cat_qs, 1):
            icon = priority_icons.get(q.priority, "  ")
            lines.append(f"   [{icon}] {i}. {q.text}")
            if verbose and q.context:
                lines.append(f"        -> {q.context}")
            lines.append("")

    lines.append("=" * 70)
    lines.append("  TIP: Run with -q/--questions --verbose for full context on each question")
    lines.append("")

    return "\n".join(lines)

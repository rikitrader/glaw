"""Shared GLAW workflow profile definitions.

This is the single source of truth for council and adversarial review coverage.
Keep it dependency-free so every CLI can import it in a source-only install.
"""
from __future__ import annotations


COUNCIL_PROFILES: dict[str, tuple[str, ...]] = {
    "accounting": (
        "cfo",
        "irs-audit-agent",
        "legal-counsel",
        "forensic-audit",
        "outside-critic",
        "external-reviewer",
    ),
    "accounting-tax": (
        "cfo",
        "tax-strategist",
        "irs-audit-agent",
        "legal-counsel",
        "forensic-audit",
        "accounting-reviewer",
        "outside-critic",
        "external-reviewer",
    ),
    "tax": (
        "tax-strategist",
        "irs-audit-agent",
        "legal-counsel",
        "accounting-reviewer",
        "outside-critic",
        "external-reviewer",
    ),
    "litigation": (
        "lead-counsel",
        "opposing-counsel-critic",
        "evidence-reviewer",
        "legal-research",
        "outside-critic",
    ),
    "corp-build": (
        "corporate-counsel",
        "tax-counsel",
        "securities-counsel",
        "accounting-reviewer",
        "outside-critic",
    ),
    "contract-review": (
        "contract-counsel",
        "business-reviewer",
        "risk-reviewer",
        "legal-research",
        "outside-critic",
    ),
    "investigation": (
        "case-commander",
        "forensic-investigator",
        "legal-counsel",
        "evidence-reviewer",
        "outside-critic",
    ),
    "sec-reporting": (
        "sec-counsel",
        "accounting-reviewer",
        "disclosure-reviewer",
        "audit-reviewer",
        "outside-critic",
    ),
    "hybrid": (
        "chief-counsel",
        "accounting-reviewer",
        "tax-reviewer",
        "legal-counsel",
        "outside-critic",
    ),
}


ADVERSARIAL_PROFILES: dict[str, tuple[str, ...]] = {
    "accounting": (
        "irs-examiner",
        "state-tax-auditor",
        "forensic-accountant",
        "cfo-controller",
        "outside-critic",
    ),
    "accounting-tax": (
        "irs-examiner",
        "state-tax-auditor",
        "tax-court-counsel",
        "penalty-reviewer",
        "forensic-accountant",
        "cfo-controller",
        "outside-critic",
    ),
    "tax": (
        "irs-examiner",
        "state-tax-auditor",
        "tax-court-counsel",
        "penalty-reviewer",
        "outside-critic",
    ),
    "litigation": (
        "opposing-counsel",
        "federal-defense-counsel",
        "evidence-adversary",
        "skeptical-judge",
        "outside-critic",
    ),
    "corp-build": (
        "irs-examiner",
        "sec-reviewer",
        "creditor-trustee",
        "corporate-separateness-reviewer",
        "outside-critic",
    ),
    "contract-review": (
        "opposing-counsel",
        "commercial-counterparty",
        "regulator-reviewer",
        "litigation-counsel",
        "outside-critic",
    ),
    "investigation": (
        "doj-ausa-prosecutor",
        "fincen-aml-reviewer",
        "sec-enforcement-reviewer",
        "irs-ci-reviewer",
        "defense-counsel",
        "outside-critic",
    ),
    "sec-reporting": (
        "sec-staff-reviewer",
        "pcaob-audit-reviewer",
        "disclosure-counsel",
        "irs-examiner",
        "outside-critic",
    ),
    "hybrid": (
        "opposing-counsel",
        "irs-examiner",
        "sec-reviewer",
        "creditor-trustee",
        "outside-critic",
    ),
}


TRACK_TO_PROFILE = {
    "accounting-tax": "accounting-tax",
    "tax": "tax",
    "litigation": "litigation",
    "corp-build": "corp-build",
    "contract-review": "contract-review",
    "investigation": "investigation",
    "sec-reporting": "sec-reporting",
    "hybrid": "hybrid",
}


TRACKS: dict[str, tuple[str, ...]] = {
    "litigation": ("claims_or_defenses", "forum", "relief_requested", "evidence_sources"),
    "corp-build": ("entity_type", "owners", "capitalization", "tax_elections", "filings_needed"),
    "investigation": ("targets", "suspected_conduct", "evidence_sources", "reporting_path"),
    "hybrid": ("tracks_in_scope", "sequencing", "shared_evidence_sources"),
    "accounting-tax": (
        "bank_statement_sources",
        "tax_years",
        "entity_tax_type",
        "books_status",
        "irs_forms_needed",
    ),
    "tax": (
        "tax_years",
        "taxpayer_type",
        "tax_forms_needed",
        "source_records",
        "positions_or_issues",
        "filing_or_exam_deadlines",
    ),
    "contract-review": ("contract_type", "counterparty", "governing_law", "review_standard"),
    "sec-reporting": (
        "filer_status",
        "period_end",
        "forms_needed",
        "audited_financial_sources",
        "xbrl_scope",
    ),
}


REVIEWER_SKILL_MAP: dict[str, str] = {
    "accounting-reviewer": "glaw-accounting",
    "audit-reviewer": "glaw-audit",
    "business-reviewer": "glaw-commercial-contracts",
    "case-commander": "glaw-command",
    "cfo": "glaw-cfo",
    "cfo-controller": "glaw-controller",
    "chief-counsel": "glaw-chief-counsel",
    "commercial-counterparty": "glaw-commercial-contracts",
    "contract-counsel": "glaw-contract-review",
    "corporate-counsel": "glaw-corporate-counsel",
    "corporate-separateness-reviewer": "glaw-veil-piercing",
    "creditor-trustee": "glaw-restructuring",
    "defense-counsel": "glaw-federal-trial-counsel",
    "disclosure-counsel": "glaw-sec-disclosure",
    "disclosure-reviewer": "glaw-disclosure-risk-analyzer",
    "doj-ausa-prosecutor": "glaw-bureau-prosecutor",
    "evidence-adversary": "glaw-evidence-timeline",
    "evidence-reviewer": "glaw-evidence-timeline",
    "external-reviewer": "glaw-consensus",
    "federal-defense-counsel": "glaw-federal-trial-counsel",
    "fincen-aml-reviewer": "glaw-fincen-aml",
    "forensic-accountant": "glaw-forensic-reconstruction",
    "forensic-audit": "glaw-audit",
    "forensic-investigator": "glaw-forensic-case-investigator",
    "irs-audit-agent": "glaw-irs-audit",
    "irs-ci-reviewer": "glaw-bureau-counterfraud",
    "irs-examiner": "glaw-irs-audit",
    "lead-counsel": "glaw-federal-trial-counsel",
    "legal-counsel": "glaw-legal-research",
    "legal-research": "glaw-legal-research",
    "litigation-counsel": "glaw-federal-trial-counsel",
    "opposing-counsel": "glaw-adversarial",
    "opposing-counsel-critic": "glaw-adversarial",
    "outside-critic": "glaw-consensus",
    "pcaob-audit-reviewer": "glaw-audit-assurance",
    "penalty-reviewer": "glaw-back-taxes",
    "regulator-reviewer": "glaw-regulatory-aml",
    "risk-reviewer": "glaw-disclosure-risk-analyzer",
    "sec-counsel": "glaw-sec",
    "sec-enforcement-reviewer": "glaw-sec-enforcement",
    "sec-reviewer": "glaw-sec",
    "sec-staff-reviewer": "glaw-sec-reporting",
    "securities-counsel": "glaw-sec",
    "skeptical-judge": "glaw-adversarial",
    "state-tax-auditor": "glaw-sales-tax",
    "tax-counsel": "glaw-tax-strategy",
    "tax-court-counsel": "glaw-tax-court",
    "tax-reviewer": "glaw-tax-provision",
    "tax-strategist": "glaw-tax-strategy",
}


def profile_for_track(track: str | None) -> str:
    if not track:
        return "hybrid"
    return TRACK_TO_PROFILE.get(track, track if track in COUNCIL_PROFILES else "hybrid")

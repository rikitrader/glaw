"""
MTD Risk Scoring Engine - Local execution.
Calculates motion-to-dismiss vulnerability scores.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from .claims import get_claim, CLAIM_LIBRARY


@dataclass
class RiskFactor:
    category: str
    score: int  # 0-100
    weight: int
    issue: str
    fix: str


@dataclass
class MTDRiskResult:
    overall_score: int
    risk_level: str  # low/medium/high/critical
    factors: list[RiskFactor]
    top_vulnerabilities: list[str]
    prioritized_fixes: list[str]


RISK_WEIGHTS = {
    "standing": 15,
    "immunity": 20,
    "exhaustion": 15,
    "sol": 15,
    "rule_9b": 10,
    "monell": 10,
    "damages": 5,
    "plausibility": 20,
}


def calculate_mtd_risk(case_data: dict, claim_key: str) -> MTDRiskResult:
    """Calculate comprehensive MTD risk score for a claim."""
    factors: list[RiskFactor] = []
    meta = get_claim(claim_key)
    if not meta:
        return MTDRiskResult(50, "medium", [], [f"Unknown claim: {claim_key}"], [])

    facts = case_data.get("facts", [])
    parties = case_data.get("parties", {})
    exhaustion = case_data.get("exhaustion", {})
    limitations = case_data.get("limitations", {})
    relief = case_data.get("relief_requested", [])

    # 1. Standing
    factors.append(_assess_standing(facts, parties, relief))

    # 2. Immunity
    factors.append(_assess_immunity(meta, parties))

    # 3. Exhaustion
    factors.append(_assess_exhaustion(meta, exhaustion))

    # 4. Statute of Limitations
    factors.append(_assess_sol(meta, limitations))

    # 5. Rule 9(b) if applicable
    if meta.heightened_pleading:
        factors.append(_assess_rule_9b(facts))

    # 6. Monell (always appended; returns N/A factor when no municipal defendant)
    factors.append(_assess_monell(claim_key, facts, parties))

    # 7. Damages
    factors.append(_assess_damages(facts))

    # 8. Plausibility (based on fact count and detail)
    factors.append(_assess_plausibility(facts, claim_key))

    # Calculate overall
    total_weighted = sum(f.score * f.weight for f in factors)
    total_weight = sum(f.weight for f in factors)
    overall = round(total_weighted / total_weight) if total_weight else 50

    risk_level = "low" if overall < 25 else "medium" if overall < 50 else "high" if overall < 75 else "critical"

    top_vulns = [f.issue for f in sorted(factors, key=lambda x: -x.score) if f.score > 50][:5]
    fixes = [f.fix for f in sorted(factors, key=lambda x: -(x.score * x.weight)) if f.score > 30][:5]

    return MTDRiskResult(overall, risk_level, factors, top_vulns, fixes)


def _names_overlap(a: str, b: str) -> bool:
    """Check if all words of the shorter name appear in the longer name."""
    a_words = set(a.split())
    b_words = set(b.split())
    shorter, longer = (a_words, b_words) if len(a_words) <= len(b_words) else (b_words, a_words)
    return bool(shorter) and shorter.issubset(longer)


def _assess_standing(facts: list, parties: dict, relief: list) -> RiskFactor:
    score = 0
    issues = []
    has_injury = any(f.get("harm") for f in facts)
    if not has_injury:
        score += 40
        issues.append("No injury alleged")
    if not relief:
        score += 20
        issues.append("No relief requested")
    defendants = parties.get("defendants", [])
    defendant_names = {d.get("name", "").lower() for d in defendants} - {""}
    has_link = any(
        any(_names_overlap(a.lower(), dn) for dn in defendant_names for a in f.get("actors", []))
        for f in facts
    ) if defendant_names else False
    if not has_link:
        score += 30
        issues.append("Defendant not linked to harm")
    return RiskFactor("standing", min(100, score), RISK_WEIGHTS["standing"],
                      "; ".join(issues) or "Standing appears adequate",
                      "Strengthen injury/causation/redressability allegations" if score > 50 else "OK")


_IMMUNITY_SCORES = {
    "qualified": (60, "Qualified immunity likely"),
    "sovereign": (50, "Sovereign immunity risk"),
    "eleventh_amendment": (70, "Eleventh Amendment bars damages"),
}


def _assess_immunity(meta, parties: dict) -> RiskFactor:
    from .immunity_checks import triggered_immunities

    triggered = triggered_immunities(meta, parties.get("defendants", []))
    score = 0
    issues: list[str] = []
    for name in triggered:
        pts, msg = _IMMUNITY_SCORES[name]
        score += pts
        issues.append(msg)
    return RiskFactor("immunity", min(100, score), RISK_WEIGHTS["immunity"],
                      "; ".join(issues) or "No immunity concerns",
                      "Argue clearly established right; identify waivers" if score > 50 else "OK")


def _assess_exhaustion(meta, exhaustion: dict) -> RiskFactor:
    if not meta.exhaustion_required:
        return RiskFactor("exhaustion", 0, RISK_WEIGHTS["exhaustion"], "No exhaustion required", "N/A")
    score = 0
    issue = ""
    etype = meta.exhaustion_type or ""
    if "eeoc" in etype:
        val = exhaustion.get("eeoc_charge_filed")
        if val is False:
            score, issue = 95, "EEOC charge NOT filed"
        elif val is None or val == "unknown":
            score, issue = 50, "EEOC status unknown"
    elif "ftca" in etype:
        val = exhaustion.get("ftca_admin_claim_filed")
        if val is False:
            score, issue = 95, "SF-95 NOT filed"
        elif val is None or val == "unknown":
            score, issue = 50, "FTCA exhaustion unknown"
    elif "erisa" in etype:
        val = exhaustion.get("erisa_appeal_done")
        if val is False:
            score, issue = 80, "ERISA internal appeal not completed"
    elif "apa" in etype:
        val = exhaustion.get("agency_final_action")
        if val is False:
            score, issue = 90, "No final agency action"
    elif "plra" in etype:
        val = exhaustion.get("plra_exhaustion_done")
        if val is False:
            score, issue = 95, "PLRA exhaustion NOT completed"
        elif val is None or val == "unknown":
            score, issue = 50, "PLRA exhaustion status unknown"
    elif "administrative" in etype:
        val = exhaustion.get("administrative_exhaustion_done")
        if val is False:
            score, issue = 80, "Administrative exhaustion not completed"
        elif val is None or val == "unknown":
            score, issue = 40, "Administrative exhaustion unknown"
    elif "irs" in etype:
        val = exhaustion.get("irs_claim_filed")
        if val is False:
            score, issue = 95, "IRS admin claim NOT filed"
        elif val is None or val == "unknown":
            score, issue = 50, "IRS claim status unknown"
    else:
        score, issue = 40, f"Unrecognized exhaustion type: {etype}"
    return RiskFactor("exhaustion", score, RISK_WEIGHTS["exhaustion"],
                      issue or "Exhaustion satisfied", "File admin prerequisites" if score > 50 else "OK")


def _assess_sol(meta, limitations: dict) -> RiskFactor:
    key_dates = limitations.get("key_dates", {})
    injury_date_str = key_dates.get("injury_date")
    if not injury_date_str:
        return RiskFactor("sol", 30, RISK_WEIGHTS["sol"], "Injury date not specified", "Provide injury date")
    try:
        injury = datetime.strptime(injury_date_str, "%Y-%m-%d").date()
    except ValueError:
        return RiskFactor("sol", 30, RISK_WEIGHTS["sol"], "Invalid injury date format", "Use YYYY-MM-DD")
    days = (date.today() - injury).days
    years = days / 365.25
    sol_text = meta.statute_of_limitations.lower()
    # Handle "analogous" or "varies" SOL - flag for manual verification
    if ('analogous' in sol_text or 'varies' in sol_text) and not re.search(r'\b\d+\s*(?:year|month|day)', sol_text):
        return RiskFactor("sol", 30, RISK_WEIGHTS["sol"],
                          f"SOL varies ({meta.statute_of_limitations})",
                          "Verify applicable SOL based on state law or plan terms")
    sol_years = 4.0
    if re.search(r'\b90\s*day', sol_text):
        sol_years = 0.25
    elif re.search(r'\b9\s*month', sol_text):
        sol_years = 0.75
    else:
        for n in [1, 2, 3, 4, 6]:
            if re.search(rf'\b{n}[\s-]*years?\b', sol_text):
                sol_years = float(n)
                break
    if years > sol_years:
        return RiskFactor("sol", 95, RISK_WEIGHTS["sol"],
                          f"SOL likely expired ({meta.statute_of_limitations})",
                          "Investigate tolling doctrines")
    if years > sol_years * 0.8:
        return RiskFactor("sol", 40, RISK_WEIGHTS["sol"],
                          f"SOL expires soon ({meta.statute_of_limitations})", "File immediately")
    return RiskFactor("sol", 0, RISK_WEIGHTS["sol"], f"Within SOL ({meta.statute_of_limitations})", "OK")


def _assess_rule_9b(facts: list) -> RiskFactor:
    score = 0
    for f in facts:
        if not f.get("date"):
            score += 15
        if not f.get("location"):
            score += 10
        if not f.get("actors"):
            score += 20
    return RiskFactor("rule_9b", min(100, score), RISK_WEIGHTS["rule_9b"],
                      "Rule 9(b) particularity concerns" if score > 30 else "OK",
                      "Add who/what/when/where/how specifics" if score > 30 else "OK")


def _assess_monell(claim_key: str, facts: list, parties: dict) -> RiskFactor:
    has_municipal = any(d.get("type") == "local" for d in parties.get("defendants", []))
    monell_relevant = "monell" in claim_key or has_municipal
    if not monell_relevant:
        return RiskFactor("monell", 0, RISK_WEIGHTS["monell"],
                          "Not applicable (no municipal defendant)", "N/A")
    facts_text = " ".join(f.get("event", "") for f in facts).lower()
    score = 0
    if not any(kw in facts_text for kw in ["policy", "custom", "training", "pattern"]):
        score += 50
    if not any(kw in facts_text for kw in ["pattern", "multiple", "repeated", "prior"]):
        score += 30
    return RiskFactor("monell", min(100, score), RISK_WEIGHTS["monell"],
                      "Monell policy/custom allegations weak" if score > 30 else "Monell OK",
                      "Allege specific policy, custom, or failure to train" if score > 30 else "OK")


def _assess_damages(facts: list) -> RiskFactor:
    score = 0
    if not any(f.get("harm") for f in facts):
        score += 40
    if not any(f.get("damages_estimate") for f in facts):
        score += 20
    if not any(f.get("documents") for f in facts):
        score += 15
    return RiskFactor("damages", min(100, score), RISK_WEIGHTS["damages"],
                      "Damages allegations weak" if score > 30 else "Damages OK",
                      "Add specific damages and documentation" if score > 30 else "OK")


def _assess_plausibility(facts: list, claim_key: str) -> RiskFactor:
    # Simple heuristic: more detailed facts = lower risk
    detail_score = 0
    for f in facts:
        if f.get("event"):
            detail_score += 10
        if f.get("date"):
            detail_score += 5
        if f.get("actors"):
            detail_score += 5
        if f.get("documents"):
            detail_score += 5
        if f.get("harm"):
            detail_score += 5
    plausibility = min(100, detail_score)
    risk = 100 - plausibility
    return RiskFactor("plausibility", risk, RISK_WEIGHTS["plausibility"],
                      f"{plausibility}% plausibility from fact detail",
                      "Develop additional factual allegations" if risk > 50 else "OK")

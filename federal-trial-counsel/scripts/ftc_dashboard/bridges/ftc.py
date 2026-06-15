"""In-process bridge to ftc_engine.

Keeps all calls synchronous Python (no subprocess overhead). Each function
accepts a plain dict and returns a JSON-serializable dict/list so the HTTP
layer stays dumb.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ftc_engine.suggest import suggest_claims
from ftc_engine.risk import calculate_mtd_risk
from ftc_engine.sol import calculate_sol, calculate_all_sol
from ftc_engine.drafter import analyze_jurisdiction, generate_complaint
from ftc_engine.claims import CLAIM_LIBRARY, get_claim, list_categories
from ftc_engine.districts import list_districts, get_active_district
from ftc_engine.case_manager import list_cases
from ftc_engine.filing_calendar import generate_filing_calendar, format_filing_calendar
from ftc_engine.rule11_monitor import generate_monitor_report, format_monitor_report
from ftc_engine.deposition import generate_deposition_outline, format_deposition_outline
from ftc_engine.exhibits import generate_exhibit_index, format_exhibit_index
from ftc_engine.pacer_meta import generate_filing_package, format_filing_package


def _to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses / lists / tuples to plain data."""
    if is_dataclass(obj):
        return {k: _to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_dict(x) for x in obj]
    # dates, sets, etc. — str-fallback at the JSON layer
    return obj


# ── Claims library ─────────────────────────────────────────────────────────

def _claim_summary(key: str, meta) -> dict:
    return {
        "key": key,
        "name": meta.name,
        "category": meta.category,
        "source": getattr(meta, "source", ""),
        "jurisdiction": getattr(meta, "jurisdiction", ""),
        "statute_of_limitations": meta.statute_of_limitations,
        "heightened_pleading": meta.heightened_pleading,
        "exhaustion_required": meta.exhaustion_required,
        "exhaustion_type": meta.exhaustion_type,
        "immunities": list(meta.immunities or []),
        "viability_warning": getattr(meta, "viability_warning", ""),
    }


def list_claims() -> dict:
    """Flat list of every claim with category, source, SOL, immunity flags."""
    out = [_claim_summary(k, m) for k, m in CLAIM_LIBRARY.items()]
    out.sort(key=lambda c: (c["category"], c["key"]))
    return {"total": len(out), "categories": list_categories(), "claims": out}


def get_claim_detail(key: str) -> dict:
    meta = get_claim(key)
    if not meta:
        return {"error": f"Unknown claim: {key}"}
    base = _claim_summary(key, meta)
    base["typical_defenses"] = list(getattr(meta, "typical_defenses", []) or [])
    return base


# ── Jurisdictional analysis ────────────────────────────────────────────────

def jurisdiction(case: dict) -> dict:
    return _to_dict(analyze_jurisdiction(case))


# ── Claim suggestion ───────────────────────────────────────────────────────

def suggest(case: dict) -> dict:
    suggestions = suggest_claims(case)
    return {"count": len(suggestions), "suggestions": _to_dict(suggestions)}


# ── MTD risk scoring ───────────────────────────────────────────────────────

def risk(case: dict, claim_keys: list[str]) -> dict:
    out = []
    for ck in claim_keys:
        try:
            out.append(_to_dict(calculate_mtd_risk(case, ck)))
        except Exception as e:
            out.append({"claim_key": ck, "error": str(e)})
    return {"scores": out}


# ── Statute of limitations ─────────────────────────────────────────────────

def sol(claim_keys: list[str], injury_date: str, district: str | None = None) -> dict:
    out = []
    for ck in claim_keys:
        try:
            result = calculate_sol(ck, injury_date, district)
            d = _to_dict(result)
            # date objects aren't JSON-serializable — stringify
            if "deadline" in d and d["deadline"] is not None:
                d["deadline"] = str(d["deadline"])
            if "injury_date" in d and d["injury_date"] is not None:
                d["injury_date"] = str(d["injury_date"])
            out.append(d)
        except Exception as e:
            out.append({"claim_key": ck, "error": str(e)})
    return {"results": out}


# ── Complaint draft ────────────────────────────────────────────────────────

def draft(case: dict) -> dict:
    return {"complaint": generate_complaint(case)}


# ── Filing calendar ────────────────────────────────────────────────────────

def calendar(case: dict, filing_date: str | None = None, district: str | None = None) -> dict:
    cal = generate_filing_calendar(case, filing_date_str=filing_date, district_code=district)
    d = _to_dict(cal)
    # Flatten CalendarEntry date fields
    for entry in d.get("entries", []):
        if "deadline" in entry and entry["deadline"] is not None:
            entry["deadline"] = str(entry["deadline"])
    if "filing_date" in d and d["filing_date"] is not None:
        d["filing_date"] = str(d["filing_date"])
    if "estimated_trial_date" in d and d["estimated_trial_date"] is not None:
        d["estimated_trial_date"] = str(d["estimated_trial_date"])
    return {"calendar": d, "formatted": format_filing_calendar(cal)}


# ── Rule 11 viability monitor ──────────────────────────────────────────────

def monitor(case: dict, claim_keys: list[str] | None = None, mode: str = "offline") -> dict:
    report = generate_monitor_report(case, claim_keys=claim_keys, mode=mode)
    return {"report": _to_dict(report), "formatted": format_monitor_report(report)}


# ── Deposition outlines ────────────────────────────────────────────────────

def deposition(case: dict, witness: str, exam_type: str = "cross",
               claim_keys: list[str] | None = None, max_questions: int = 50) -> dict:
    outline = generate_deposition_outline(
        case, witness_name=witness, exam_type=exam_type,
        claim_keys=claim_keys, max_questions=max_questions,
    )
    return {"outline": _to_dict(outline), "formatted": format_deposition_outline(outline)}


# ── Exhibit index ──────────────────────────────────────────────────────────

def exhibits(case: dict, scan_directory: str | None = None, numbering: str = "alpha",
             prefix: str = "") -> dict:
    index = generate_exhibit_index(case, scan_directory=scan_directory,
                                   numbering=numbering, prefix=prefix or "")
    return {"index": _to_dict(index), "formatted": format_exhibit_index(index)}


# ── PACER / ECF filing package ─────────────────────────────────────────────

def pacer(case: dict) -> dict:
    pkg = generate_filing_package(case)
    return {"package": _to_dict(pkg), "formatted": format_filing_package(pkg)}


# ── Cases & districts ──────────────────────────────────────────────────────

def cases() -> dict:
    return {"cases": list_cases()}


def districts() -> dict:
    try:
        active = get_active_district()
        active_code = active.config.code
    except Exception:
        active_code = None
    return {
        "districts": [_to_dict(d) for d in list_districts()],
        "active": active_code,
    }

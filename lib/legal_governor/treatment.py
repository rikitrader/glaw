"""Holding, precedent-treatment, and temporal validity gates."""
from __future__ import annotations


HOLDING_TYPES = {"HOLDING", "DICTA", "PROCEDURAL_HISTORY", "PARTY_ARGUMENT", "DISSENT", "CONCURRENCE", "LOWER_COURT_DESCRIPTION"}
TREATMENTS = {"GOOD_LAW", "LIMITED", "DISTINGUISHED", "CRITICIZED", "OVERRULED", "SUPERSEDED", "ABROGATED", "UNKNOWN"}


def validate_holdings(rows: list[dict]) -> list[str]:
    failures = []
    for row in rows or []:
        if row.get("classification") not in HOLDING_TYPES:
            failures.append(f"holding {row.get('id', '?')} classification is invalid")
        if row.get("material", True) and row.get("classification") != "HOLDING":
            failures.append(f"material authority passage {row.get('id', '?')} is not classified as holding")
    return failures


def validate_treatment(rows: list[dict]) -> list[str]:
    failures = []
    for row in rows or []:
        if row.get("status") not in TREATMENTS:
            failures.append(f"precedent {row.get('source_id', '?')} treatment is unknown")
        if row.get("material", True) and row.get("status") in {"OVERRULED", "SUPERSEDED", "ABROGATED", "UNKNOWN"}:
            failures.append(f"material precedent {row.get('source_id', '?')} is not current good law")
    return failures


def validate_temporal(rows: list[dict], relevant_date: str | None) -> list[str]:
    failures = []
    if not relevant_date:
        return ["legally relevant date is missing"]
    for row in rows or []:
        if row.get("status") != "VALID":
            failures.append(f"temporal validity is not verified for {row.get('source_id', '?')}")
    return failures


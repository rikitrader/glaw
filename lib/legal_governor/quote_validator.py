"""Exact quote validation against immutable source text."""
from __future__ import annotations

import re


def _normalize(value: str) -> str:
    value = value.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    value = re.sub(r"[\u00ad\u2010-\u2015-]", "-", value)
    return re.sub(r"\s+", " ", value).strip()


def validate(quote: str, source_text: str) -> str:
    if quote in source_text:
        return "EXACT"
    if _normalize(quote) in _normalize(source_text):
        return "NORMALIZED_MATCH"
    return "NO_MATCH"


def validate_records(records: list[dict], sources: dict[str, dict]) -> list[str]:
    failures = []
    for row in records or []:
        status = validate(str(row.get("quote", "")), str(sources.get(str(row.get("source_id")), {}).get("text", "")))
        if row.get("material", True) and status == "NO_MATCH":
            failures.append(f"material quote {row.get('id', '?')} has no source match")
    return failures


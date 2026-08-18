"""Premise extraction and fail-closed premise states."""
from __future__ import annotations

import re


STATES = {"VERIFIED", "PARTIALLY_VERIFIED", "FALSE", "UNRESOLVED"}


def extract(question: str) -> list[dict]:
    if not str(question).strip():
        return [{"id": "P001", "text": "question is missing", "status": "UNRESOLVED", "material": True}]
    candidates = []
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+", question.strip()), start=1):
        if re.search(r"\b(because|guarantee|guarantees|always|never|automatically|must|cannot|clearly)\b", sentence, re.I):
            candidates.append({"id": f"P{index:03d}", "text": sentence, "status": "UNRESOLVED", "material": True})
    return candidates


def validate(rows: list[dict]) -> list[str]:
    failures = []
    for row in rows or []:
        if row.get("status") not in STATES:
            failures.append(f"premise {row.get('id', '?')} has unresolved state")
        if row.get("material") and row.get("status") not in {"VERIFIED", "PARTIALLY_VERIFIED"}:
            failures.append(f"material premise {row.get('id', '?')} is not verified or corrected")
    return failures


"""Evidence-derived confidence vector; not a model self-reported probability."""
from __future__ import annotations


FIELDS = ("retrievalCompleteness", "sourceReliability", "authorityStrength", "jurisdictionMatch", "entailment", "temporalValidity", "precedentValidity", "independentAgreement", "adversarialSurvival", "citationIntegrity")


def vector(record: dict) -> dict:
    return {field: record.get(field, "UNKNOWN") for field in FIELDS}


def pass_threshold(v: dict) -> tuple[bool, list[str]]:
    failures = []
    for field in FIELDS:
        value = v.get(field)
        if isinstance(value, (int, float)) and value < 0.95:
            failures.append(f"{field} below calibrated threshold")
        elif value in {None, "UNKNOWN", "INCOMPLETE", "UNVERIFIED", "FAIL"}:
            failures.append(f"{field} is not verified")
    return not failures, failures


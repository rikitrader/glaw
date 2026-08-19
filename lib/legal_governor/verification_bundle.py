"""Composite verification bundle used by the deterministic Governor."""
from __future__ import annotations

from legal_governor.claim_graph import validate_claims
from legal_governor.confidence import pass_threshold
from legal_governor.premise import validate as validate_premises
from legal_governor.quote_validator import validate_records as validate_quotes
from legal_governor.treatment import validate_holdings, validate_temporal, validate_treatment


def validate(bundle: dict, source_map: dict[str, dict]) -> list[str]:
    failures = []
    if not isinstance(bundle, dict):
        return ["verification bundle is missing"]
    failures.extend(validate_premises(bundle.get("premises", [])))
    failures.extend(validate_claims(bundle.get("claims", [])))
    failures.extend(validate_quotes(bundle.get("quotes", []), source_map))
    failures.extend(validate_holdings(bundle.get("holdings", [])))
    failures.extend(validate_treatment(bundle.get("precedent_treatment", [])))
    failures.extend(validate_temporal(bundle.get("temporal", []), bundle.get("relevant_date")))
    if bundle.get("retrieval_completeness") not in {"COMPLETE", "LIKELY_COMPLETE"}:
        failures.append("retrieval completeness is not sufficient for PASS")
    if bundle.get("adverse_search_status") != "COMPLETE":
        failures.append("adverse authority search is incomplete")
    if bundle.get("red_team_status") not in {"PASS", "SURVIVED"}:
        failures.append("red-team status is not clear")
    ok, confidence_failures = pass_threshold(bundle.get("confidence_vector", {}))
    if not ok:
        failures.extend(confidence_failures)
    return sorted(set(failures))


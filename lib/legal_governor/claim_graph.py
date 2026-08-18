"""Atomic legal claims and claim-to-source graph validation."""
from __future__ import annotations


MATERIALITY = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
CLAIM_TYPES = {"SOURCE FACT", "CLIENT ALLEGATION", "LEGAL RULE", "LEGAL INFERENCE", "MODEL ANALYSIS", "UNKNOWN"}
ENTAILMENT = {"SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "CONTRADICTED", "AMBIGUOUS"}


def validate_claims(claims: list[dict]) -> list[str]:
    failures = []
    if not isinstance(claims, list) or not claims:
        return ["material legal claims are missing"]
    ids = set()
    for index, row in enumerate(claims, start=1):
        cid = str(row.get("id", ""))
        if not cid or cid in ids:
            failures.append(f"claim[{index}] has missing or duplicate id")
        ids.add(cid)
        if row.get("materiality") not in MATERIALITY:
            failures.append(f"claim[{cid}].materiality is invalid")
        if row.get("type") not in CLAIM_TYPES:
            failures.append(f"claim[{cid}].type is invalid")
        if not str(row.get("text", "")).strip():
            failures.append(f"claim[{cid}].text is missing")
        if row.get("entailment") not in ENTAILMENT:
            failures.append(f"claim[{cid}].entailment is missing or invalid")
        if row.get("materiality") in {"CRITICAL", "HIGH"}:
            if row.get("entailment") != "SUPPORTED":
                failures.append(f"material claim {cid} is not fully supported")
            if not row.get("supporting_source_ids"):
                failures.append(f"material claim {cid} has no supporting source")
            if row.get("adverse_search_status") != "COMPLETE":
                failures.append(f"material claim {cid} adverse search is incomplete")
    return failures


def graph_edges(claims: list[dict]) -> list[dict]:
    edges = []
    for claim in claims or []:
        cid = claim.get("id")
        for source in claim.get("supporting_source_ids", []):
            edges.append({"from": cid, "type": "SUPPORTED_BY", "to": source})
        for source in claim.get("adverse_source_ids", []):
            edges.append({"from": cid, "type": "CONTRADICTED_BY", "to": source})
        for fact in claim.get("required_fact_ids", []):
            edges.append({"from": cid, "type": "REQUIRES", "to": fact})
    return edges


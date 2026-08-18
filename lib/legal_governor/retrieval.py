"""Dependency-light lexical, citation-graph, and retrieval-completeness engine.

Semantic retrieval is deliberately an adapter boundary. Without a configured
embedding provider this module returns UNAVAILABLE rather than fake vectors.
"""
from __future__ import annotations

import re
from collections import Counter


def lexical(query: str, sources: list[dict], limit: int = 20) -> list[dict]:
    terms = re.findall(r"[A-Za-z0-9§]+", query.lower())
    rows = []
    for source in sources:
        text = f"{source.get('title', '')} {source.get('citation', '')} {source.get('text', '')}".lower()
        counts = Counter(re.findall(r"[A-Za-z0-9§]+", text))
        score = sum(counts.get(term, 0) for term in terms)
        if score:
            rows.append({"source_id": source.get("id"), "lexical_score": score})
    return sorted(rows, key=lambda row: (-row["lexical_score"], str(row["source_id"])))[:limit]


def citation_graph(query_source_ids: list[str], edges: list[dict], limit: int = 50) -> list[dict]:
    ids = set(query_source_ids)
    expanded = []
    for edge in edges or []:
        if edge.get("from") in ids or edge.get("to") in ids:
            expanded.append(edge)
    return expanded[:limit]


def hybrid(query: str, sources: list[dict], edges: list[dict], *, semantic_results: list[dict] | None = None) -> dict:
    lexical_rows = lexical(query, sources)
    semantic_rows = semantic_results if semantic_results is not None else []
    semantic_status = "CONFIGURED" if semantic_results is not None else "UNAVAILABLE"
    ids = [row.get("source_id") for row in lexical_rows]
    graph = citation_graph(ids, edges)
    return {"semantic_status": semantic_status, "lexical": lexical_rows, "citation_graph": graph, "completeness": "UNKNOWN"}


def completeness(result: dict, *, statutory_text_found: bool, adverse_search_complete: bool, controlling_authority_found: bool) -> str:
    if result.get("semantic_status") == "UNAVAILABLE":
        return "UNKNOWN"
    if not statutory_text_found or not adverse_search_complete:
        return "INCOMPLETE"
    if controlling_authority_found and result.get("lexical") and result.get("citation_graph") is not None:
        return "LIKELY_COMPLETE"
    return "UNKNOWN"


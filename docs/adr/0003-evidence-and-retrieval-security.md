# ADR-0003: Evidence and Retrieval Security

Status: proposed

## Decision

Authorization, conflict, privilege, jurisdiction, retention, and legal-hold
filters execute before retrieval, ranking, embedding exposure, or model context
assembly. Evidence is immutable, classified, versioned, and linked to claims and
citations by exact spans and hashes.

## Consequence

Semantic search is additive only after lexical/source lineage and negative
authorization tests pass. Retrieved content is untrusted data.

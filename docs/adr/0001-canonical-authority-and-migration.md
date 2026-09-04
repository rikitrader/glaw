# ADR-0001: Canonical Authority and Strangler Migration

Status: proposed

## Decision

Existing GLAW gate semantics and source/workpaper hashes remain authoritative
during migration. New services consume adapters first; no big-bang rewrite or
silent replacement of local matter state.

## Consequence

Canonical IDs and provenance must be preserved across local, Worker, D1, and
future hosted representations. Every migrated workflow has shadow comparison,
canary, rollback, and replay evidence.

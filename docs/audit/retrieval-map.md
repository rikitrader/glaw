# Retrieval and Evidence Map

## Current baseline

- Source-locked lexical/citation retrieval and hashed source workpapers exist.
- Legal Governor verification and groundedness gates exist.
- Semantic vector storage is explicitly unavailable unless configured.
- Authority and jurisdiction packs exist in source form.

## Target additions

```text
ingest → hash → normalize → classify → entity/jurisdiction/date resolve
→ privilege/conflict filter → index → hybrid retrieve → authority rerank
→ contradiction search → claim linking → citation validation → human verification
```

## Critical rule

Authorization and privilege filters happen before retrieval exposure and model
context assembly. Vector search cannot bypass source lineage or matter scope.

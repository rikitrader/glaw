# Data Flow Audit

## Current flow

```text
request → intake/KV or local matter folder
→ Managing Partner / specialist skill
→ source-locked retrieval and workpapers
→ citation/adversarial/legal-governor gates
→ draft/final packet
```

## Target flow

```text
request → identity/tenant/matter/conflict/privilege authorization
→ command envelope → task graph
→ permission-filtered evidence ingestion/retrieval
→ claim/evidence/citation graph
→ Red/Blue/Judge
→ human approval
→ reproducible proof packet
→ external command receipt + authoritative reconciliation
```

## Data-flow risks

- Current local and Worker persistence boundaries can diverge.
- UI/event streams must not become authority.
- Semantic retrieval must not be added before authorization and provenance tests.
- External completion must be independently verified.
- Model context must be assembled only after all scope and privilege filters.

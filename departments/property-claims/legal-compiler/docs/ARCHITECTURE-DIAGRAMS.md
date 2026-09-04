# PCLC architecture diagrams

## System

```mermaid
flowchart LR
  C[Claim facts + policy] --> I[Issue classifier]
  I --> J[Jurisdiction/date resolver]
  J --> S[Source registry + snapshots]
  S --> V[Authority verifier]
  V --> P[Propositions]
  P --> R[Safe rule DSL]
  R --> A[Red / Blue review]
  A --> W[White neutral review]
  W --> H[Human gate]
  H --> O[Versioned authority package]
  O --> GCAE[Coverage Authority Engine]
  GCAE --> X[Xactimate evidence engine]
```

## Temporal rule compilation

```mermaid
flowchart TD
  A[Authority source] --> AV[Authority versions]
  AV --> VT{Valid on loss date?}
  VT -- no --> N[Not applicable]
  VT -- yes --> P[Verified proposition]
  P --> CR[Compiled rule]
  CR --> C[Claim legal context]
  C --> D[Decision with rule/source snapshot IDs]
```

## Red/Blue/White

```mermaid
flowchart LR
  R[Red: insured/contractor] <--> B[Blue: carrier]
  R --> W[White: neutral evidence + authority analysis]
  B --> W
  W --> AP[Appellate independent review]
  AP --> H[Human approval if required]
```

Semantic retrieval assists discovery only. Authority hierarchy, dates, policy language, and source verification control the result.

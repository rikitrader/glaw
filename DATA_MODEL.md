# Legal Governor Data Model

The current zero-dependency persistence model uses matter workpapers:

| Artifact | Purpose |
|---|---|
| `workpapers/source-universe.jsonl` | immutable source metadata and hashes |
| `workpapers/rag-context.json` | source-bound retrieval context digest |
| `workpapers/claude-analysis.json` | independent Claude output binding |
| `workpapers/codex-analysis.json` | independent Codex output binding |
| `workpapers/verification-bundle.json` | premises, claims, graph checks, confidence |
| `workpapers/legal-governor-report.json` | deterministic decision and reasons |
| `workpapers/legal-governor-audit.jsonl` | append-only hash-chain audit |
| `workpapers/dependency-matrix.json` | lane/department/gate dependencies |

A future PostgreSQL migration must preserve these identifiers and hashes as
foreign keys and immutable source-version records; it must not change the gate
semantics.

# HAEIS — Hanke Applied Economics Intelligence System

HAEIS is a source-locked, adversarial economics research department for GLAW. It reconstructs and tests Steve H. Hanke's published work without impersonating him. It preserves the distinction between direct source claims, framework derivations, system calculations, historical evidence, competing views, red-team challenges, blue-team responses, and unresolved issues.

This first implementation is intentionally provider-independent. Retrieval adapters may be added later, but no citation or policy conclusion is accepted without a source record and an audit trail.

## Guarantees

- Unsupported Hanke attribution is blocked as `ATTRIBUTION_BLOCKED`.
- Significant numbers must be produced by deterministic formula functions.
- Historical data retain observation, release, revision, and source metadata.
- Red Team, Blue Team, second Red Team, data, math, and citation gates are explicit workflow nodes.
- A policy recommendation may conclude `SUPPORTED`, `SUPPORTED_WITH_CONDITIONS`, or `NOT_SUPPORTED`; it is never hard-coded to agree with Hanke.

## Module map

| Area | Location |
|---|---|
| Department and source taxonomy | `department.yaml` |
| Typed contracts | `src/types.ts` |
| Deterministic formulas | `src/formulas.ts` |
| Source and claim registries | `rag/`, `schemas/` |
| Agents and postures | `agents/`, `postures/` |
| Required skills | `skills/` |
| Workflows and benchmarks | `workflows/`, `benchmarks/` |
| Verification | `tests/` |
| Build ledger | `IMPLEMENTATION_LEDGER.md` |

## Start an intake

Run the safe template validation first:

```sh
npm run intake:validate
```

For a matter-scoped readiness report:

```sh
npm run intake:start -- intake/venezuela-dollarization.json
```

The Venezuela template is intentionally `UNAVAILABLE`/source-empty and therefore
reports `BLOCKED` until verified source IDs and lineaged data
are supplied. It must not be populated with guessed values. To execute the full
workflow after those prerequisites are satisfied:

```sh
npm run run:venezuela
```

The run writes an auditable JSON result and JSONL event log under `runs/`. A
policy conclusion emits an explicit post-run human-review packet and the
supporting, contradictory, and alternative-explanation evidence-search lanes.

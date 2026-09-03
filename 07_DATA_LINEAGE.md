# Data Lineage

## Confirmed paths

```text
Public intake JSON
  -> glaw-intake Worker
  -> INTAKE_KV key intake:<timestamp>:<id>
  -> routed lanes + handoff package

Legal request JSON + source IDs
  -> glaw-intake Worker legal routes
  -> INTAKE_KV legal:request:<id>
  -> append-only legal:audit:<timestamp>:<audit-id>
  -> research / verification / red-team evidence
  -> named human review

Matter source files
  -> source-universe.jsonl with hashes
  -> retrieval context digest
  -> analysis bindings
  -> verification bundle
  -> Legal Governor report and audit chain

Local matter operations
  -> matter.md + intake.json + timeline.jsonl + docket.jsonl
  -> stage gate and final packet artifacts

Local SKILL.md files
  -> x402 catalog import
  -> D1 agent/service matrix
  -> quote / charge / authorization state
```

## Ownership findings

- Matter workpapers are the current legal evidence owner.
- `INTAKE_KV` owns intake/API workflow records, but it is not a relational system of record.
- X402 D1 owns its paid-agent catalog and charge domain.
- Architecture metadata currently has no owner or persistence model.

## Gaps

1. No architecture graph lineage from source file to node/edge is generated automatically.
2. No explicit table/column lineage exists for D1 beyond migration/source code.
3. No R2 artifact store is configured for large evidence or graph snapshots.
4. No tenant-aware permission filter is evidenced inside the RAG retrieval path.
5. No runtime telemetry lineage connects execution, model, cost, latency, or retries to workpapers.

## Proposed Cloudflare fit

Use D1 for normalized architecture nodes, edges, evidence references, ownership, and versions; R2 for large scan artifacts and source snapshots; Queues for asynchronous scans; Workflows for durable scan/rebuild stages; and a Durable Object only for collaborative graph editing or serialized publication. Do not use KV for graph transactions.

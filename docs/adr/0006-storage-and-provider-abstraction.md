# ADR-0006: Storage and Provider Abstraction

Status: proposed

## Decision

Business logic uses interfaces for relational state, object storage, search,
vector, graph, cache, queues, events, identity, KMS, inference, and telemetry.
Cloudflare is the initial deployment fit where already specified, but no business
logic imports provider-specific APIs directly.

## Consequence

SaaS, single-tenant, customer VPC, private, on-prem, and air-gapped modes remain
possible, at the cost of adapter and contract-test work.

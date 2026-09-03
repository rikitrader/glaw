# ADR-0007: Security, Observability, and Evaluation

Status: proposed

## Decision

Every run receives trace, matter, workflow, agent, and command identities.
Sensitive content is excluded from ordinary logs. Production readiness requires
threat modeling, tenant-isolation tests, chaos/fault tests, legal benchmark
regression, accessibility checks, SLOs, cost telemetry, runbooks, and rollback.

## Consequence

No completion claim is accepted from a model response alone. Release evidence is
part of the product and is exportable in a GLAW Proof Packet.

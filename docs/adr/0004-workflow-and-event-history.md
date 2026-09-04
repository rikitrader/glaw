# ADR-0004: Workflow and Event History

Status: proposed

## Decision

Workflows are versioned DAG/state-machine hybrids. Critical transitions emit
immutable events; materialized state is a query projection. Red/Blue/Judge loops
are bounded by rounds, thresholds, and critical-failure rules.

## Consequence

Pause, resume, replay, retry, compensation, dead-letter, and reconciliation are
first-class behavior, not ad hoc error handling.

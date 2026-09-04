# GLAW Production Control-Plane Runbook

## Deploy

1. Verify migration compatibility, signed artifact, SBOM, benchmark results, threat-model sign-off, and rollback target.
2. Apply database migrations forward-only in the home region.
3. Deploy to one canary region/tenant cohort.
4. Verify health, authorization-denial tests, audit signature continuity, queue lag, model policy enforcement, and connector reconciliation.
5. Expand only after SLOs hold for the defined observation window.

## Rollback

Stop promotion, fence writes for the affected region, preserve traces/events, and route read-only work to the last healthy deployment. Roll back application artifacts first; use database rollback only through a reviewed forward-compatible migration. Reconcile every in-flight command before resuming writes.

## Region failure

Declare incident, increment fencing epoch, stop writes in the failed region, validate residency and key availability in the target region, restore or promote the latest verified state, replay durable events, and reconcile all external operations. Do not report completion from a local HTTP response alone.

## Connector incident

Pause the connector capability, stop retries after the configured attempt limit, move malformed or exhausted jobs to a dead-letter queue, retain payload hashes and redacted failure metadata, and require human disposition before replay.

## Model incident

Disable the deployment in the registry, stop canary traffic, route only to a policy-approved fallback, preserve model/version/benchmark telemetry, and rerun the affected benchmark suite before re-enabling.

## Evidence to retain

Trace IDs, command IDs, workflow events, policy versions, model versions, connector receipts, reconciliation results, audit export manifest, incident timeline, and reviewer approvals.

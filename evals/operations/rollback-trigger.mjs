import assert from "node:assert/strict";
const thresholds = { citationAccuracy: .99, unsupportedClaimRate: .001, schemaFailureRate: .001, p95LatencyMs: 2000, securityAnomalies: 0 };
const observed = { citationAccuracy: Number(process.env.GLAW_CANARY_CITATION_ACCURACY ?? .98), unsupportedClaimRate: Number(process.env.GLAW_CANARY_UNSUPPORTED_RATE ?? .002), schemaFailureRate: Number(process.env.GLAW_CANARY_SCHEMA_FAILURE_RATE ?? .002), p95LatencyMs: Number(process.env.GLAW_CANARY_P95_MS ?? 2500), securityAnomalies: Number(process.env.GLAW_CANARY_SECURITY_ANOMALIES ?? 0) };
const failed = observed.citationAccuracy < thresholds.citationAccuracy || observed.unsupportedClaimRate > thresholds.unsupportedClaimRate || observed.schemaFailureRate > thresholds.schemaFailureRate || observed.p95LatencyMs > thresholds.p95LatencyMs || observed.securityAnomalies > thresholds.securityAnomalies;
const report = { test: "canary-rollback-trigger", observed, thresholds, expectedAction: failed ? "ROLLBACK" : "PROMOTE", passed: failed, generatedAt: new Date().toISOString() };
assert.equal(report.expectedAction, "ROLLBACK");
console.log(JSON.stringify(report));

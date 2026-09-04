#!/usr/bin/env node

const baseUrl = process.env.GLAW_LOCAL_URL ?? "http://127.0.0.1:8788";
const token = process.env.CONTROL_PLANE_API_TOKEN ?? "local-dev-only-token";

const response = await fetch(`${baseUrl}/api/health`);
if (!response.ok) throw new Error(`health endpoint returned ${response.status}`);
const health = await response.json();
if (!health.ok || health.environment !== "local") {
  throw new Error(`unexpected local health response: ${JSON.stringify(health)}`);
}

const metricsResponse = await fetch(`${baseUrl}/api/command-center`);
if (metricsResponse.status !== 200) throw new Error(`command-center endpoint returned ${metricsResponse.status}`);
const metrics = await metricsResponse.json();
if (!metrics.ok || metrics.metrics.openMatters < 1 || metrics.metrics.pendingApprovals < 1) {
  throw new Error(`seed data is missing: ${JSON.stringify(metrics)}`);
}

console.log(JSON.stringify({ ok: true, health, metrics }, null, 2));

const smokeId = `cmd-local-smoke-${Date.now()}`;
const command = {
  commandId: smokeId,
  idempotencyKey: smokeId,
  tenantId: "org-local",
  matterId: "matter-local-001",
  actor: { actorId: "user-local-admin", actorType: "human", role: "administrator" },
  authority: { policyId: "local-policy", policyVersion: "1.0.0" },
  action: "research.search",
  payload: { query: "smoke" },
  riskClass: "LOW",
  evidenceRefs: [],
  approvalRefs: [],
  createdAt: new Date().toISOString()
};

const commandHeaders = {
  "content-type": "application/json",
  authorization: `Bearer ${token}`,
  "x-glaw-actor-id": "user-local-admin",
  "x-glaw-tenant-id": "org-local",
  "x-glaw-role": "administrator",
  "x-glaw-actor-type": "human",
  "idempotency-key": command.idempotencyKey
};

const identityHeaders = {
  authorization: `Bearer ${token}`,
  "x-glaw-actor-id": "user-local-admin",
  "x-glaw-tenant-id": "org-local",
  "x-glaw-role": "administrator",
  "x-glaw-actor-type": "human"
};
const firstCommand = await fetch(`${baseUrl}/api/commands`, { method: "POST", headers: commandHeaders, body: JSON.stringify(command) });
if (firstCommand.status !== 201) throw new Error(`command create returned ${firstCommand.status}: ${await firstCommand.text()}`);
const replayCommand = await fetch(`${baseUrl}/api/commands`, { method: "POST", headers: commandHeaders, body: JSON.stringify(command) });
if (replayCommand.status !== 200) throw new Error(`command replay returned ${replayCommand.status}: ${await replayCommand.text()}`);

console.log(JSON.stringify({ commandCreate: firstCommand.status, commandReplay: replayCommand.status }));

const highRiskId = `${smokeId}-critical`;
const highRisk = { ...command, commandId: highRiskId, idempotencyKey: highRiskId, action: "court.file", riskClass: "CRITICAL" };
const highRiskResponse = await fetch(`${baseUrl}/api/commands`, { method: "POST", headers: { ...commandHeaders, "idempotency-key": highRisk.idempotencyKey }, body: JSON.stringify(highRisk) });
if (highRiskResponse.status !== 202) throw new Error(`high-risk command should require approval, got ${highRiskResponse.status}: ${await highRiskResponse.text()}`);

const unauthorizedResponse = await fetch(`${baseUrl}/api/commands`, { method: "POST", headers: { "content-type": "application/json", "idempotency-key": "cmd-local-smoke-unauthorized" }, body: JSON.stringify(command) });
if (unauthorizedResponse.status !== 401) throw new Error(`unauthorized command should return 401, got ${unauthorizedResponse.status}`);

const snapshotResponse = await fetch(`${baseUrl}/api/matters/matter-local-001/snapshot`, { headers: identityHeaders });
if (snapshotResponse.status !== 200) throw new Error(`authorized matter snapshot returned ${snapshotResponse.status}: ${await snapshotResponse.text()}`);
const snapshot = await snapshotResponse.json();
if (!snapshot.ok || snapshot.matter.id !== "matter-local-001" || !snapshot.authorization.relationshipsEvaluated.length) throw new Error(`invalid matter snapshot: ${JSON.stringify(snapshot)}`);
const crossTenantResponse = await fetch(`${baseUrl}/api/matters/matter-local-001/snapshot`, { headers: { ...identityHeaders, "x-glaw-tenant-id": "tenant-attacker", "x-glaw-actor-id": "attacker" } });
if (crossTenantResponse.status !== 403) throw new Error(`cross-tenant snapshot should return 403, got ${crossTenantResponse.status}`);

const runId = `run-local-smoke-${Date.now()}`;
const runResponse = await fetch(`${baseUrl}/api/workflows/runs`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: runId, matterId: "matter-local-001", workflowId: "workflow-local-intake", workflowVersion: "1.0.0", riskClass: "MODERATE", policyVersion: "policy-v1" }) });
if (runResponse.status !== 201) throw new Error(`workflow run returned ${runResponse.status}: ${await runResponse.text()}`);
const pauseResponse = await fetch(`${baseUrl}/api/workflows/runs/${runId}/control`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ action: "pause", reason: "local smoke test" }) });
if (pauseResponse.status !== 200) throw new Error(`workflow pause returned ${pauseResponse.status}: ${await pauseResponse.text()}`);
const resumeResponse = await fetch(`${baseUrl}/api/workflows/runs/${runId}/control`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ action: "resume", reason: "local smoke test" }) });
if (resumeResponse.status !== 200) throw new Error(`workflow resume returned ${resumeResponse.status}: ${await resumeResponse.text()}`);
const taskId = `task-local-smoke-${Date.now()}`;
const taskResponse = await fetch(`${baseUrl}/api/workflows/runs/${runId}/tasks`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: taskId, taskKey: "research-primary-law", taskType: "RESEARCH", assignedAgent: "legal-research" }) });
if (taskResponse.status !== 201) throw new Error(`workflow task returned ${taskResponse.status}: ${await taskResponse.text()}`);
const evidenceId = `evidence-local-smoke-${Date.now()}`;
const evidenceResponse = await fetch(`${baseUrl}/api/matters/matter-local-001/evidence`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: evidenceId, sourceType: "PRIMARY_LAW", sourceId: "local-source-001", sourceVersion: "1", documentHash: "sha256:local", page: 1, exactSpan: "verified test span" }) });
if (evidenceResponse.status !== 201) throw new Error(`evidence record returned ${evidenceResponse.status}: ${await evidenceResponse.text()}`);
const claimId = `claim-local-smoke-${Date.now()}`;
const claimResponse = await fetch(`${baseUrl}/api/matters/matter-local-001/claims`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: claimId, proposition: "Smoke claim is linked to evidence", claimType: "fact", evidence: [{ evidenceId, linkType: "SUPPORTS" }] }) });
if (claimResponse.status !== 201) throw new Error(`claim record returned ${claimResponse.status}: ${await claimResponse.text()}`);

const modelRegistry = await fetch(`${baseUrl}/api/models/registry`, { headers: identityHeaders });
if (modelRegistry.status !== 200) throw new Error(`model registry returned ${modelRegistry.status}: ${await modelRegistry.text()}`);
const benchmarkResponse = await fetch(`${baseUrl}/api/models/benchmarks`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: `benchmark-local-smoke-${Date.now()}`, deploymentId: "local-test-deployment", suite: "smoke", score: 1, sampleCount: 1, evaluatorVersion: "smoke-v1" }) });
if (benchmarkResponse.status !== 201) throw new Error(`benchmark registration returned ${benchmarkResponse.status}: ${await benchmarkResponse.text()}`);
const deploymentId = `deployment-local-smoke-${Date.now()}`;
const deploymentModel = `test-model-${Date.now()}`;
const deploymentPayload = { id: deploymentId, provider: "local", model: deploymentModel, version: "1", region: "local", rolloutStage: "BENCHMARK", enabled: false, benchmarkScore: 1, configHash: "local-config" };
const deploymentResponse = await fetch(`${baseUrl}/api/models/registry`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify(deploymentPayload) });
if (![200, 201].includes(deploymentResponse.status)) throw new Error(`deployment registration returned ${deploymentResponse.status}: ${await deploymentResponse.text()}`);
const deploymentBody = await deploymentResponse.json();
const effectiveDeploymentId = deploymentBody.deployment?.id ?? deploymentId;
const duplicateDeploymentResponse = await fetch(`${baseUrl}/api/models/registry`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ ...deploymentPayload, id: `${deploymentId}-duplicate` }) });
if (duplicateDeploymentResponse.status !== 200) throw new Error(`duplicate deployment registration should return 200, got ${duplicateDeploymentResponse.status}: ${await duplicateDeploymentResponse.text()}`);
const duplicateDeploymentBody = await duplicateDeploymentResponse.json();
if (!duplicateDeploymentBody.replayed || duplicateDeploymentBody.deployment?.id !== effectiveDeploymentId) throw new Error(`duplicate deployment did not return the canonical deployment: ${JSON.stringify(duplicateDeploymentBody)}`);
const blockedPromotion = await fetch(`${baseUrl}/api/models/rollout`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ deploymentId: effectiveDeploymentId, action: "PROMOTE", targetStage: "FULL" }) });
if (blockedPromotion.status !== 412) throw new Error(`unbenchmarked model should return 412, got ${blockedPromotion.status}`);
const deploymentBenchmark = await fetch(`${baseUrl}/api/models/benchmarks`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: `benchmark-deployment-${Date.now()}`, deploymentId: effectiveDeploymentId, suite: "smoke", score: 1, sampleCount: 1, evaluatorVersion: "smoke-v1" }) });
if (deploymentBenchmark.status !== 201) throw new Error(`deployment benchmark returned ${deploymentBenchmark.status}: ${await deploymentBenchmark.text()}`);
const promotion = await fetch(`${baseUrl}/api/models/rollout`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ deploymentId: effectiveDeploymentId, action: "PROMOTE", targetStage: "FULL" }) });
if (promotion.status !== 200) throw new Error(`model promotion returned ${promotion.status}: ${await promotion.text()}`);
const rollback = await fetch(`${baseUrl}/api/models/rollout`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ deploymentId: effectiveDeploymentId, action: "ROLLBACK" }) });
if (rollback.status !== 200) throw new Error(`model rollback returned ${rollback.status}: ${await rollback.text()}`);
const connectorId = `connector-op-local-${Date.now()}`;
const connector = await fetch(`${baseUrl}/api/connectors/operations`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: connectorId, matterId: "matter-local-001", commandId: highRiskId, connectorId: "local-test", idempotencyKey: connectorId, expectedState: { status: "prepared" } }) });
if (connector.status !== 201) throw new Error(`connector prepare returned ${connector.status}: ${await connector.text()}`);
const connectorReplay = await fetch(`${baseUrl}/api/connectors/operations`, { method: "POST", headers: { ...identityHeaders, "content-type": "application/json" }, body: JSON.stringify({ id: `${connectorId}-replay`, matterId: "matter-local-001", commandId: highRiskId, connectorId: "local-test", idempotencyKey: connectorId, expectedState: { status: "prepared" } }) });
if (connectorReplay.status !== 409) throw new Error(`connector duplicate should return 409, got ${connectorReplay.status}`);

console.log(JSON.stringify({ highRiskEscalated: highRiskResponse.status, unauthorizedDenied: unauthorizedResponse.status, snapshot: snapshotResponse.status, crossTenantDenied: crossTenantResponse.status, workflowPaused: pauseResponse.status, workflowResumed: resumeResponse.status, taskQueued: taskResponse.status, evidenceRecorded: evidenceResponse.status, claimCreated: claimResponse.status, modelRegistry: modelRegistry.status, benchmarkRecorded: benchmarkResponse.status, modelRegistration: deploymentResponse.status, benchmarkGate: blockedPromotion.status, modelPromotion: promotion.status, modelRollback: rollback.status, connectorPrepared: connector.status, connectorDuplicate: connectorReplay.status }));

const auditExport = await fetch(`${baseUrl}/api/audit/export?matterId=matter-local-001`, { headers: identityHeaders });
if (auditExport.status !== 200) throw new Error(`audit export returned ${auditExport.status}: ${await auditExport.text()}`);
const auditBody = await auditExport.json();
if (!auditBody.ok || !auditBody.audit.signature || auditBody.audit.manifest.eventCount < 1) throw new Error(`invalid audit export: ${JSON.stringify(auditBody)}`);
console.log(JSON.stringify({ auditExport: auditExport.status, signedEvents: auditBody.audit.manifest.eventCount }));

import type { ControlPlaneDb } from "./db";
import { invokeThroughModelGateway, type ModelAdapter, type ModelPolicy, type ModelRequest } from "./model-gateway";

export async function invokeAndAuditModel(db: ControlPlaneDb, input: { tenantId: string; matterId?: string; workflowId?: string; policyVersion: string; request: ModelRequest; policy: ModelPolicy; adapter: ModelAdapter }): Promise<unknown> {
  const runId = crypto.randomUUID();
  const started = Date.now();
  const requestHash = await digest(JSON.stringify(input.request));
  const now = new Date().toISOString();
  await db.prepare("INSERT INTO model_runs (id, tenant_id, matter_id, workflow_id, task_type, provider, model, model_version, region, policy_version, benchmark_score, estimated_cost_usd, status, request_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'STARTED', ?, ?)").bind(runId, input.tenantId, input.matterId ?? null, input.workflowId ?? null, input.request.taskType, input.request.provider, input.request.model, input.request.model, input.request.region ?? null, input.policyVersion, input.request.benchmarkScore, input.request.estimatedCostUsd, requestHash, now).run();
  try {
    const result = await invokeThroughModelGateway(input.request, input.policy, input.adapter);
    await db.prepare("UPDATE model_runs SET status = 'SUCCEEDED', response_hash = ?, latency_ms = ?, completed_at = ? WHERE id = ? AND tenant_id = ?").bind(await digest(JSON.stringify(result.output)), Date.now() - started, new Date().toISOString(), runId, input.tenantId).run();
    return result.output;
  } catch (error) {
    await db.prepare("UPDATE model_runs SET status = 'BLOCKED', latency_ms = ?, completed_at = ? WHERE id = ? AND tenant_id = ?").bind(Date.now() - started, new Date().toISOString(), runId, input.tenantId).run();
    throw error;
  }
}

async function digest(value: string): Promise<string> { const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)); return Array.from(new Uint8Array(bytes), (b) => b.toString(16).padStart(2, "0")).join(""); }

import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../../../lib/control-plane/db";
import { authorizeRelation } from "../../../../../lib/control-plane/authorization";
import { appendAuditEvent } from "../../../../../lib/control-plane/audit";

export const prerender = false;
export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const runId = request.url.split("/runs/")[1]?.split("/")[0] ?? "";
  let body: { id?: string; taskKey?: string; taskType?: string; assignedAgent?: string; inputHash?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!runId || !body.id || !body.taskKey || !body.taskType) return jsonError("run id, task id, task key, and task type are required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const run = await db.prepare("SELECT matter_id, control_state FROM workflow_runs WHERE id = ? AND organization_id = ?").bind(runId, principal.tenantId).first<{ matter_id: string; control_state: string }>();
  if (!run) return jsonError("workflow run not found", 404);
  if (run.control_state !== "ACTIVE") return jsonError(`workflow is ${run.control_state.toLowerCase()}`, 409);
  const access = await authorizeRelation(db, principal, "workflow.start", "matter", run.matter_id, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  const now = new Date().toISOString();
  try { await db.prepare("INSERT INTO workflow_tasks (id, run_id, organization_id, matter_id, task_key, task_type, assigned_agent, state, input_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'QUEUED', ?, ?, ?)").bind(body.id, runId, principal.tenantId, run.matter_id, body.taskKey, body.taskType, body.assignedAgent ?? null, body.inputHash ?? null, now, now).run(); } catch (error) { return jsonError(error instanceof Error && error.message.includes("UNIQUE") ? "task already exists" : "task could not be created", error instanceof Error && error.message.includes("UNIQUE") ? 409 : 400); }
  await appendAuditEvent(db, { tenantId: principal.tenantId, matterId: run.matter_id, actorId: principal.actorId, traceId: crypto.randomUUID(), eventType: "workflow.task.queued", payload: { runId, taskId: body.id, taskKey: body.taskKey, taskType: body.taskType } });
  return new Response(JSON.stringify({ ok: true, task: { id: body.id, runId, state: "QUEUED", createdAt: now } }), { status: 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

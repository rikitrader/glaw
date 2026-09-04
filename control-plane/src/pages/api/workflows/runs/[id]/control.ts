import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../../../lib/control-plane/db";
import { authorizeRelation } from "../../../../../lib/control-plane/authorization";
import { appendAuditEvent } from "../../../../../lib/control-plane/audit";

export const prerender = false;

const transitions: Record<string, { from: string[]; to: string }> = {
  pause: { from: ["ACTIVE"], to: "PAUSED" },
  resume: { from: ["PAUSED"], to: "ACTIVE" },
  freeze: { from: ["ACTIVE", "PAUSED"], to: "FROZEN" },
  terminate: { from: ["ACTIVE", "PAUSED", "FROZEN"], to: "TERMINATED" }
};

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const runId = request.url.split("/runs/")[1]?.split("/")[0] ?? "";
  let body: { action?: string; reason?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  const transition = body.action ? transitions[body.action.toLowerCase()] : undefined;
  if (!runId || !transition || !body.action) return jsonError("run id and action (pause, resume, freeze, terminate) are required", 400);
  if (!body.reason?.trim()) return jsonError("a reason is required for workflow control actions", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const run = await db.prepare("SELECT id, matter_id, control_state FROM workflow_runs WHERE id = ? AND organization_id = ?").bind(runId, principal.tenantId).first<{ id: string; matter_id: string; control_state: string }>();
  if (!run) return jsonError("workflow run not found", 404);
  const access = await authorizeRelation(db, principal, "workflow.control", "matter", run.matter_id, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  if (!['attorney', 'administrator', 'admin'].includes(principal.role.toLowerCase())) return jsonError("authorized workflow controller role required", 403);
  if (!transition.from.includes(run.control_state)) return jsonError(`invalid transition from ${run.control_state}`, 409);
  const now = new Date().toISOString();
  await db.batch([
    db.prepare("UPDATE workflow_runs SET control_state = ?, updated_at = ? WHERE id = ? AND organization_id = ?").bind(transition.to, now, runId, principal.tenantId),
    db.prepare("INSERT INTO workflow_control_events (id, organization_id, matter_id, run_id, actor_id, action, previous_state, next_state, reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), principal.tenantId, run.matter_id, runId, principal.actorId, body.action.toUpperCase(), run.control_state, transition.to, body.reason.trim(), now)
  ]);
  await appendAuditEvent(db, { tenantId: principal.tenantId, matterId: run.matter_id, actorId: principal.actorId, traceId: crypto.randomUUID(), eventType: `workflow.${body.action.toLowerCase()}`, payload: { runId, previousState: run.control_state, nextState: transition.to, reason: body.reason.trim() } });
  return new Response(JSON.stringify({ ok: true, runId, controlState: transition.to, controlledAt: now }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

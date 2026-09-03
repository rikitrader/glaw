import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
import { authorizeRelation } from "../../../lib/control-plane/authorization";
import { appendAuditEvent } from "../../../lib/control-plane/audit";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const matterId = new URL(request.url).searchParams.get("matterId");
  if (!matterId) return jsonError("matterId is required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const access = await authorizeRelation(db, principal, "matter.read", "matter", matterId, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  const runs = await db.prepare("SELECT id, workflow_id, workflow_version, state, risk_class, policy_version, started_at, updated_at FROM workflow_runs WHERE organization_id = ? AND matter_id = ? ORDER BY updated_at DESC").bind(principal.tenantId, matterId).all();
  return new Response(JSON.stringify({ ok: true, runs: runs.results, authorization: access }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  let body: { id?: string; matterId?: string; workflowId?: string; workflowVersion?: string; riskClass?: string; policyVersion?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!body.id || !body.matterId || !body.workflowId || !body.workflowVersion || !body.riskClass || !body.policyVersion) return jsonError("run id, matter, workflow, version, risk class, and policy version are required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const access = await authorizeRelation(db, principal, "workflow.start", "matter", body.matterId, body.policyVersion);
  if (access.decision !== "ALLOW") return jsonError(access.reason, access.decision === "DENY" ? 403 : 202);
  const now = new Date().toISOString();
  try {
    await db.prepare("INSERT INTO workflow_runs (id, organization_id, matter_id, workflow_id, workflow_version, state, risk_class, policy_version, started_at, updated_at) VALUES (?, ?, ?, ?, ?, 'REQUESTED', ?, ?, ?, ?)").bind(body.id, principal.tenantId, body.matterId, body.workflowId, body.workflowVersion, body.riskClass, body.policyVersion, now, now).run();
    await appendAuditEvent(db, { tenantId: principal.tenantId, matterId: body.matterId, actorId: principal.actorId, traceId: crypto.randomUUID(), eventType: "workflow.run.requested", payload: { runId: body.id, workflowId: body.workflowId, workflowVersion: body.workflowVersion, riskClass: body.riskClass } });
  } catch (error) {
    return jsonError(error instanceof Error && error.message.includes("UNIQUE") ? "workflow run already exists" : "workflow run could not be created", error instanceof Error && error.message.includes("UNIQUE") ? 409 : 400);
  }
  return new Response(JSON.stringify({ ok: true, run: { id: body.id, matterId: body.matterId, state: "REQUESTED", startedAt: now } }), { status: 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

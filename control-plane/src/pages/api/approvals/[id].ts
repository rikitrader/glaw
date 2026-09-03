import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
import { authorizeRelation } from "../../../lib/control-plane/authorization";
import { appendAuditEvent } from "../../../lib/control-plane/audit";

export const prerender = false;

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const approvalId = request.url.split("/approvals/")[1]?.split("/")[0] ?? "";
  let body: { decision?: "approve" | "reject" | "revoke"; note?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!approvalId || !body.decision) return jsonError("approval id and decision are required", 400);
  if (!['attorney', 'administrator', 'admin'].includes(principal.role.toLowerCase())) return jsonError("authorized reviewer role required", 403);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const approval = await db.prepare("SELECT id, matter_id, status FROM approvals WHERE id = ? AND organization_id = ?").bind(approvalId, principal.tenantId).first<{ id: string; matter_id: string; status: string }>();
  if (!approval) return jsonError("approval not found", 404);
  const access = await authorizeRelation(db, principal, "matter.read", "matter", approval.matter_id, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  if (approval.status !== "pending" && body.decision !== "revoke") return jsonError("approval is not pending", 409);
  const next = body.decision === "approve" ? "approved" : body.decision === "reject" ? "rejected" : "revoked";
  const now = new Date().toISOString();
  await db.prepare("UPDATE approvals SET status = ?, decided_at = ? WHERE id = ? AND organization_id = ?").bind(next, now, approvalId, principal.tenantId).run();
  await appendAuditEvent(db, { tenantId: principal.tenantId, matterId: approval.matter_id, actorId: principal.actorId, traceId: crypto.randomUUID(), eventType: `approval.${body.decision}`, payload: { approvalId, note: body.note ?? null } });
  return new Response(JSON.stringify({ ok: true, approval: { id: approvalId, status: next, decidedAt: now } }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

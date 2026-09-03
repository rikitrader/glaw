import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../lib/control-plane/db";
import { authorizeRelation } from "../../lib/control-plane/authorization";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const matterId = new URL(request.url).searchParams.get("matterId");
  if (!matterId) return jsonError("matterId is required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const access = await authorizeRelation(db, principal, "matter.read", "matter", matterId, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  const rows = await db.prepare("SELECT id, matter_id, workflow_id, required_role, status, created_at, decided_at FROM approvals WHERE organization_id = ? AND matter_id = ? ORDER BY created_at DESC LIMIT 100").bind(principal.tenantId, matterId).all();
  return new Response(JSON.stringify({ ok: true, approvals: rows.results, authorization: access, freshness: new Date().toISOString() }), { headers: headers() });
}, env as unknown as Record<string, unknown>);

function headers() { return { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }; }

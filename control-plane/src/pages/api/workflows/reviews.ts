import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
import { authorizeRelation } from "../../../lib/control-plane/authorization";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const params = new URL(request.url).searchParams;
  const matterId = params.get("matterId");
  const workflowId = params.get("workflowId");
  const team = params.get("team");
  if (!matterId || !workflowId) return jsonError("matterId and workflowId are required", 400);
  if (team && !["RED_TEAM", "BLUE_TEAM"].includes(team)) return jsonError("team must be RED_TEAM or BLUE_TEAM", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const access = await authorizeRelation(db, principal, "matter.read", "matter", matterId, "policy-v1");
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  const query = team ? "SELECT id, workflow_id, run_id, team, state, severity, summary, evidence_refs_json, created_by, created_at, updated_at FROM workflow_reviews WHERE organization_id = ? AND matter_id = ? AND workflow_id = ? AND team = ? ORDER BY updated_at DESC LIMIT 100" : "SELECT id, workflow_id, run_id, team, state, severity, summary, evidence_refs_json, created_by, created_at, updated_at FROM workflow_reviews WHERE organization_id = ? AND matter_id = ? AND workflow_id = ? ORDER BY updated_at DESC LIMIT 100";
  const rows = team ? await db.prepare(query).bind(principal.tenantId, matterId, workflowId, team).all() : await db.prepare(query).bind(principal.tenantId, matterId, workflowId).all();
  return new Response(JSON.stringify({ ok: true, reviews: rows.results, authorization: access, freshness: new Date().toISOString() }), { headers: headers() });
}, env as unknown as Record<string, unknown>);

function headers() { return { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }; }

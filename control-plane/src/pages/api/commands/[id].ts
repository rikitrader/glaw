import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const id = String((_request as Request & { url: string }).url).split("/").pop() ?? "";
  if (!id) return jsonError("command id is required", 400);
  const row = await getControlPlaneDb(env as unknown as Record<string, unknown>).prepare("SELECT id, idempotency_key, organization_id, matter_id, actor_id, actor_type, actor_role, action, risk_class, status, payload_hash, created_at, expires_at FROM commands WHERE id = ? AND organization_id = ?").bind(id, principal.tenantId).first<Record<string, unknown>>();
  if (!row) return jsonError("command not found", 404);
  return new Response(JSON.stringify({ ok: true, command: row }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

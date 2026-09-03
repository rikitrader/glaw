import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const rows = await db.prepare("SELECT id, operation_id, kind, payload_hash, reason_code, state, created_at, reviewed_at, reviewed_by FROM dead_letter_items WHERE tenant_id = ? ORDER BY created_at DESC LIMIT 100").bind(principal.tenantId).all();
  return new Response(JSON.stringify({ ok: true, items: rows.results }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const id = request.url.split("dead-letters")[1]?.split("/")[1] ?? "";
  let body: { action?: "REPLAY" | "DISCARD"; reason?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!id || !body.action || !body.reason?.trim()) return jsonError("dead-letter id, action, and reason are required", 400);
  if (!['attorney', 'administrator', 'admin'].includes(principal.role.toLowerCase())) return jsonError("authorized reviewer role required", 403);
  const next = body.action === "REPLAY" ? "REPLAYED" : "DISCARDED";
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const result = await db.prepare("UPDATE dead_letter_items SET state = ?, reviewed_at = ?, reviewed_by = ? WHERE id = ? AND tenant_id = ? AND state = 'OPEN'").bind(next, new Date().toISOString(), principal.actorId, id, principal.tenantId).run();
  if (!result.meta || Number(result.meta.changes ?? 0) !== 1) return jsonError("dead-letter item not found or already reviewed", 409);
  return new Response(JSON.stringify({ ok: true, id, state: next, reason: body.reason.trim() }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

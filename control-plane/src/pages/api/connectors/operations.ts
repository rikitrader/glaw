import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const rows = await db.prepare("SELECT id, matter_id, command_id, connector_id, idempotency_key, state, external_request_id, external_transaction_id, expected_state_json, observed_state_json, reconciliation_json, created_at, updated_at FROM connector_operations WHERE tenant_id = ? ORDER BY updated_at DESC LIMIT 100").bind(principal.tenantId).all();
  return new Response(JSON.stringify({ ok: true, operations: rows.results }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  let body: { id?: string; matterId?: string; commandId?: string; connectorId?: string; idempotencyKey?: string; expectedState?: unknown };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!body.id || !body.commandId || !body.connectorId || !body.idempotencyKey || body.expectedState === undefined) return jsonError("operation id, command, connector, idempotency key, and expected state are required", 400);
  const now = new Date().toISOString();
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  try {
    await db.prepare("INSERT INTO connector_operations (id, tenant_id, matter_id, command_id, connector_id, idempotency_key, state, expected_state_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 'PREPARED', ?, ?, ?)").bind(body.id, principal.tenantId, body.matterId ?? null, body.commandId, body.connectorId, body.idempotencyKey, JSON.stringify(body.expectedState), now, now).run();
  } catch (error) {
    return jsonError(error instanceof Error && error.message.includes("UNIQUE") ? "connector idempotency key already exists" : "connector operation could not be prepared", error instanceof Error && error.message.includes("UNIQUE") ? 409 : 400);
  }
  return new Response(JSON.stringify({ ok: true, operation: { id: body.id, tenantId: principal.tenantId, state: "PREPARED", createdAt: now } }), { status: 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
import { acceptCommand } from "../../../lib/control-plane/commands";
import type { LegalCommand } from "../../../lib/contracts/legal";

export const prerender = false;

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  let body: LegalCommand;
  try {
    body = await request.json() as LegalCommand;
  } catch {
    return jsonError("request body must be valid JSON", 400);
  }
  const idempotencyHeader = request.headers.get("idempotency-key");
  if (!idempotencyHeader || idempotencyHeader !== body.idempotencyKey) return jsonError("Idempotency-Key header must match command.idempotencyKey", 400);
  if (body.tenantId !== principal.tenantId) return jsonError("tenant scope mismatch", 403);
  try {
    const result = await acceptCommand(getControlPlaneDb(env as unknown as Record<string, unknown>), body, principal);
    return new Response(JSON.stringify({ ok: true, ...result }), { status: result.replayed ? 200 : result.decision === "DENY" ? 403 : result.decision === "ESCALATE" ? 202 : 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
  } catch (error) {
    const message = error instanceof Error ? error.message : "command could not be accepted";
    return jsonError(message, message.includes("UNIQUE") ? 409 : 400);
  }
}, env as unknown as Record<string, unknown>);

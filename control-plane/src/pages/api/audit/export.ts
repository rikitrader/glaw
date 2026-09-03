import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
import { createAuditExport } from "../../../lib/control-plane/audit";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const url = new URL(request.url);
  const matterId = url.searchParams.get("matterId") ?? undefined;
  try {
    const audit = await createAuditExport(getControlPlaneDb(env as unknown as Record<string, unknown>), principal.tenantId, principal.actorId, String(env.GLAW_AUDIT_SIGNING_SECRET ?? ""), String(env.GLAW_AUDIT_SIGNING_KEY_ID ?? "local-dev-key"), matterId);
    return new Response(JSON.stringify({ ok: true, audit }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
  } catch (error) {
    return new Response(JSON.stringify({ ok: false, error: error instanceof Error ? error.message : "audit export failed" }), { status: 503, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
  }
}, env as unknown as Record<string, unknown>);

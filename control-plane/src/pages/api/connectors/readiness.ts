import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth } from "../../../lib/control-plane/auth";
import { getGovernedCatalog } from "../../../lib/workflows/governed-catalog";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const adapters = getGovernedCatalog().adapters.map((adapter) => ({ ...adapter, health: adapter.configured ? "CONFIGURED_NOT_HEALTH_CHECKED" : "NOT_CONFIGURED", tenantId: principal.tenantId }));
  return new Response(JSON.stringify({ ok: true, adapters, freshness: new Date().toISOString(), note: "Connector health is not inferred from catalog configuration; live health checks must be supplied by the connector worker." }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

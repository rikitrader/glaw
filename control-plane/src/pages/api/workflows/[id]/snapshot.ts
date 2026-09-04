import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth } from "../../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../../lib/control-plane/db";
import { getWorkflowScope } from "../../../../lib/control-plane/workflow-authority";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const workflowId = String(_request.url).split("/workflows/")[1]?.split("/")[0] ?? "";
  const result = await getWorkflowScope(getControlPlaneDb(env as unknown as Record<string, unknown>), principal, workflowId);
  if (result.error) return result.error;
  return new Response(JSON.stringify({ ok: true, snapshot: result.scope }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

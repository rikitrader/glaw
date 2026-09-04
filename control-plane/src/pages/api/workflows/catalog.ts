import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getGovernedCatalog, validateWorkflowBinding, type WorkflowBinding } from "../../../lib/workflows/governed-catalog";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  return new Response(JSON.stringify({ ok: true, tenantId: principal.tenantId, catalog: getGovernedCatalog() }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  let body: { binding?: WorkflowBinding };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!body.binding?.workflowId || !body.binding.departmentId || !body.binding.scope) return jsonError("workflowId, departmentId, and scope are required", 400);
  const findings = validateWorkflowBinding(body.binding);
  if (findings.length) return new Response(JSON.stringify({ ok: false, tenantId: principal.tenantId, status: "BLOCK", findings }), { status: 422, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
  return new Response(JSON.stringify({ ok: true, tenantId: principal.tenantId, status: "PASS", binding: body.binding }), { status: 200, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

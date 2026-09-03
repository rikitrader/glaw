import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth } from "../../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../../lib/control-plane/db";
import { getWorkflowScope, authorizeWorkflowWrite, persistWorkflowVersion, type WorkflowDefinition } from "../../../../lib/control-plane/workflow-authority";
import { validateGraph } from "../../../../lib/workflows/validator";

export const prerender = false;

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const workflowId = request.url.split("/workflows/")[1]?.split("/")[0] ?? "";
  let body: { nodes?: unknown[]; edges?: unknown[]; expectedRevision?: number; policyVersion?: string; environment?: "sandbox" | "staging" | "production" };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!Array.isArray(body.nodes) || !Array.isArray(body.edges)) return jsonError("nodes and edges arrays are required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const current = await getWorkflowScope(db, principal, workflowId);
  if (current.error || !current.scope) return current.error ?? jsonError("workflow scope unavailable", 404);
  const forbidden = await authorizeWorkflowWrite(db, principal, current.scope.matterId!, body.policyVersion ?? current.scope.policyVersion);
  if (forbidden) return forbidden;
  const definition: WorkflowDefinition = { nodes: body.nodes, edges: body.edges };
  const findings = validateGraph(body.nodes as never[], body.edges as never[]);
  if (findings.some((item) => item.severity === "error")) return new Response(JSON.stringify({ ok: false, status: "BLOCK", findings, reason: "workflow cannot be published until blocking validation findings are resolved" }), { status: 422, headers: headers() });
  const result = await persistWorkflowVersion(db, { principal, workflowId, matterId: current.scope.matterId!, definition, expectedRevision: body.expectedRevision ?? current.scope.revision, policyVersion: body.policyVersion ?? current.scope.policyVersion, environment: body.environment ?? current.scope.environment, status: "DRAFT", action: "REQUEST_PUBLISH", state: "approval_required", reason: "publish request recorded; human approval is required before activation" });
  if (!result.ok) return result.response;
  return new Response(JSON.stringify({ ok: true, status: "APPROVAL_REQUIRED", findings, ...result }), { status: 202, headers: headers() });
}, env as unknown as Record<string, unknown>);

function headers() { return { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }; }
function jsonError(message: string, status: number) { return new Response(JSON.stringify({ ok: false, error: message }), { status, headers: headers() }); }

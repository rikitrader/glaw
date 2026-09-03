import type { APIRoute } from "astro";

export type RequestPrincipal = {
  actorId: string;
  actorType: "human" | "agent" | "service";
  role: string;
  tenantId: string;
};

function constantTimeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) return false;
  let result = 0;
  for (let i = 0; i < left.length; i += 1) result |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return result === 0;
}

export function authenticateControlPlane(request: Request, env: Record<string, unknown>): RequestPrincipal | Response {
  const configured = typeof env.CONTROL_PLANE_API_TOKEN === "string" ? env.CONTROL_PLANE_API_TOKEN : "";
  if (!configured) return jsonError("control-plane authentication is not configured", 503);

  const authorization = request.headers.get("authorization") ?? "";
  const token = authorization.startsWith("Bearer ") ? authorization.slice(7) : "";
  if (!constantTimeEqual(token, configured)) return jsonError("unauthorized", 401);

  const actorId = request.headers.get("x-glaw-actor-id") ?? "";
  const tenantId = request.headers.get("x-glaw-tenant-id") ?? "";
  const role = request.headers.get("x-glaw-role") ?? "";
  const actorType = request.headers.get("x-glaw-actor-type") ?? "service";
  if (!actorId || !tenantId || !role || !["human", "agent", "service"].includes(actorType)) {
    return jsonError("actor identity headers are required", 400);
  }
  return { actorId, tenantId, role, actorType: actorType as RequestPrincipal["actorType"] };
}

export function jsonError(message: string, status: number): Response {
  return new Response(JSON.stringify({ ok: false, error: message }), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}

export function apiRouteWithAuth(handler: (request: Request, principal: RequestPrincipal) => Promise<Response>, configuredEnv?: Record<string, unknown>): APIRoute {
  return async ({ request, locals }) => {
    const env = configuredEnv ?? (locals as { runtime?: { env?: Record<string, unknown> } }).runtime?.env ?? {};
    const principal = authenticateControlPlane(request, env);
    if (principal instanceof Response) return principal;
    return handler(request, principal);
  };
}

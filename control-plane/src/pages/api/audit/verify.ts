import type { APIRoute } from "astro";
import { verifyAuditChain, type AuditExport } from "../../../lib/control-plane/audit";

export const prerender = false;
export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json() as { audit?: AuditExport };
    if (!body.audit) return new Response(JSON.stringify({ ok: false, error: "audit payload is required" }), { status: 400, headers: { "content-type": "application/json" } });
    const result = verifyAuditChain(body.audit);
    return new Response(JSON.stringify({ ok: result.valid, verification: result }), { status: result.valid ? 200 : 422, headers: { "content-type": "application/json", "cache-control": "no-store" } });
  } catch { return new Response(JSON.stringify({ ok: false, error: "request body must be valid JSON" }), { status: 400, headers: { "content-type": "application/json" } }); }
};

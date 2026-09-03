import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";

export const prerender = false;

export const GET: APIRoute = async () => {
  const db = env.GLAW_DB as unknown as { prepare: (sql: string) => { first: <T>() => Promise<T> } } | undefined;

  if (!db) {
    return new Response(JSON.stringify({
      ok: false,
      status: "unavailable",
      reason: "GLAW_DB binding is not configured"
    }), { status: 503, headers: { "content-type": "application/json; charset=utf-8" } });
  }

  const [matters, approvals, workflows] = await Promise.all([
    db.prepare("SELECT COUNT(*) AS count FROM matters WHERE status = 'active'").first<{ count: number }>(),
    db.prepare("SELECT COUNT(*) AS count FROM approvals WHERE status = 'pending'").first<{ count: number }>(),
    db.prepare("SELECT COUNT(*) AS count FROM workflows WHERE status IN ('confirmed', 'running')").first<{ count: number }>()
  ]);

  return new Response(JSON.stringify({
    ok: true,
    metrics: {
      openMatters: matters?.count ?? 0,
      pendingApprovals: approvals?.count ?? 0,
      activeWorkflows: workflows?.count ?? 0
    }
  }), { headers: { "content-type": "application/json; charset=utf-8" } });
};

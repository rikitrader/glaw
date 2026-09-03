import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";

export const prerender = false;

export const GET: APIRoute = () => {
  return new Response(JSON.stringify({
    ok: true,
    environment: env.APP_ENV ?? "unknown",
    controlPlaneMode: env.CONTROL_PLANE_MODE ?? "unknown",
    bindings: {
      database: Boolean(env.GLAW_DB),
      objects: Boolean(env.GLAW_OBJECTS),
      jobs: Boolean(env.GLAW_JOBS),
      session: Boolean(env.SESSION)
    },
    generatedAt: new Date().toISOString()
  }), { headers: { "content-type": "application/json; charset=utf-8" } });
};

// GLAW public intake app — API + static assets.
// POST /api/intake        store a routed intake submission (KV)
// GET  /api/intake/:id    fetch one submission
// GET  /api/intakes       list submissions (requires Bearer INTAKE_ADMIN_TOKEN secret)
// everything else         static assets (public/)

const MAX_BODY = 64 * 1024;

const json = (data, status = 200) =>
  new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (url.pathname === "/api/intake" && req.method === "POST") {
      const raw = await req.text();
      if (raw.length > MAX_BODY) return json({ error: "Submission too large" }, 413);
      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        return json({ error: "Body must be valid JSON" }, 400);
      }
      if (!data.track || !data.goal) {
        return json({ error: "Missing required fields: track, goal" }, 400);
      }
      const id = crypto.randomUUID().slice(0, 8);
      const ts = new Date().toISOString();
      const record = { id, ts, ...data };
      await env.INTAKE_KV.put(`intake:${ts}:${id}`, JSON.stringify(record), {
        metadata: { track: String(data.track), matter: String(data.matter_name || "").slice(0, 80) },
      });
      return json({ ok: true, id, ts });
    }

    const one = url.pathname.match(/^\/api\/intake\/([A-Za-z0-9-]+)$/);
    if (one && req.method === "GET") {
      const list = await env.INTAKE_KV.list({ prefix: "intake:" });
      const key = list.keys.find((k) => k.name.endsWith(`:${one[1]}`));
      if (!key) return json({ error: "Not found" }, 404);
      const val = await env.INTAKE_KV.get(key.name);
      return new Response(val, { headers: { "content-type": "application/json; charset=utf-8" } });
    }

    if (url.pathname === "/api/intakes" && req.method === "GET") {
      const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
      if (!env.INTAKE_ADMIN_TOKEN || token !== env.INTAKE_ADMIN_TOKEN) {
        return json({ error: "Unauthorized" }, 401);
      }
      const list = await env.INTAKE_KV.list({ prefix: "intake:", limit: 200 });
      return json(
        list.keys.map((k) => ({
          key: k.name,
          id: k.name.split(":").pop(),
          ts: k.name.split(":").slice(1, -1).join(":"),
          track: k.metadata?.track,
          matter: k.metadata?.matter,
        }))
      );
    }

    return env.ASSETS.fetch(req);
  },
};

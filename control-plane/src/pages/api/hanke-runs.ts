import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { validateHaeisRunPayload, type HaeisRunPayload } from "../../lib/hanke-validation";

export const prerender = false;

type HaeisDb = {
  prepare: (sql: string) => { bind: (...values: unknown[]) => { run: () => Promise<unknown>; all: <T>() => Promise<{ results: T[] }> }; first: <T>() => Promise<T | null> };
};

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8" } });

export const GET: APIRoute = async ({ url }) => {
  const db = (env as unknown as { GLAW_DB?: HaeisDb }).GLAW_DB;
  if (!db) return json({ ok: false, status: "unavailable", reason: "GLAW_DB binding is not configured" }, 503);
  const runId = url.searchParams.get("run_id");
  if (runId) {
    const run = await db.prepare("SELECT run_id, organization_id, matter_id, workflow_id, status, review_status, reviewer_id, review_note, reviewed_at, payload_json, created_at, updated_at FROM hanke_runs WHERE run_id = ?").bind(runId).first<Record<string, unknown>>();
    if (!run) return json({ ok: false, status: "not_found", run_id: runId }, 404);
    const gates = await db.prepare("SELECT gate_id, status, owner, evidence_ids_json, reason, recorded_at FROM hanke_gate_records WHERE run_id = ? ORDER BY gate_id").bind(runId).all<Record<string, unknown>>();
    return json({ ok: true, run, gates: gates.results });
  }
  const runs = await db.prepare("SELECT run_id, organization_id, matter_id, workflow_id, status, review_status, reviewer_id, reviewed_at, created_at, updated_at FROM hanke_runs ORDER BY updated_at DESC LIMIT 100").all<Record<string, unknown>>();
  return json({ ok: true, runs: runs.results });
};

export const POST: APIRoute = async ({ request }) => {
  const bindings = env as unknown as { GLAW_DB?: HaeisDb; HAEIS_RUN_TOKEN?: string };
  if (!bindings.GLAW_DB) return json({ ok: false, status: "unavailable", reason: "GLAW_DB binding is not configured" }, 503);
  if (!bindings.HAEIS_RUN_TOKEN) return json({ ok: false, status: "misconfigured", reason: "HAEIS_RUN_TOKEN secret is not configured" }, 503);
  if (request.headers.get("authorization") !== `Bearer ${bindings.HAEIS_RUN_TOKEN}`) return json({ ok: false, status: "unauthorized" }, 401);
  let payload: HaeisRunPayload;
  try { payload = await request.json(); } catch { return json({ ok: false, status: "invalid_json" }, 400); }
  const validationErrors = validateHaeisRunPayload(payload);
  if (validationErrors.length) return json({ ok: false, status: "invalid_payload", errors: validationErrors }, 400);
  const reviewStatus = payload.review?.status ?? "PENDING";
  const now = new Date().toISOString();
  const db = bindings.GLAW_DB;
  await db.prepare("INSERT INTO hanke_runs (run_id, organization_id, matter_id, workflow_id, status, review_status, reviewer_id, review_note, reviewed_at, payload_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(run_id) DO UPDATE SET status = excluded.status, review_status = excluded.review_status, reviewer_id = excluded.reviewer_id, review_note = excluded.review_note, reviewed_at = excluded.reviewed_at, payload_json = excluded.payload_json, updated_at = excluded.updated_at").bind(payload.run_id, payload.organization_id, payload.matter_id ?? null, payload.workflow_id, payload.status, reviewStatus, payload.review?.reviewer_id ?? null, payload.review?.note ?? null, reviewStatus === "PENDING" ? null : now, JSON.stringify(payload), now, now).run();
  for (const [gateId, gate] of Object.entries(payload.gate_records)) await db.prepare("INSERT INTO hanke_gate_records (run_id, gate_id, status, owner, evidence_ids_json, reason, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(run_id, gate_id) DO UPDATE SET status = excluded.status, owner = excluded.owner, evidence_ids_json = excluded.evidence_ids_json, reason = excluded.reason, recorded_at = excluded.recorded_at").bind(payload.run_id, gateId, gate.status, gate.owner, JSON.stringify(gate.evidence_ids), gate.reason ?? null, now).run();
  for (const event of payload.events) await db.prepare("INSERT OR REPLACE INTO hanke_run_events (run_id, sequence, event_type, payload_json, recorded_at) VALUES (?, ?, ?, ?, ?)").bind(payload.run_id, event.sequence, event.type, JSON.stringify(event.payload ?? {}), now).run();
  return json({ ok: true, run_id: payload.run_id, status: payload.status, persisted_at: now }, 201);
};

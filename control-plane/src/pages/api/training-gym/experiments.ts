import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;
const canManage = (role: string) => ["admin", "administrator", "researcher", "service"].includes(role.toLowerCase());

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const rows = await db.prepare("SELECT id, name, gym_version, dataset_version, task_id, models_json, episodes_per_model, concurrency, seed_strategy, status, created_by, created_at, updated_at FROM gym_experiments WHERE organization_id = ? ORDER BY created_at DESC").bind(principal.tenantId).all();
  return new Response(JSON.stringify({ ok: true, experiments: rows.results }), { headers: { "content-type": "application/json", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  if (!canManage(principal.role)) return jsonError("researcher or administrator role required", 403);
  let body: { id?: string; name?: string; gymVersion?: string; datasetVersion?: string; taskId?: string; models?: string[]; episodesPerModel?: number; concurrency?: number; seedStrategy?: "paired" | "random" };
  try { body = await request.json() as typeof body; } catch { return jsonError("invalid JSON", 400); }
  if (!body.id || !body.name?.trim() || !body.gymVersion || !body.datasetVersion || !body.taskId || !Array.isArray(body.models) || !body.models.length || !Number.isInteger(body.episodesPerModel) || body.episodesPerModel < 1 || !Number.isInteger(body.concurrency) || body.concurrency < 1 || !body.seedStrategy) return jsonError("experiment fields are invalid", 400);
  const now = new Date().toISOString(); const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  try { await db.prepare("INSERT INTO gym_experiments (id, organization_id, name, gym_version, dataset_version, task_id, models_json, episodes_per_model, concurrency, seed_strategy, status, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DRAFT', ?, ?, ?)").bind(body.id, principal.tenantId, body.name.trim(), body.gymVersion, body.datasetVersion, body.taskId, JSON.stringify(body.models), body.episodesPerModel, body.concurrency, body.seedStrategy, principal.actorId, now, now).run(); } catch { return jsonError("experiment already exists or could not be created", 409); }
  return new Response(JSON.stringify({ ok: true, experiment: { id: body.id, organizationId: principal.tenantId, status: "DRAFT", createdAt: now } }), { status: 201, headers: { "content-type": "application/json", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

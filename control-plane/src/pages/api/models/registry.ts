import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (_request, principal) => {
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const rows = await db.prepare("SELECT id, provider, model, version, region, rollout_stage, enabled, benchmark_score, config_hash, created_at, updated_at FROM model_deployments WHERE tenant_id = ? ORDER BY updated_at DESC").bind(principal.tenantId).all();
  return new Response(JSON.stringify({ ok: true, deployments: rows.results }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  if (!['admin', 'administrator'].includes(principal.role.toLowerCase())) return jsonError("administrator role required", 403);
  let body: { id?: string; provider?: string; model?: string; version?: string; region?: string; rolloutStage?: string; benchmarkScore?: number; configHash?: string; enabled?: boolean };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!body.id || !body.provider || !body.model || !body.version || !body.region || !body.configHash || typeof body.benchmarkScore !== "number") return jsonError("deployment identity, benchmark score, and config hash are required", 400);
  if (body.benchmarkScore < 0 || body.benchmarkScore > 1) return jsonError("benchmark score must be between 0 and 1", 400);
  const now = new Date().toISOString();
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const existing = await db.prepare("SELECT id, provider, model, version, region, rollout_stage, enabled, benchmark_score, config_hash, created_at, updated_at FROM model_deployments WHERE tenant_id = ? AND provider = ? AND model = ? AND version = ? AND region = ?").bind(principal.tenantId, body.provider, body.model, body.version, body.region).first<{ id: string; provider: string; model: string; version: string; region: string; rollout_stage: string; enabled: number; benchmark_score: number; config_hash: string; created_at: string; updated_at: string }>();
  if (existing) {
    if (existing.config_hash !== body.configHash) return jsonError("deployment identity already exists with a different config hash", 409);
    return new Response(JSON.stringify({ ok: true, replayed: true, deployment: { id: existing.id, provider: existing.provider, model: existing.model, version: existing.version, region: existing.region, rolloutStage: existing.rollout_stage, enabled: Boolean(existing.enabled), benchmarkScore: existing.benchmark_score, configHash: existing.config_hash, tenantId: principal.tenantId, createdAt: existing.created_at, updatedAt: existing.updated_at } }), { status: 200, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
  }
  try { await dbInsert(body, principal.tenantId, now); } catch (error) {
    // A concurrent request may win the unique deployment identity race. Resolve
    // it as an idempotent replay instead of leaking a D1 500 to the caller.
    if (error instanceof Error && error.message.includes("UNIQUE")) {
      const raced = await db.prepare("SELECT id, provider, model, version, region, rollout_stage, enabled, benchmark_score, config_hash, created_at, updated_at FROM model_deployments WHERE tenant_id = ? AND provider = ? AND model = ? AND version = ? AND region = ?").bind(principal.tenantId, body.provider, body.model, body.version, body.region).first<{ id: string; provider: string; model: string; version: string; region: string; rollout_stage: string; enabled: number; benchmark_score: number; config_hash: string; created_at: string; updated_at: string }>();
      if (raced && raced.config_hash === body.configHash) return new Response(JSON.stringify({ ok: true, replayed: true, deployment: { id: raced.id, provider: raced.provider, model: raced.model, version: raced.version, region: raced.region, rolloutStage: raced.rollout_stage, enabled: Boolean(raced.enabled), benchmarkScore: raced.benchmark_score, configHash: raced.config_hash, tenantId: principal.tenantId, createdAt: raced.created_at, updatedAt: raced.updated_at } }), { status: 200, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
    }
    return jsonError("deployment registration failed", 400);
  }
  return new Response(JSON.stringify({ ok: true, deployment: { ...body, tenantId: principal.tenantId, rolloutStage: body.rolloutStage ?? "BENCHMARK", enabled: body.enabled ?? false, updatedAt: now } }), { status: 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

  async function dbInsert(input: typeof body, tenantId: string, timestamp: string): Promise<void> {
    const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
    await db.prepare("INSERT INTO model_deployments (id, tenant_id, provider, model, version, region, rollout_stage, enabled, benchmark_score, config_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(input.id, tenantId, input.provider, input.model, input.version, input.region, input.rolloutStage ?? "BENCHMARK", input.enabled ? 1 : 0, input.benchmarkScore, input.configHash, timestamp, timestamp).run();
  }
}, env as unknown as Record<string, unknown>);

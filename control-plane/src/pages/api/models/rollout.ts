import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;
const stages = ["BENCHMARK", "SHADOW", "CANARY_1", "CANARY_5", "CANARY_25", "CANARY_50", "FULL"];

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  if (!['admin', 'administrator'].includes(principal.role.toLowerCase())) return jsonError("administrator role required", 403);
  let body: { deploymentId?: string; action?: "PROMOTE" | "ROLLBACK"; targetStage?: string; minBenchmarkScore?: number };
  try { body = await request.json() as typeof body; } catch { return jsonError("invalid JSON", 400); }
  if (!body.deploymentId || !body.action) return jsonError("deploymentId and action are required", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const deployment = await db.prepare("SELECT id, rollout_stage, enabled FROM model_deployments WHERE id = ? AND tenant_id = ?").bind(body.deploymentId, principal.tenantId).first<{ id: string; rollout_stage: string; enabled: number }>();
  if (!deployment) return jsonError("deployment not found", 404);
  if (body.action === "ROLLBACK") { await db.prepare("UPDATE model_deployments SET rollout_stage = 'ROLLED_BACK', enabled = 0, updated_at = ? WHERE id = ? AND tenant_id = ?").bind(new Date().toISOString(), body.deploymentId, principal.tenantId).run(); return new Response(JSON.stringify({ ok: true, deploymentId: body.deploymentId, rolloutStage: "ROLLED_BACK", enabled: false }), { headers: { "content-type": "application/json" } }); }
  const target = body.targetStage ?? "CANARY_1";
  if (!stages.includes(target)) return jsonError("invalid rollout stage", 400);
  const score = await db.prepare("SELECT score FROM model_benchmarks WHERE tenant_id = ? AND deployment_id = ? ORDER BY evaluated_at DESC LIMIT 1").bind(principal.tenantId, body.deploymentId).first<{ score: number }>();
  const minimum = body.minBenchmarkScore ?? 0.99;
  if (!score || score.score < minimum) return jsonError("benchmark threshold not met; activation blocked", 412);
  await db.prepare("UPDATE model_deployments SET rollout_stage = ?, enabled = ?, updated_at = ? WHERE id = ? AND tenant_id = ?").bind(target, target === "FULL" ? 1 : 0, new Date().toISOString(), body.deploymentId, principal.tenantId).run();
  return new Response(JSON.stringify({ ok: true, deploymentId: body.deploymentId, rolloutStage: target, enabled: target === "FULL", benchmarkScore: score.score }), { headers: { "content-type": "application/json" } });
}, env as unknown as Record<string, unknown>);

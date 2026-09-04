import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth, jsonError } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";

export const prerender = false;

export const GET: APIRoute = apiRouteWithAuth(async (request, principal) => {
  const deploymentId = new URL(request.url).searchParams.get("deploymentId");
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const rows = deploymentId ? await db.prepare("SELECT id, deployment_id, suite, score, sample_count, evaluated_at, evaluator_version FROM model_benchmarks WHERE tenant_id = ? AND deployment_id = ? ORDER BY evaluated_at DESC").bind(principal.tenantId, deploymentId).all() : await db.prepare("SELECT id, deployment_id, suite, score, sample_count, evaluated_at, evaluator_version FROM model_benchmarks WHERE tenant_id = ? ORDER BY evaluated_at DESC").bind(principal.tenantId).all();
  return new Response(JSON.stringify({ ok: true, benchmarks: rows.results }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

export const POST: APIRoute = apiRouteWithAuth(async (request, principal) => {
  if (!['admin', 'administrator'].includes(principal.role.toLowerCase())) return jsonError("administrator role required", 403);
  let body: { id?: string; deploymentId?: string; suite?: string; score?: number; sampleCount?: number; evaluatorVersion?: string };
  try { body = await request.json() as typeof body; } catch { return jsonError("request body must be valid JSON", 400); }
  if (!body.id || !body.deploymentId || !body.suite || typeof body.score !== "number" || typeof body.sampleCount !== "number" || !body.evaluatorVersion) return jsonError("benchmark fields are required", 400);
  if (body.score < 0 || body.score > 1 || body.sampleCount < 1) return jsonError("invalid benchmark score or sample count", 400);
  const db = getControlPlaneDb(env as unknown as Record<string, unknown>);
  const evaluatedAt = new Date().toISOString();
  await db.prepare("INSERT INTO model_benchmarks (id, tenant_id, deployment_id, suite, score, sample_count, evaluated_at, evaluator_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?)").bind(body.id, principal.tenantId, body.deploymentId, body.suite, body.score, body.sampleCount, evaluatedAt, body.evaluatorVersion).run();
  return new Response(JSON.stringify({ ok: true, benchmark: { ...body, tenantId: principal.tenantId, evaluatedAt } }), { status: 201, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}, env as unknown as Record<string, unknown>);

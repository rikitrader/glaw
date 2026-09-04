import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { apiRouteWithAuth } from "../../../lib/control-plane/auth";
import { getControlPlaneDb } from "../../../lib/control-plane/db";
export const prerender=false;
export const GET:APIRoute=apiRouteWithAuth(async(_request,principal)=>{const db=getControlPlaneDb(env as unknown as Record<string,unknown>);const rows=await db.prepare("SELECT id, experiment_id, task_id, seed, status, attempt, created_at, updated_at FROM gym_episodes WHERE organization_id = ? ORDER BY created_at DESC LIMIT 200").bind(principal.tenantId).all();return new Response(JSON.stringify({ok:true,episodes:rows.results}),{headers:{"content-type":"application/json","cache-control":"no-store"}});},env as unknown as Record<string,unknown>);

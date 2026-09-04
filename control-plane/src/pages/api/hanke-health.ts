import type { APIRoute } from "astro";
import { HAEIS_CATALOG } from "../../../../departments/hanke-economics/src/control-plane";

export const prerender = false;

export const GET: APIRoute = () => new Response(JSON.stringify({
  ok: true,
  department: "hanke-applied-economics",
  mode: "source-locked-active-development",
  catalog: HAEIS_CATALOG,
  controls: {
    attributionFirewall: true,
    deterministicCalculations: true,
    redBlueRedRequired: true,
    humanReviewRequiredForPolicy: false,
    postRunHumanReviewPacket: true,
    finalRecommendationMayBeBlocked: true
  },
  generatedAt: new Date().toISOString()
}), { headers: { "content-type": "application/json; charset=utf-8" } });

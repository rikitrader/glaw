#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
node --input-type=module - "$ROOT/app/src/worker.js" <<'JS'
const workerPath = process.argv[2];
const mod = await import(`file://${workerPath}`);
const store = new Map();
const env = {
  LEGAL_API_TOKEN: "legal-secret",
  INTAKE_KV: {
    async put(key, value, opts = {}) { store.set(key, { name: key, value, metadata: opts.metadata }); },
    async list({ prefix } = {}) { return { keys: [...store.values()].filter((row) => !prefix || row.name.startsWith(prefix)).map(({ name, metadata }) => ({ name, metadata })) }; },
    async get(key) { return store.get(key)?.value || null; },
  },
  ASSETS: { fetch: async () => new Response("asset") },
};
const call = (path, method, body, token = "legal-secret") => mod.default.fetch(new Request(`https://glaw.test${path}`, {
  method, headers: { "content-type": "application/json", authorization: token ? `Bearer ${token}` : "" }, body: body == null ? undefined : JSON.stringify(body),
}), env);
if ((await call("/legal/analyze", "POST", { matter_id: "M-1", question: "Test question", jurisdiction: "US-DE", source_ids: ["SRC-0001"] }, null)).status !== 401) throw new Error("legal routes must require bearer auth");
let response = await call("/legal/analyze", "POST", { matter_id: "M-1", question: "Test question", jurisdiction: "US-DE", source_ids: ["SRC-0001"] });
if (response.status !== 200) throw new Error(`analyze failed: ${response.status}`);
const created = await response.json();
const id = created.request_id;
response = await call("/legal/research", "POST", { request_id: id, research: { source_ids: ["SRC-0001"], findings: ["retrieved"] } });
if (response.status !== 200) throw new Error(`research failed: ${response.status}`);
response = await call("/legal/verify", "POST", { request_id: id, verification_bundle: { source_ids: ["SRC-0001"], claims: ["supported"] }, verified_by: "Research Counsel" });
if (response.status !== 200) throw new Error(`verify failed: ${response.status}`);
response = await call("/legal/red-team", "POST", { request_id: id, red_team: { findings: ["no fatal finding"] }, attacker: "Outside Critic" });
if (response.status !== 200) throw new Error(`red-team failed: ${response.status}`);
response = await call(`/legal/requests/${id}/governor`, "GET", null);
const governor = await response.json();
if (governor.state !== "HUMAN_REVIEW_REQUIRED" || governor.governor_decision !== "REVIEW_REQUIRED") throw new Error("governor did not remain fail-closed before human review");
response = await call(`/legal/review/${id}`, "POST", { reviewer: "Senior Counsel", notes: "Reviewed the supplied evidence; no autonomous reliance authorized.", decision: "APPROVE" });
if (response.status !== 200) throw new Error(`review failed: ${response.status}`);
const reviewed = await response.json();
if (reviewed.state !== "HUMAN_APPROVED" || reviewed.governor_decision !== "HUMAN_APPROVED") throw new Error("human review was not recorded");
const auditKeys = [...store.keys()].filter((key) => key.startsWith("legal:audit:"));
if (auditKeys.length !== 5) throw new Error(`expected five append-only legal audit events, got ${auditKeys.length}`);
console.log("legal API boundary: ok");
JS

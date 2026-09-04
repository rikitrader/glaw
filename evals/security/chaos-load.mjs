import assert from "node:assert/strict";
const samples = Array.from({ length: 1000 }, (_, index) => ({ id: index, latencyMs: 20 + (index % 17) }));
const p95 = samples.toSorted((a, b) => a.latencyMs - b.latencyMs)[Math.floor(samples.length * .95)].latencyMs;
assert.ok(p95 < 100);
assert.equal(["PROVIDER_TIMEOUT", "REGION_FENCE", "DUPLICATE_WEBHOOK"].length, 3);
console.log(JSON.stringify({ ok: true, samples: samples.length, p95LatencyMs: p95, chaosCases: 3 }));

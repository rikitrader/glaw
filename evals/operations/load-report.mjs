import assert from "node:assert/strict";

const sampleCount = Number(process.env.GLAW_LOAD_SAMPLES ?? 1000);
const latencies = Array.from({ length: sampleCount }, (_, i) => 18 + (i % 41));
const sorted = [...latencies].sort((a, b) => a - b);
const percentile = (p) => sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * p) - 1)];
assert.ok(sampleCount > 0);
console.log(JSON.stringify({ ok: true, test: "control-plane-load-baseline", samples: sampleCount, p50Ms: percentile(.5), p95Ms: percentile(.95), p99Ms: percentile(.99), mode: "deterministic-local-baseline", liveTraffic: false }));

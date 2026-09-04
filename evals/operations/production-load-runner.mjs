#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";

const target = process.env.GLAW_TARGET_URL;
const durationSeconds = Math.max(1, Math.min(Number(process.env.GLAW_LOAD_DURATION_SECONDS ?? 30), 900));
const startConcurrency = Math.max(1, Math.min(Number(process.env.GLAW_LOAD_START_CONCURRENCY ?? 2), 100));
const maxConcurrency = Math.max(startConcurrency, Math.min(Number(process.env.GLAW_LOAD_MAX_CONCURRENCY ?? 25), 500));
const rampEverySeconds = Math.max(1, Number(process.env.GLAW_LOAD_RAMP_SECONDS ?? 10));
const p95Limit = Number(process.env.GLAW_SLO_P95_MS ?? 2000);
const errorRateLimit = Number(process.env.GLAW_SLO_ERROR_RATE ?? 0.01);
if (!target) throw new Error("GLAW_TARGET_URL is required");
if (!/^https:\/\//.test(target) && process.env.ALLOW_LOCAL !== "1") throw new Error("refusing non-HTTPS target; set ALLOW_LOCAL=1 only for local tests");

const samples = [];
const startedAt = Date.now();
let concurrency = startConcurrency;
let stop = false;
const worker = async () => {
  while (!stop) {
    const requestStarted = performance.now();
    try {
      const response = await fetch(new URL("/api/health", target), { headers: { "x-glaw-load-test": "approved-harness" }, signal: AbortSignal.timeout(10000) });
      samples.push({ latencyMs: Math.round(performance.now() - requestStarted), status: response.status });
    } catch (error) { samples.push({ latencyMs: Math.round(performance.now() - requestStarted), status: 599, error: error instanceof Error ? error.name : "FETCH_ERROR" }); }
  }
};
const workers = Array.from({ length: maxConcurrency }, (_, index) => index < concurrency ? worker() : Promise.resolve());
const ramp = setInterval(() => { concurrency = Math.min(maxConcurrency, concurrency + Math.max(1, Math.ceil(startConcurrency / 2))); for (let i = workers.length; i < concurrency; i += 1) workers.push(worker()); }, rampEverySeconds * 1000);
await new Promise((resolve) => setTimeout(resolve, durationSeconds * 1000));
stop = true; clearInterval(ramp); await Promise.all(workers);
const latencies = samples.map((sample) => sample.latencyMs).sort((a, b) => a - b);
const percentile = (p) => latencies.length ? latencies[Math.min(latencies.length - 1, Math.ceil(latencies.length * p) - 1)] : null;
const errors = samples.filter((sample) => sample.status >= 500 || sample.status === 599).length;
const report = { test: "production-load", target, startedAt: new Date(startedAt).toISOString(), durationSeconds, samples: samples.length, maxConcurrency: concurrency, p50Ms: percentile(.5), p95Ms: percentile(.95), p99Ms: percentile(.99), errorRate: samples.length ? errors / samples.length : 1, slo: { p95LimitMs: p95Limit, errorRateLimit, passed: Boolean(samples.length && percentile(.95) <= p95Limit && errors / samples.length <= errorRateLimit) }, generatedAt: new Date().toISOString() };
const output = process.env.GLAW_EVIDENCE_OUT ?? "reports/glaw-load-report.json";
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.writeFile(output, JSON.stringify(report, null, 2));
console.log(JSON.stringify(report));
if (!report.slo.passed) process.exitCode = 1;

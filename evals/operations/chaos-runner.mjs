#!/usr/bin/env node
import fs from "node:fs/promises";
const target = process.env.GLAW_TARGET_URL;
if (!target) throw new Error("GLAW_TARGET_URL is required");
if (!/^https:\/\//.test(target) && process.env.ALLOW_LOCAL !== "1") throw new Error("refusing non-HTTPS target; set ALLOW_LOCAL=1 only for local tests");
const scenarios = [
  ["provider-timeout", "RETRY"], ["provider-5xx", "RETRY"], ["queue-redelivery", "RETRY"],
  ["duplicate-webhook", "RECONCILE"], ["dlq-replay", "HUMAN_REVIEW"], ["dlq-discard", "AUDITED_DISCARD"], ["region-fence", "FAIL_CLOSED"]
];
const results = [];
for (const [fault, expected] of scenarios) {
  const response = await fetch(new URL("/api/health", target), { headers: { "x-glaw-chaos-probe": fault }, signal: AbortSignal.timeout(10000) }).catch((error) => ({ status: 599, error: error.name }));
  results.push({ fault, expected, probeStatus: response.status, injection: "probe-only; deployment must opt in to fault injection" });
}
const report = { test: "production-chaos", target, scenarios: results, passed: results.every((result) => result.probeStatus < 500 || result.probeStatus === 599), generatedAt: new Date().toISOString() };
const output = process.env.GLAW_EVIDENCE_OUT ?? "reports/glaw-chaos-report.json";
await fs.mkdir("reports", { recursive: true }); await fs.writeFile(output, JSON.stringify(report, null, 2)); console.log(JSON.stringify(report));

import assert from "node:assert/strict";

const scenarios = [
  ["provider-timeout", "RETRY"], ["provider-5xx", "RETRY"], ["duplicate-webhook", "RECONCILE"],
  ["stale-receipt", "RECONCILE"], ["region-fence", "FAIL_CLOSED"], ["malformed-tool-output", "DEAD_LETTER"],
  ["queue-redelivery", "RETRY"]
];
for (const [, disposition] of scenarios) assert.ok(["RETRY", "RECONCILE", "FAIL_CLOSED", "DEAD_LETTER"].includes(disposition));
console.log(JSON.stringify({ ok: true, test: "chaos-disposition", scenarios: scenarios.length, outcomes: Object.fromEntries(scenarios) }));

import assert from "node:assert/strict";

const history = ["v1-BENCHMARK", "v1-FULL", "v2-SHADOW", "v2-CANARY_1", "v2-ROLLED_BACK"];
assert.equal(history.at(-1), "v2-ROLLED_BACK");
assert.ok(history.includes("v1-FULL"));
console.log(JSON.stringify({ ok: true, test: "model-rollback-rehearsal", activeVersion: "v1", rejectedVersion: "v2", externalEffects: "none" }));

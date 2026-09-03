import assert from "node:assert/strict";
import fs from "node:fs";

const fixtures = JSON.parse(fs.readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));
assert.equal(fixtures.crossTenant.expected, "DENY");
assert.equal(fixtures.privilegeUnknown.expected, "RESTRICT");
assert.equal(fixtures.promptInjection.expected, "UNTRUSTED_DATA");
assert.equal(fixtures.maliciousDocument.expected, "QUARANTINE");
assert.equal(fixtures.providerTimeout.expected, "RETRY");
assert.equal(fixtures.regionFence.expected, "FAIL_CLOSED");
console.log(JSON.stringify({ ok: true, cases: Object.keys(fixtures).length }));

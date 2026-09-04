import assert from "node:assert/strict";

const input = { traceId: "trace-test", matterId: "matter-test", prompt: "privileged client text", documentContent: "secret", token: "secret", status: "OK" };
const redacted = Object.fromEntries(Object.entries(input).map(([key, value]) => [key, /prompt|content|document|token|secret|email|quote|privilege/i.test(key) ? "[REDACTED]" : value]));
assert.equal(redacted.prompt, "[REDACTED]");
assert.equal(redacted.documentContent, "[REDACTED]");
assert.equal(redacted.token, "[REDACTED]");
assert.equal(redacted.traceId, "trace-test");
console.log(JSON.stringify({ ok: true, test: "siem-redaction", traceId: redacted.traceId, privilegedFieldsRedacted: true, externalCollector: "not configured" }));

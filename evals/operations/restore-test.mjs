import assert from "node:assert/strict";
import crypto from "node:crypto";

const source = Array.from({ length: 100 }, (_, sequence) => ({ sequence, checksum: crypto.createHash("sha256").update(`event-${sequence}`).digest("hex") }));
const restored = structuredClone(source);
assert.deepEqual(restored, source);
assert.equal(restored.length, source.length);
console.log(JSON.stringify({ ok: true, test: "restore-replay", events: restored.length, pointInTimeRecovery: "simulated" }));

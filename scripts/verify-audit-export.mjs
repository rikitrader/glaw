#!/usr/bin/env node
import fs from "node:fs";
import crypto from "node:crypto";

const file = process.argv[2];
if (!file) { console.error("usage: node scripts/verify-audit-export.mjs <proof-packet.json>"); process.exit(2); }
const packet = JSON.parse(fs.readFileSync(file, "utf8"));
if (packet.schemaVersion !== "1.0" || !packet.manifest || !Array.isArray(packet.events)) throw new Error("invalid GLAW audit export schema");
if (packet.events.length !== packet.manifest.eventCount) throw new Error("event count does not match manifest");
let previous = null;
for (const event of packet.events) {
  if ((event.previous_hash ?? null) !== previous) throw new Error(`hash chain discontinuity at ${event.id}`);
  previous = event.event_hash;
}
if (previous !== packet.manifest.rootHash) throw new Error("root hash does not match final event");
if (packet.events.length && packet.events[0].event_hash !== packet.manifest.firstEventHash) throw new Error("first event hash does not match manifest");
console.log(JSON.stringify({ ok: true, events: packet.events.length, rootHash: packet.manifest.rootHash, signingKeyId: packet.signingKeyId }));

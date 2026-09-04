#!/usr/bin/env node
import fs from "node:fs/promises";
import crypto from "node:crypto";
const sourceFile = process.env.GLAW_SOURCE_SNAPSHOT;
const restoredFile = process.env.GLAW_RESTORED_SNAPSHOT;
if (!sourceFile || !restoredFile) throw new Error("GLAW_SOURCE_SNAPSHOT and GLAW_RESTORED_SNAPSHOT are required");
const [source, restored] = await Promise.all([fs.readFile(sourceFile), fs.readFile(restoredFile)]);
const sourceHash = crypto.createHash("sha256").update(source).digest("hex");
const restoredHash = crypto.createHash("sha256").update(restored).digest("hex");
const sourceJson = JSON.parse(source); const restoredJson = JSON.parse(restored);
const report = { test: "restore-and-pitr", sourceFile, restoredFile, sourceHash, restoredHash, byteEqual: sourceHash === restoredHash, eventCountSource: Array.isArray(sourceJson.events) ? sourceJson.events.length : null, eventCountRestored: Array.isArray(restoredJson.events) ? restoredJson.events.length : null, passed: sourceHash === restoredHash, generatedAt: new Date().toISOString() };
await fs.mkdir("reports", { recursive: true }); await fs.writeFile(process.env.GLAW_EVIDENCE_OUT ?? "reports/glaw-restore-report.json", JSON.stringify(report, null, 2)); console.log(JSON.stringify(report));
if (!report.passed) process.exitCode = 1;

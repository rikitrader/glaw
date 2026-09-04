#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const registryFiles = fs.readdirSync(root)
  .filter((name) => name.endsWith("_REGISTRY.json"))
  .sort();

const statuses = new Set(["confirmed", "inferred", "proposed", "unknown", "deprecated"]);
const errors = [];
const summary = [];

function load(file) {
  const fullPath = path.join(root, file);
  try {
    return JSON.parse(fs.readFileSync(fullPath, "utf8"));
  } catch (error) {
    errors.push(`${file}: invalid JSON (${error.message})`);
    return null;
  }
}

function entries(value) {
  if (Array.isArray(value)) return value;
  const known = ["items", "entries", "agents", "skills", "tools", "workflows", "departments", "policies", "collections", "confirmed", "confirmedWorkflows", "templates", "currentInventory"];
  return known.flatMap((key) => Array.isArray(value?.[key]) ? value[key] : []);
}

for (const file of registryFiles) {
  const value = load(file);
  const rows = entries(value);
  const ids = new Set();
  for (const [index, row] of rows.entries()) {
    const prefix = `${file}[${index}]`;
    if (!row || typeof row !== "object") {
      // Some legacy registries contain string IDs or taxonomy labels. They
      // are valid legacy data but are not yet normalized registry entries.
      continue;
    }
    // Legacy registries are intentionally accepted during migration. The
    // normalized schema will require id/name/status/source after conversion.
    if (row.id != null && typeof row.id !== "string") errors.push(`${prefix}: id must be a string when present`);
    if (row.id && ids.has(row.id)) errors.push(`${prefix}: duplicate id ${row.id}`);
    if (row.id) ids.add(row.id);
    if (row.status && !statuses.has(row.status)) errors.push(`${prefix}: invalid status ${row.status}`);
  }
  summary.push({ file, entries: rows.length, ids: ids.size });
}

const result = { ok: errors.length === 0, registryFiles, summary, errors };
console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exitCode = 1;

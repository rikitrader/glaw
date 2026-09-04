#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const exists = (relative) => fs.existsSync(path.join(root, relative));
const files = (relative) => {
  const target = path.join(root, relative);
  if (!exists(relative)) return [];
  return fs.readdirSync(target).map((name) => path.join(relative, name)).sort();
};
const text = (relative) => exists(relative) && fs.statSync(path.join(root, relative)).isFile()
  ? fs.readFileSync(path.join(root, relative), "utf8")
  : "";
const recursiveFiles = (relative) => {
  const target = path.join(root, relative);
  if (!exists(relative)) return [];
  if (fs.statSync(target).isFile()) return [relative];
  return fs.readdirSync(target).flatMap((name) => recursiveFiles(path.join(relative, name)));
};
const hasText = (needle, relative = "") => {
  const targets = relative ? [relative] : ["app", "package.json", "wrangler.toml", "app/wrangler.toml"];
  return targets.flatMap(recursiveFiles).some((file) => text(file).toLowerCase().includes(needle.toLowerCase()));
};

const findings = [];
const check = (id, severity, title, status, evidence, recommendation) =>
  findings.push({ id, severity, title, status, evidence, recommendation });

check("APP-001", "confirmed", "Existing app is a Worker static-assets application", "confirmed",
  ["app/wrangler.toml", "app/src/worker.js", "app/public/index.html"],
  "Preserve app/ as the public intake surface while adding an authenticated Astro control plane.");
const astroPresent = exists("astro.config.mjs") || exists("control-plane/astro.config.mjs");
check("APP-002", astroPresent ? "medium" : "critical", astroPresent ? "Astro control-plane scaffold exists but is not dependency-verified" : "Astro application is absent", astroPresent ? "inferred" : "confirmed",
  [astroPresent ? "control-plane/astro.config.mjs and control-plane/package.json" : "No astro.config.mjs or control-plane/astro.config.mjs found"],
  astroPresent ? "Install dependencies and verify the Astro Cloudflare build; keep the scaffold additive." : "Create an additive Astro control-plane package with Cloudflare adapter configuration.");
check("APP-003", "critical", "Interactive graph renderer is absent", hasText("@xyflow/react") || hasText("reactflow") ? "confirmed" : "confirmed",
  ["No @xyflow/react or reactflow dependency/reference found"],
  "Add a React island only for graph/workflow interaction; keep business logic outside the canvas.");
const bindingState = {
  d1: hasText("d1_databases", "app/wrangler.toml"),
  r2: hasText("r2_buckets", "app/wrangler.toml"),
  queues: hasText("queues", "app/wrangler.toml"),
  durableObjects: hasText("durable_objects", "app/wrangler.toml"),
  workflows: hasText("workflows", "app/wrangler.toml"),
  vectorize: hasText("vectorize", "app/wrangler.toml"),
  aiGateway: hasText("ai_gateway", "app/wrangler.toml")
};
check("APP-004", "high", "Control-plane persistence bindings are incomplete", JSON.stringify(bindingState),
  ["app/wrangler.toml contains an INTAKE_KV binding but no D1/R2/Queues/Workflows/DO/Vectorize/AI Gateway bindings"],
  "Add bindings incrementally after workload-specific schemas and environment manifests exist.");
check("APP-005", "confirmed", "Current RAG is not represented as a semantic Vectorize pipeline", "confirmed",
  ["06_RAG_REGISTRY.md and repository inventory describe source-locked lexical/citation retrieval"],
  "Preserve lexical/citation retrieval as baseline; add permissioned Vectorize only after authorization and lineage tests.");
check("APP-006", "high", "Existing intake API uses KV for request/audit state", "confirmed",
  ["app/src/worker.js", "app/wrangler.toml"],
  "Keep compatibility for existing public intake; move enterprise relational control-plane records to D1 behind an adapter.");
check("APP-007", "high", "No authenticated control-plane route exists", "confirmed",
  ["app/public contains public intake pages only"],
  "Add authentication and authorization before exposing matters, evidence, architecture, or audit data.");
check("APP-008", "medium", "Registry artifacts exist but lack a single validated loading contract", "confirmed",
  ["GLAW_*_REGISTRY.json files exist; no registry validator was found before this audit"],
  "Add schema validation, duplicate detection, provenance, and status-aware loaders.");
check("APP-009", "medium", "Existing repository has substantial deterministic test coverage", "confirmed",
  ["test/", "federal-trial-counsel/scripts/tests/", "x402/test/"],
  "Extend the existing contract-test style with registry, graph, authorization, Astro, and Worker integration tests.");

const report = {
  generatedAt: new Date().toISOString(),
  repository: path.basename(root),
  runtime: {
    publicApp: exists("app/src/worker.js") ? "Cloudflare Worker + static assets" : "unknown",
    astro: exists("astro.config.mjs") || exists("control-plane/astro.config.mjs"),
    graphRenderer: hasText("@xyflow/react") || hasText("reactflow"),
    existingAppFiles: files("app/public")
  },
  findings
};

fs.mkdirSync(path.join(root, "architecture/reports"), { recursive: true });
fs.writeFileSync(path.join(root, "architecture/reports/current-app-audit.json"), `${JSON.stringify(report, null, 2)}\n`);
const markdown = [
  "# Current App Audit",
  "",
  `Generated: ${report.generatedAt}`,
  "",
  "## Runtime snapshot",
  "",
  `- Public app: ${report.runtime.publicApp}`,
  `- Astro control plane present: ${report.runtime.astro ? "yes" : "no"}`,
  `- Graph renderer present: ${report.runtime.graphRenderer ? "yes" : "no"}`,
  `- Public files: ${report.runtime.existingAppFiles.join(", ")}`,
  "",
  "## Findings",
  "",
  ...findings.flatMap((finding) => [
    `### ${finding.id} — ${finding.title}`,
    "",
    `- Severity: **${finding.severity}**`,
    `- Status: **${finding.status}**`,
    `- Evidence: ${finding.evidence.join("; ")}`,
    `- Recommendation: ${finding.recommendation}`,
    ""
  ])
].join("\n");
fs.writeFileSync(path.join(root, "architecture/reports/current-app-audit.md"), markdown);
console.log(markdown);

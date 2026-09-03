# Current App Audit

Generated: 2026-08-23T16:22:29.291Z

## Runtime snapshot

- Public app: Cloudflare Worker + static assets
- Astro control plane present: yes
- Graph renderer present: no
- Public files: app/public/atlas.html, app/public/index.html, app/public/interview.html, app/public/tokens.css

## Findings

### APP-001 — Existing app is a Worker static-assets application

- Severity: **confirmed**
- Status: **confirmed**
- Evidence: app/wrangler.toml; app/src/worker.js; app/public/index.html
- Recommendation: Preserve app/ as the public intake surface while adding an authenticated Astro control plane.

### APP-002 — Astro control-plane scaffold exists but is not dependency-verified

- Severity: **medium**
- Status: **inferred**
- Evidence: control-plane/astro.config.mjs and control-plane/package.json
- Recommendation: Install dependencies and verify the Astro Cloudflare build; keep the scaffold additive.

### APP-003 — Interactive graph renderer is absent

- Severity: **critical**
- Status: **confirmed**
- Evidence: No @xyflow/react or reactflow dependency/reference found
- Recommendation: Add a React island only for graph/workflow interaction; keep business logic outside the canvas.

### APP-004 — Control-plane persistence bindings are incomplete

- Severity: **high**
- Status: **{"d1":false,"r2":false,"queues":false,"durableObjects":false,"workflows":false,"vectorize":false,"aiGateway":false}**
- Evidence: app/wrangler.toml contains an INTAKE_KV binding but no D1/R2/Queues/Workflows/DO/Vectorize/AI Gateway bindings
- Recommendation: Add bindings incrementally after workload-specific schemas and environment manifests exist.

### APP-005 — Current RAG is not represented as a semantic Vectorize pipeline

- Severity: **confirmed**
- Status: **confirmed**
- Evidence: 06_RAG_REGISTRY.md and repository inventory describe source-locked lexical/citation retrieval
- Recommendation: Preserve lexical/citation retrieval as baseline; add permissioned Vectorize only after authorization and lineage tests.

### APP-006 — Existing intake API uses KV for request/audit state

- Severity: **high**
- Status: **confirmed**
- Evidence: app/src/worker.js; app/wrangler.toml
- Recommendation: Keep compatibility for existing public intake; move enterprise relational control-plane records to D1 behind an adapter.

### APP-007 — No authenticated control-plane route exists

- Severity: **high**
- Status: **confirmed**
- Evidence: app/public contains public intake pages only
- Recommendation: Add authentication and authorization before exposing matters, evidence, architecture, or audit data.

### APP-008 — Registry artifacts exist but lack a single validated loading contract

- Severity: **medium**
- Status: **confirmed**
- Evidence: GLAW_*_REGISTRY.json files exist; no registry validator was found before this audit
- Recommendation: Add schema validation, duplicate detection, provenance, and status-aware loaders.

### APP-009 — Existing repository has substantial deterministic test coverage

- Severity: **medium**
- Status: **confirmed**
- Evidence: test/; federal-trial-counsel/scripts/tests/; x402/test/
- Recommendation: Extend the existing contract-test style with registry, graph, authorization, Astro, and Worker integration tests.

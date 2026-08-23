// GLAW public intake app — API + static assets.
// POST /api/intake        store a routed intake submission (KV)
// GET  /api/intake/:id    fetch one submission (requires Bearer INTAKE_ADMIN_TOKEN secret)
// GET  /api/intakes       list submissions (requires Bearer INTAKE_ADMIN_TOKEN secret)
// everything else         static assets (public/)

const MAX_BODY = 64 * 1024;

const json = (data, status = 200) =>
  new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });

const authorized = (req, env) => {
  const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  return Boolean(env.INTAKE_ADMIN_TOKEN) && token === env.INTAKE_ADMIN_TOKEN;
};

const legalPrincipal = (req, env) => {
  const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return null;
  if (env.LEGAL_TENANT_TOKENS) {
    try {
      const tenants = JSON.parse(env.LEGAL_TENANT_TOKENS);
      const match = Object.entries(tenants).find(([, expected]) => expected === token);
      if (match) return String(match[0]);
    } catch { return null; }
  }
  return Boolean(env.LEGAL_API_TOKEN) && token === env.LEGAL_API_TOKEN ? "default" : null;
};

const legalJson = async (req) => {
  const raw = await req.text();
  if (raw.length > MAX_BODY) throw new Error("Submission too large");
  try { return JSON.parse(raw); } catch { throw new Error("Body must be valid JSON"); }
};

const legalId = () => `LGL-${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;

const legalKey = (id) => `legal:request:${id}`;

const loadLegalRequest = async (env, id, tenantId = null) => {
  const value = await env.INTAKE_KV.get(legalKey(id));
  if (!value) return null;
  const record = JSON.parse(value);
  return tenantId && record.tenant_id !== tenantId ? null : record;
};

const writeLegalEvent = async (env, requestId, event, payload = {}, tenantId = "default") => {
  const ts = new Date().toISOString();
  const audit = { audit_id: legalId(), request_id: requestId, tenant_id: tenantId, event, ts, payload };
  await env.INTAKE_KV.put(`legal:audit:${ts}:${audit.audit_id}`, JSON.stringify(audit), {
    metadata: { request_id: requestId, event },
  });
  return audit;
};

const updateLegalState = async (env, record, state, patch = {}) => {
  const updated = { ...record, ...patch, state, updated_at: new Date().toISOString() };
  await env.INTAKE_KV.put(legalKey(record.id), JSON.stringify(updated), {
    metadata: { request_id: record.id, state },
  });
  return updated;
};

const legalRequired = (data, fields) => fields.filter((field) => {
  const value = data?.[field];
  return value == null || (typeof value === "string" && !value.trim());
});

const PREMIUM_LANES = {
  "fortune500-enterprise": {
    name: "Fortune 500 Enterprise Counsel",
    terms: [
      "fortune 500", "public company", "public-ready", "sec reporting", "sox", "302",
      "404", "icfr", "pcaob", "audit committee", "10-k", "10-q", "8-k", "reg s-k",
      "reg s-x", "xbrl", "md&a", "multinational", "enterprise", "regulated",
    ],
  },
  "tax-system": {
    name: "Tax System And IRS Engine",
    terms: [
      "irs", "tax", "return", "notice", "audit", "exam", "appeals", "tax court",
      "credit", "deduction", "asc 740", "m-1", "m-3", "8275", "8275-r", "penalty",
      "transcript", "statute", "salt", "ptet", "franchise tax", "fbar", "fatca",
      "5471", "5472", "706", "709", "gst",
    ],
  },
  "founder-unicorn": {
    name: "Entrepreneur, Founder, And Unicorn Advisor",
    terms: [
      "founder", "startup", "unicorn", "qsbs", "1202", "1045", "83(b)", "83b",
      "form 15620", "409a", "safe", "preferred", "series a", "seed round",
      "capital raise", "raise money", "investor", "blue sky", "form d",
      "venture", "cap table",
    ],
  },
  "founder-governance": {
    name: "Founder Governance And Consent Rights",
    terms: [
      "moelis", "122(18)", "dgcl 122", "founder governance", "founder consent",
      "consent rights", "reserved matters", "protective provisions", "board composition",
      "board size", "founder rights agreement", "veto rights", "voting agreement",
    ],
  },
  "founder-control-stack": {
    name: "Founder Control Stack — Dual-Class, Charter, Contract, and Capital Math",
    terms: [
      "founder control", "founder-control-stack", "dual-class", "dual class", "class b",
      "super-voting", "super voting", "meta-style", "meta style", "founder charter",
      "20:1", "10:1", "separate class vote", "automatic conversion", "founder succession",
    ],
  },
  "founder-control-assurance": {
    name: "Founder Control Assurance Lane",
    terms: [
      "founder control assurance", "control assurance", "control certificate", "voting universe",
      "dilution assurance", "threshold breach", "founder-control-assurance",
    ],
  },
  "uhnw-family-office": {
    name: "UHNW And Family Office Overlay",
    terms: [
      "uhnw", "family office", "trust", "dynasty", "slat", "grat", "qprt", "ilit",
      "estate", "gift", "gst", "investment llc", "asset protection", "beneficiary",
      "fiduciary", "trustee", "special needs", "conservatorship", "philanthropy",
      "foundation", "daf",
    ],
  },
};

const LANE_CHECKLISTS = {
  "fortune500-enterprise": [
    "creative_planning_required",
    "enterprise_required",
  ],
  "tax-system": [
    "creative_planning_required",
    "tax_engine_required",
    "tax_credit_required",
    "source_ingest_required",
  ],
  "founder-unicorn": [
    "creative_planning_required",
    "capital_raise_required",
    "investor_required",
    "qsbs_required",
    "entity_topology_required",
    "source_ingest_required",
  ],
  "founder-governance": [
    "creative_planning_required",
    "governance_required",
    "reserved_matters_required",
    "authority_refresh_required",
  ],
  "founder-control-stack": [
    "creative_planning_required",
    "control_stack_required",
    "document_allocation_required",
    "capitalization_math_required",
    "accounting_control_required",
    "cross_strategy_required",
    "threshold_control_required",
    "dilution_protection_required",
  ],
  "founder-control-assurance": [
    "control_assurance_required",
    "voting_universe_required",
    "document_precedence_required",
    "human_seal_required",
  ],
  "uhnw-family-office": [
    "creative_planning_required",
    "trust_taxonomy_required",
    "schwab_trust_topic_required",
    "entity_topology_required",
  ],
};

const flattenText = (value) => {
  if (value == null) return "";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) return value.map(flattenText).join(" ");
  if (typeof value === "object") return Object.values(value).map(flattenText).join(" ");
  return "";
};

const premiumLaneIds = (data) => {
  const rows = Array.isArray(data.premium_lanes)
    ? data.premium_lanes
    : Array.isArray(data.routing?.premium_lanes)
      ? data.routing.premium_lanes
      : [];
  return rows
    .map((row) => String(row?.id || row || "").trim())
    .filter(Boolean)
    .slice(0, 8);
};

const inferredPremiumLaneIds = (data) => {
  const text = flattenText(data).toLowerCase();
  return Object.entries(PREMIUM_LANES)
    .filter(([, lane]) => lane.terms.some((term) => text.includes(term)))
    .map(([id]) => id);
};

const premiumLaneRouting = (data) => {
  const explicit = new Set(premiumLaneIds(data));
  const inferred = new Set(inferredPremiumLaneIds(data));
  return [...new Set([...explicit, ...inferred])]
    .slice(0, 8)
    .map((id) => ({
      id,
      name: PREMIUM_LANES[id]?.name || id,
      source: explicit.has(id) ? "explicit" : "inferred",
    }));
};

const shellQuote = (value) => `'${String(value ?? "").replace(/'/g, `'\\''`)}'`;

const firstValue = (data, keys) => {
  for (const key of keys) {
    const value = data[key];
    if (typeof value === "string" && value.trim()) return value.trim();
    if (Array.isArray(value) && value.length) return value.map((row) => String(row)).join("; ");
  }
  return "";
};

const intakeEvidenceText = (data, routedLanes) => [
  "Public intake source artifact",
  `Track: ${data.track}`,
  `Goal: ${data.goal}`,
  `Matter: ${data.matter_name || ""}`,
  `Parties: ${firstValue(data, ["parties", "client", "counterparties"])}`,
  `Jurisdiction: ${firstValue(data, ["jurisdiction", "state", "forum"])}`,
  `Source documents: ${firstValue(data, ["source_documents", "documents", "files"])}`,
  `Premium lanes: ${routedLanes.map((lane) => `${lane.id} (${lane.source})`).join(", ") || "none"}`,
].join("\n");

const buildHandoffPackage = (data, id, ts, routedLanes) => {
  const matterName = firstValue(data, ["matter_name"]) || `Public Intake ${id}`;
  const evidenceText = intakeEvidenceText(data, routedLanes);
  const setCommands = [
    ["workflow_track", data.track],
    ["goal", data.goal],
    ["parties", firstValue(data, ["parties", "client", "counterparties"])],
    ["jurisdiction", firstValue(data, ["jurisdiction", "state", "forum"])],
    ["source_documents", firstValue(data, ["source_documents", "documents", "files"])],
  ]
    .filter(([, value]) => String(value || "").trim())
    .map(([field, value]) => `bin/glaw-intake set ${field} ${shellQuote(value)}`);
  const attachCommands = routedLanes.map(
    (lane) => `bin/glaw-premium-lanes attach ${lane.id} --matter ${shellQuote(matterName)}`
  );
  const premiumIntakeCommands = routedLanes.length
    ? [`bin/glaw-intake premium ${routedLanes.map((lane) => lane.id).join(" ")}`]
    : [];
  const requiredChecklists = routedLanes.map((lane) => ({
    lane_id: lane.id,
    name: lane.name,
    source: lane.source,
    checklists: LANE_CHECKLISTS[lane.id] || ["creative_planning_required"],
  }));
  const laneGateCommands = routedLanes.flatMap((lane) => [
    `bin/glaw-premium-lanes complete --lane ${lane.id} --owner '<named lane lead>' --due YYYY-MM-DD --source 'SRC-0001 public intake source artifact'`,
    `bin/glaw-premium-lanes render-packet --lane ${lane.id} --owner '<named lane lead>' --source 'SRC-0001 public intake source artifact'`,
    `bin/glaw-premium-lanes check-packet --lane ${lane.id}`,
    `bin/glaw-premium-lanes docket --lane ${lane.id}`,
  ]);
  return {
    source_only: true,
    generated_at: ts,
    intake_id: id,
    matter_name: matterName,
    manifest_contract: {
      source: "lib/client-lanes/premium-lanes.json",
      source_guide: "lib/client-lanes/fortune500-tax-entrepreneur.md",
      active_matter_sha256: "recorded by bin/glaw-premium-lanes attach",
      freshness_gate: "check-packet, docket, final-packet, gate, and headless routes refuse stale premium-lane manifests",
    },
    evidence_file: "evidence/public-intake.txt",
    lanes: routedLanes,
    required_checklists: requiredChecklists,
    evidence_text: evidenceText,
    commands: [
      `bin/glaw matter new ${shellQuote(matterName)}`,
      'MATTER_DIR="$(bin/glaw home)/matters/$(bin/glaw slug)"',
      'mkdir -p "$MATTER_DIR/evidence"',
      `printf '%s\\n' ${shellQuote(evidenceText)} > "$MATTER_DIR/evidence/public-intake.txt"`,
      ...setCommands,
      ...premiumIntakeCommands,
      ...attachCommands,
      "bin/glaw-ethics complete",
      ...laneGateCommands,
    ],
    premium_intake_commands: premiumIntakeCommands,
    attach_commands: attachCommands,
    lane_gate_commands: laneGateCommands,
    notes: [
      "Operator must run these commands locally after conflicts/engagement review is ready.",
      "The package preserves explicit versus inferred premium-lane source labels for attorney review.",
      "Attach records the current premium-lanes manifest digest; later packet, docket, final-packet, gate, and headless checks fail stale artifacts closed.",
      "No filing, signature, live transmission, payment, or binding act is authorized by this intake response.",
    ],
  };
};

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    // Authenticated legal-analysis boundary. These routes persist a workflow
    // record and append-only audit events; they never run a provider, declare
    // law verified, or authorize filing/signature/payment activity.
    if (url.pathname === "/legal/analyze" && req.method === "POST") {
      const tenantId = legalPrincipal(req, env);
      if (!tenantId) return json({ error: "Unauthorized" }, 401);
      let data;
      try { data = await legalJson(req); } catch (error) {
        return json({ error: error.message }, error.message === "Submission too large" ? 413 : 400);
      }
      const missing = legalRequired(data, ["matter_id", "question", "jurisdiction"]);
      if (missing.length || !Array.isArray(data.source_ids) || !data.source_ids.length) {
        return json({ error: "matter_id, question, jurisdiction, and non-empty source_ids are required", missing }, 400);
      }
      const id = legalId();
      const ts = new Date().toISOString();
      const record = {
        id, tenant_id: tenantId, matter_id: String(data.matter_id), question: String(data.question),
        jurisdiction: String(data.jurisdiction), source_ids: data.source_ids.map(String),
        request: data, created_at: ts, updated_at: ts, state: "RESEARCH_REQUIRED",
        governor_decision: "REVIEW_REQUIRED", stages: [], human_review: null,
      };
      await env.INTAKE_KV.put(legalKey(id), JSON.stringify(record), { metadata: { request_id: id, state: record.state } });
      await writeLegalEvent(env, id, "ANALYSIS_REQUESTED", { source_ids: record.source_ids, jurisdiction: record.jurisdiction }, tenantId);
      return json({ ok: true, request_id: id, state: record.state, governor_decision: record.governor_decision });
    }

    const legalStage = url.pathname === "/legal/research" ? "RESEARCH_COMPLETED"
      : url.pathname === "/legal/verify" ? "VERIFICATION_COMPLETED"
      : url.pathname === "/legal/red-team" ? "RED_TEAM_COMPLETED" : null;
    if (legalStage && req.method === "POST") {
      const tenantId = legalPrincipal(req, env);
      if (!tenantId) return json({ error: "Unauthorized" }, 401);
      let data;
      try { data = await legalJson(req); } catch (error) {
        return json({ error: error.message }, error.message === "Submission too large" ? 413 : 400);
      }
      const requestId = String(data.request_id || "").trim();
      if (!requestId) return json({ error: "request_id is required" }, 400);
      const record = await loadLegalRequest(env, requestId, tenantId);
      if (!record) return json({ error: "Not found" }, 404);
      const requiredByStage = {
        RESEARCH_COMPLETED: ["research"],
        VERIFICATION_COMPLETED: ["verification_bundle", "verified_by"],
        RED_TEAM_COMPLETED: ["red_team", "attacker"],
      };
      const expectedState = {
        RESEARCH_COMPLETED: "RESEARCH_REQUIRED",
        VERIFICATION_COMPLETED: "VERIFICATION_REQUIRED",
        RED_TEAM_COMPLETED: "RED_TEAM_REQUIRED",
      };
      if (record.state !== expectedState[legalStage]) {
        return json({ error: `workflow state must be ${expectedState[legalStage]}`, state: record.state }, 409);
      }
      const missing = legalRequired(data, requiredByStage[legalStage]);
      if (legalStage === "RESEARCH_COMPLETED" && (!Array.isArray(data.research?.source_ids) || !data.research.source_ids.length)) missing.push("research.source_ids");
      if (legalStage === "VERIFICATION_COMPLETED" && (!Array.isArray(data.verification_bundle?.source_ids) || !data.verification_bundle.source_ids.length)) missing.push("verification_bundle.source_ids");
      if (legalStage === "RED_TEAM_COMPLETED" && !Array.isArray(data.red_team?.findings)) missing.push("red_team.findings");
      if (missing.length) return json({ error: "stage evidence is incomplete", missing }, 400);
      const evidenceSourceIds = legalStage === "RESEARCH_COMPLETED" ? data.research.source_ids
        : legalStage === "VERIFICATION_COMPLETED" ? data.verification_bundle.source_ids : [];
      if (evidenceSourceIds.some((sourceId) => !record.source_ids.includes(String(sourceId)))) {
        return json({ error: "stage evidence references a source outside the original request" }, 400);
      }
      const nextState = legalStage === "RESEARCH_COMPLETED" ? "VERIFICATION_REQUIRED"
        : legalStage === "VERIFICATION_COMPLETED" ? "RED_TEAM_REQUIRED" : "HUMAN_REVIEW_REQUIRED";
      const updated = await updateLegalState(env, record, nextState, {
        stages: [...(record.stages || []), { stage: legalStage, received_at: new Date().toISOString(), evidence: data }],
      });
      await writeLegalEvent(env, requestId, legalStage, { actor: data.verified_by || data.attacker || "retrieval", state: nextState }, tenantId);
      return json({ ok: true, request_id: requestId, state: updated.state, governor_decision: updated.governor_decision });
    }

    const governorMatch = url.pathname.match(/^\/legal\/requests\/([A-Za-z0-9-]+)\/governor$/);
    if (governorMatch && req.method === "GET") {
      const tenantId = legalPrincipal(req, env);
      if (!tenantId) return json({ error: "Unauthorized" }, 401);
      const record = await loadLegalRequest(env, governorMatch[1], tenantId);
      if (!record) return json({ error: "Not found" }, 404);
      return json({ request_id: record.id, state: record.state, governor_decision: record.governor_decision, stages: record.stages || [], human_review: record.human_review });
    }

    const reviewMatch = url.pathname.match(/^\/legal\/review\/([A-Za-z0-9-]+)$/);
    if (reviewMatch && req.method === "POST") {
      const tenantId = legalPrincipal(req, env);
      if (!tenantId) return json({ error: "Unauthorized" }, 401);
      let data;
      try { data = await legalJson(req); } catch (error) {
        return json({ error: error.message }, error.message === "Submission too large" ? 413 : 400);
      }
      const missing = legalRequired(data, ["reviewer", "notes", "decision"]);
      if (missing.length || !["APPROVE", "REVIEW_REQUIRED", "BLOCK"].includes(data.decision)) {
        return json({ error: "reviewer, notes, and decision (APPROVE, REVIEW_REQUIRED, or BLOCK) are required", missing }, 400);
      }
      const record = await loadLegalRequest(env, reviewMatch[1], tenantId);
      if (!record) return json({ error: "Not found" }, 404);
      if (record.state !== "HUMAN_REVIEW_REQUIRED") return json({ error: "Human review is not yet unlocked by the workflow" }, 409);
      const review = { reviewer: String(data.reviewer), notes: String(data.notes), decision: data.decision, recorded_at: new Date().toISOString() };
      const nextState = data.decision === "APPROVE" ? "HUMAN_APPROVED" : data.decision === "BLOCK" ? "BLOCKED" : "HUMAN_REVIEW_REQUIRED";
      const updated = await updateLegalState(env, record, nextState, { human_review: review, governor_decision: data.decision === "APPROVE" ? "HUMAN_APPROVED" : "REVIEW_REQUIRED" });
      await writeLegalEvent(env, record.id, "HUMAN_REVIEW_RECORDED", review, tenantId);
      return json({ ok: true, request_id: record.id, state: updated.state, governor_decision: updated.governor_decision });
    }

    if (url.pathname === "/api/intake" && req.method === "POST") {
      const raw = await req.text();
      if (raw.length > MAX_BODY) return json({ error: "Submission too large" }, 413);
      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        return json({ error: "Body must be valid JSON" }, 400);
      }
      if (!data.track || !data.goal) {
        return json({ error: "Missing required fields: track, goal" }, 400);
      }
      const id = crypto.randomUUID().slice(0, 8);
      const ts = new Date().toISOString();
      const routedLanes = premiumLaneRouting(data);
      const lanes = routedLanes.map((lane) => lane.id);
      const handoffPackage = buildHandoffPackage(data, id, ts, routedLanes);
      const record = {
        id,
        ts,
        ...data,
        premium_lanes: routedLanes,
        routing: { ...(data.routing || {}), premium_lanes: routedLanes },
        handoff_package: handoffPackage,
      };
      await env.INTAKE_KV.put(`intake:${ts}:${id}`, JSON.stringify(record), {
        metadata: {
          track: String(data.track),
          matter: String(data.matter_name || "").slice(0, 80),
          premium_lanes: lanes.join(",").slice(0, 160),
        },
      });
      return json({ ok: true, id, ts, premium_lanes: lanes, handoff_package: handoffPackage });
    }

    const one = url.pathname.match(/^\/api\/intake\/([A-Za-z0-9-]+)$/);
    if (one && req.method === "GET") {
      if (!authorized(req, env)) return json({ error: "Unauthorized" }, 401);
      const list = await env.INTAKE_KV.list({ prefix: "intake:" });
      const key = list.keys.find((k) => k.name.endsWith(`:${one[1]}`));
      if (!key) return json({ error: "Not found" }, 404);
      const val = await env.INTAKE_KV.get(key.name);
      return new Response(val, { headers: { "content-type": "application/json; charset=utf-8" } });
    }

    if (url.pathname === "/api/intakes" && req.method === "GET") {
      if (!authorized(req, env)) return json({ error: "Unauthorized" }, 401);
      const list = await env.INTAKE_KV.list({ prefix: "intake:", limit: 200 });
      return json(
        list.keys.map((k) => ({
          key: k.name,
          id: k.name.split(":").pop(),
          ts: k.name.split(":").slice(1, -1).join(":"),
          track: k.metadata?.track,
          matter: k.metadata?.matter,
          premium_lanes: k.metadata?.premium_lanes || "",
        }))
      );
    }

    return env.ASSETS.fetch(req);
  },
};

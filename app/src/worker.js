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

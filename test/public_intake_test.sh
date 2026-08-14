#!/usr/bin/env bash
# public_intake_test.sh — generated public intake packages must satisfy source-evidence gates.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FATAL: cannot resolve repo root" >&2
  exit 99
}
TMP="$(mktemp -d)"
export GLAW_HOME="$TMP"
pass=0
fail=0
ok() {
  if [ "$1" = 1 ]; then
    pass=$((pass + 1))
    echo "  ✓ $2"
  else
    fail=$((fail + 1))
    echo "  ✗ FAIL: $2"
  fi
}

cd "$ROOT" || exit 99

bin/glaw matter new "Public Intake Handoff" >/dev/null
MATTER_DIR="$(bin/glaw home)/matters/$(bin/glaw slug)"
mkdir -p "$MATTER_DIR/evidence"
printf '%s\n' 'Public intake source for Public Intake Handoff' > "$MATTER_DIR/evidence/public-intake.txt"
bin/glaw-intake set workflow_track litigation >/dev/null
bin/glaw-intake set parties 'Client LLC; Adverse Corp' >/dev/null
bin/glaw-intake set jurisdiction 'Florida' >/dev/null
bin/glaw-intake set goal 'judgment and collection' >/dev/null
bin/glaw-intake premium uhnw-family-office >/dev/null
rc=$?
ok "$([ "$rc" = 0 ] && grep -q '"premium_lanes":' "$MATTER_DIR/intake.json" && echo 1 || echo 0)" "generated public intake handoff records premium lanes in structured intake"
bin/glaw-premium-lanes attach uhnw-family-office --matter 'Public Intake Handoff' >/dev/null
rc=$?
ok "$([ "$rc" = 0 ] && [ -s "$MATTER_DIR/workpapers/premium-lane-uhnw-family-office.json" ] && echo 1 || echo 0)" "generated public intake premium-lane handoff attaches active-matter workpaper"
bin/glaw docket add --owner 'intake docket clerk' --source 'SRC-0001 public intake form' 2026-09-01 'SOL: breach claim' >/dev/null
rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "generated public intake docket command accepts current SRC-0001"
ok "$([ -s "$MATTER_DIR/evidence/public-intake.txt" ] && echo 1 || echo 0)" "public intake source artifact is nonempty"
ok "$(grep -q '"source":"SRC-0001 public intake form"' "$MATTER_DIR/docket.jsonl" && echo 1 || echo 0)" "docket row records source evidence basis"
ok "$(grep -q 'premium_lane_attached' "$MATTER_DIR/timeline.jsonl" && echo 1 || echo 0)" "premium lane handoff records timeline event"

node --input-type=module - "$ROOT/app/src/worker.js" <<'JS'
const workerPath = process.argv[2];
const mod = await import(`file://${workerPath}`);
const store = new Map();
const env = {
  INTAKE_ADMIN_TOKEN: "secret",
  INTAKE_KV: {
    async put(key, value, opts = {}) {
      store.set(key, { name: key, value, metadata: opts.metadata });
    },
    async list() {
      return { keys: [...store.values()].map(({ name, metadata }) => ({ name, metadata })) };
    },
    async get(key) {
      return store.get(key)?.value || null;
    },
  },
  ASSETS: { fetch: async () => new Response("asset") },
};

const post = await mod.default.fetch(new Request("https://glaw.test/api/intake", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    track: "litigation",
    goal: "collect",
    matter_name: "Public Intake",
    premium_lanes: [{ id: "uhnw-family-office", name: "UHNW / family office" }],
  }),
}), env);
if (post.status !== 200) throw new Error(`POST /api/intake expected 200, got ${post.status}`);
const posted = await post.json();
const { id } = posted;
if (!posted.premium_lanes?.includes("uhnw-family-office")) throw new Error("POST did not echo premium lane ids");
if (!posted.handoff_package?.source_only) throw new Error("POST did not return a source-only handoff package");
if (!posted.handoff_package?.attach_commands?.some((cmd) => cmd.includes("bin/glaw-premium-lanes attach uhnw-family-office"))) {
  throw new Error("POST handoff package did not include UHNW lane attach command");
}
if (!posted.handoff_package?.premium_intake_commands?.some((cmd) => cmd === "bin/glaw-intake premium uhnw-family-office")) {
  throw new Error("POST handoff package did not include premium intake command");
}
if (!posted.handoff_package?.commands?.some((cmd) => cmd === "bin/glaw-intake premium uhnw-family-office")) {
  throw new Error("POST full command script did not tag premium intake scope");
}
if (posted.handoff_package?.manifest_contract?.source !== "lib/client-lanes/premium-lanes.json") {
  throw new Error("POST handoff package did not expose premium-lane manifest contract");
}
const explicitChecklists = new Map((posted.handoff_package?.required_checklists || []).map((row) => [row.lane_id, row.checklists]));
if (!explicitChecklists.get("uhnw-family-office")?.includes("schwab_trust_topic_required")) {
  throw new Error("POST handoff package did not expose UHNW Schwab trust checklist");
}
if (!explicitChecklists.get("uhnw-family-office")?.includes("trust_taxonomy_required")) {
  throw new Error("POST handoff package did not expose UHNW trust taxonomy checklist");
}
for (const fragment of [
  "bin/glaw-premium-lanes complete --lane uhnw-family-office",
  "bin/glaw-premium-lanes render-packet --lane uhnw-family-office",
  "bin/glaw-premium-lanes check-packet --lane uhnw-family-office",
  "bin/glaw-premium-lanes docket --lane uhnw-family-office",
]) {
  if (!posted.handoff_package?.lane_gate_commands?.some((cmd) => cmd.includes(fragment))) {
    throw new Error(`POST handoff package did not include lane gate command: ${fragment}`);
  }
}
if (!posted.handoff_package?.evidence_text?.includes("Premium lanes: uhnw-family-office (explicit)")) {
  throw new Error("POST handoff package did not preserve explicit lane evidence text");
}

const unauthOne = await mod.default.fetch(new Request(`https://glaw.test/api/intake/${id}`), env);
if (unauthOne.status !== 401) throw new Error(`GET /api/intake/:id without token expected 401, got ${unauthOne.status}`);

const authOne = await mod.default.fetch(new Request(`https://glaw.test/api/intake/${id}`, {
  headers: { authorization: "Bearer secret" },
}), env);
if (authOne.status !== 200) throw new Error(`GET /api/intake/:id with token expected 200, got ${authOne.status}`);
const record = await authOne.json();
if (record.id !== id || record.track !== "litigation") throw new Error("GET /api/intake/:id returned wrong record");
if (record.premium_lanes?.[0]?.id !== "uhnw-family-office") throw new Error("GET /api/intake/:id lost premium lane payload");
if (!record.handoff_package?.attach_commands?.some((cmd) => cmd.includes("bin/glaw-premium-lanes attach uhnw-family-office"))) {
  throw new Error("GET /api/intake/:id lost handoff attach command");
}

const unauthList = await mod.default.fetch(new Request("https://glaw.test/api/intakes"), env);
if (unauthList.status !== 401) throw new Error(`GET /api/intakes without token expected 401, got ${unauthList.status}`);

const authList = await mod.default.fetch(new Request("https://glaw.test/api/intakes", {
  headers: { authorization: "Bearer secret" },
}), env);
if (authList.status !== 200) throw new Error(`GET /api/intakes with token expected 200, got ${authList.status}`);
const rows = await authList.json();
if (rows[0]?.premium_lanes !== "uhnw-family-office") throw new Error("GET /api/intakes metadata lost premium lanes");

const inferredPost = await mod.default.fetch(new Request("https://glaw.test/api/intake", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    track: "hybrid",
    goal: "Fortune 500 public-ready founder wants QSBS, 83(b), 409A, SEC reporting, ASC 740 tax provision, IRS notice response, capital raise, dynasty trust, investment LLC, and investor disclosures",
    matter_name: "Founder Enterprise Tax Intake",
    parties: "Founder; public-ready C-corp; family office; investors",
    source_documents: "cap table, SAFE, IRS notice, draft 10-K controls, trust chart",
  }),
}), env);
if (inferredPost.status !== 200) throw new Error(`POST inferred intake expected 200, got ${inferredPost.status}`);
const inferred = await inferredPost.json();
const inferredIds = new Set(inferred.premium_lanes || []);
for (const id of ["fortune500-enterprise", "tax-system", "founder-unicorn", "uhnw-family-office"]) {
  if (!inferredIds.has(id)) throw new Error(`POST did not infer ${id}`);
}
for (const id of ["fortune500-enterprise", "tax-system", "founder-unicorn", "uhnw-family-office"]) {
  if (!inferred.handoff_package?.attach_commands?.some((cmd) => cmd.includes(`bin/glaw-premium-lanes attach ${id}`))) {
    throw new Error(`POST inferred handoff did not include attach command for ${id}`);
  }
}
if (!inferred.handoff_package?.premium_intake_commands?.includes("bin/glaw-intake premium fortune500-enterprise tax-system founder-unicorn uhnw-family-office")) {
  throw new Error("POST inferred handoff did not include canonical multi-lane intake premium command");
}
if (!inferred.handoff_package?.evidence_text?.includes("Premium lanes: fortune500-enterprise (inferred)")) {
  throw new Error("POST inferred handoff did not include premium-lane evidence text");
}
if (!inferred.handoff_package?.lanes?.every((lane) => lane.source === "inferred")) {
  throw new Error("POST inferred handoff did not preserve inferred source labels");
}
const inferredChecklists = new Map((inferred.handoff_package?.required_checklists || []).map((row) => [row.lane_id, row.checklists]));
const expectedChecklistByLane = new Map([
  ["fortune500-enterprise", "enterprise_required"],
  ["tax-system", "source_ingest_required"],
  ["founder-unicorn", "qsbs_required"],
  ["uhnw-family-office", "schwab_trust_topic_required"],
]);
for (const [laneId, checklist] of expectedChecklistByLane) {
  if (!inferredChecklists.get(laneId)?.includes(checklist)) {
    throw new Error(`POST inferred handoff did not include ${checklist} for ${laneId}`);
  }
  if (!inferred.handoff_package?.lane_gate_commands?.some((cmd) => cmd.includes(`bin/glaw-premium-lanes check-packet --lane ${laneId}`))) {
    throw new Error(`POST inferred handoff did not include check-packet command for ${laneId}`);
  }
}
if (!inferred.handoff_package?.notes?.some((note) => note.includes("fail stale artifacts closed"))) {
  throw new Error("POST inferred handoff did not explain stale manifest failure");
}

const inferredOne = await mod.default.fetch(new Request(`https://glaw.test/api/intake/${inferred.id}`, {
  headers: { authorization: "Bearer secret" },
}), env);
if (inferredOne.status !== 200) throw new Error(`GET inferred intake expected 200, got ${inferredOne.status}`);
const inferredRecord = await inferredOne.json();
const routed = new Map((inferredRecord.routing?.premium_lanes || []).map((lane) => [lane.id, lane]));
for (const id of ["fortune500-enterprise", "tax-system", "founder-unicorn", "uhnw-family-office"]) {
  if (routed.get(id)?.source !== "inferred") throw new Error(`GET inferred record did not preserve inferred route for ${id}`);
}
if (!inferredRecord.handoff_package?.evidence_text?.includes("Premium lanes: fortune500-enterprise (inferred)")) {
  throw new Error("GET inferred record lost handoff evidence text");
}
if (!inferredRecord.handoff_package?.required_checklists?.some((row) => row.lane_id === "tax-system" && row.checklists.includes("tax_credit_required"))) {
  throw new Error("GET inferred record lost required checklist payload");
}
JS
ok "$([ "$?" = 0 ] && echo 1 || echo 0)" "worker keeps POST public, returns source-only lane handoff, infers premium lanes, and gates intake reads behind bearer token"

echo "public-intake test: $pass passed, $fail failed"
[ "$fail" = 0 ]

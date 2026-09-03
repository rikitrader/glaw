import type { ControlPlaneDb } from "./db";
import { createLocalHmacSigner } from "./signer";

type AuditRow = Record<string, unknown>;

export type AuditExport = {
  schemaVersion: "1.0";
  tenantId: string;
  matterId?: string;
  events: AuditRow[];
  manifest: {
    eventCount: number;
    firstEventHash?: string;
    rootHash: string;
    generatedAt: string;
  };
  signature: string;
  signingKeyId: string;
};

export function verifyAuditChain(audit: AuditExport): { valid: boolean; reason: string } {
  if (audit.schemaVersion !== "1.0" || audit.events.length !== audit.manifest.eventCount) return { valid: false, reason: "schema or event count mismatch" };
  let previous: string | null = null;
  for (const event of audit.events) {
    if ((event.previous_hash ?? null) !== previous) return { valid: false, reason: `hash chain discontinuity at ${String(event.id)}` };
    previous = String(event.event_hash);
  }
  if (previous !== audit.manifest.rootHash) return { valid: false, reason: "root hash mismatch" };
  if (audit.events[0] && String(audit.events[0].event_hash) !== audit.manifest.firstEventHash) return { valid: false, reason: "first hash mismatch" };
  return { valid: true, reason: "audit chain is structurally valid; cryptographic signature requires the configured verifier key" };
}

export async function appendAuditEvent(db: ControlPlaneDb, input: { tenantId: string; matterId?: string; actorId: string; traceId: string; commandId?: string; eventType: string; payload: Record<string, unknown> }): Promise<void> {
  await db.batch([await buildAuditEventStatement(db, input)]);
}

export async function buildAuditEventStatement(db: ControlPlaneDb, input: { tenantId: string; matterId?: string; actorId: string; traceId: string; commandId?: string; eventType: string; payload: Record<string, unknown> }) {
  const previous = await db.prepare("SELECT event_hash FROM governed_audit_events WHERE organization_id = ? ORDER BY created_at DESC LIMIT 1").bind(input.tenantId).first<{ event_hash: string }>();
  const createdAt = new Date().toISOString();
  const payloadJson = canonicalJson(input.payload);
  const eventHash = await sha256Hex(canonicalJson({ ...input, payload: payloadJson, previousHash: previous?.event_hash ?? null, createdAt }));
  return db.prepare("INSERT INTO governed_audit_events (id, organization_id, matter_id, actor_id, trace_id, command_id, event_type, payload_json, previous_hash, event_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), input.tenantId, input.matterId ?? null, input.actorId, input.traceId, input.commandId ?? null, input.eventType, payloadJson, previous?.event_hash ?? null, eventHash, createdAt);
}

export async function createAuditExport(db: ControlPlaneDb, tenantId: string, actorId: string, signingSecret: string, signingKeyId: string, matterId?: string): Promise<AuditExport> {
  const signer = createLocalHmacSigner(signingSecret, signingKeyId);
  const query = matterId ? "SELECT id, organization_id, matter_id, actor_id, trace_id, command_id, event_type, payload_json, previous_hash, event_hash, created_at FROM governed_audit_events WHERE organization_id = ? AND matter_id = ? ORDER BY created_at ASC" : "SELECT id, organization_id, matter_id, actor_id, trace_id, command_id, event_type, payload_json, previous_hash, event_hash, created_at FROM governed_audit_events WHERE organization_id = ? ORDER BY created_at ASC";
  const rows = matterId ? await db.prepare(query).bind(tenantId, matterId).all<AuditRow>() : await db.prepare(query).bind(tenantId).all<AuditRow>();
  const events = rows.results;
  const rootHash = events.at(-1)?.event_hash ? String(events.at(-1)?.event_hash) : await sha256Hex(`${tenantId}:${matterId ?? "all"}:empty`);
  const manifest = { eventCount: events.length, firstEventHash: events[0]?.event_hash ? String(events[0].event_hash) : undefined, rootHash, generatedAt: new Date().toISOString() };
  const signedBody = canonicalJson({ schemaVersion: "1.0", tenantId, matterId, events, manifest });
  const signature = await signer.sign(signedBody);
  await db.prepare("INSERT INTO audit_export_manifests (id, tenant_id, matter_id, event_count, root_hash, manifest_json, signature, signing_key_id, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), tenantId, matterId ?? null, events.length, rootHash, JSON.stringify(manifest), signature, signingKeyId, manifest.generatedAt, actorId).all();
  return { schemaVersion: "1.0", tenantId, matterId, events, manifest, signature, signingKeyId: signer.keyId };
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b)).map(([key, nested]) => `${JSON.stringify(key)}:${canonicalJson(nested)}`).join(",")}}`;
  }
  return JSON.stringify(value);
}
async function sha256Hex(value: string): Promise<string> { const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)); return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join(""); }

import type { ControlPlaneDb } from "./db";
import type { RequestPrincipal } from "./auth";
import { authorizeRelation } from "./authorization";
import { buildAuditEventStatement } from "./audit";

export type WorkflowDefinition = { nodes: unknown[]; edges: unknown[]; [key: string]: unknown };
export type WorkflowScope = { workflowId: string; matterId?: string; name: string; revision: number; revisionHash: string; policyVersion: string; environment: "sandbox" | "staging" | "production"; status: "DRAFT" | "PUBLISHED" | "REVOKED"; definition: WorkflowDefinition; updatedBy: string; updatedAt: string };

export async function getWorkflowScope(db: ControlPlaneDb, principal: RequestPrincipal, workflowId: string): Promise<{ scope?: WorkflowScope; error?: Response }> {
  const workflow = await db.prepare("SELECT id, matter_id, name, version, status, definition_json, created_at FROM workflows WHERE id = ? AND organization_id = ?").bind(workflowId, principal.tenantId).first<{ id: string; matter_id: string | null; name: string; version: string; status: string; definition_json: string; created_at: string }>();
  if (!workflow) return { error: jsonError("workflow not found in tenant scope", 404) };
  if (!workflow.matter_id) return { error: jsonError("workflow matter scope is required", 422) };
  const access = await authorizeRelation(db, principal, "workflow.read", "matter", workflow.matter_id, workflow.version);
  if (access.decision === "DENY") return { error: jsonError(access.reason, 403) };
  const latest = await db.prepare("SELECT revision, revision_hash, policy_version, environment, status, definition_json, created_by, created_at FROM workflow_versions WHERE organization_id = ? AND workflow_id = ? ORDER BY revision DESC LIMIT 1").bind(principal.tenantId, workflowId).first<{ revision: number; revision_hash: string; policy_version: string; environment: "sandbox" | "staging" | "production"; status: "DRAFT" | "PUBLISHED" | "REVOKED"; definition_json: string; created_by: string; created_at: string }>();
  const definition = parseDefinition(latest?.definition_json ?? workflow.definition_json);
  return { scope: { workflowId, matterId: workflow.matter_id, name: workflow.name, revision: latest?.revision ?? 0, revisionHash: latest?.revision_hash ?? "legacy-unversioned", policyVersion: latest?.policy_version ?? workflow.version, environment: latest?.environment ?? "sandbox", status: latest?.status ?? (workflow.status === "confirmed" ? "PUBLISHED" : "DRAFT"), definition, updatedBy: latest?.created_by ?? "legacy", updatedAt: latest?.created_at ?? workflow.created_at } };
}

export async function authorizeWorkflowWrite(db: ControlPlaneDb, principal: RequestPrincipal, matterId: string, policyVersion: string): Promise<Response | null> {
  const access = await authorizeRelation(db, principal, "workflow.write", "matter", matterId, policyVersion);
  if (access.decision === "DENY") return jsonError(access.reason, 403);
  return null;
}

export async function hashDefinition(definition: WorkflowDefinition): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonicalJson(definition)));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function parseDefinition(value: string): WorkflowDefinition {
  try {
    const parsed = JSON.parse(value) as Partial<WorkflowDefinition>;
    return { ...parsed, nodes: Array.isArray(parsed.nodes) ? parsed.nodes : [], edges: Array.isArray(parsed.edges) ? parsed.edges : [] };
  } catch { return { nodes: [], edges: [] }; }
}

export async function persistWorkflowVersion(db: ControlPlaneDb, input: { principal: RequestPrincipal; workflowId: string; matterId: string; definition: WorkflowDefinition; expectedRevision: number; policyVersion: string; environment: "sandbox" | "staging" | "production"; status: "DRAFT" | "PUBLISHED"; action: "SAVE_DRAFT" | "REQUEST_PUBLISH" | "PREPARE_DRY_RUN"; state: "accepted" | "authorized" | "approval_required" | "blocked" | "completed" | "failed"; reason: string }): Promise<{ ok: true; receiptId: string; commandId: string; revision: number; revisionHash: string; state: string } | { ok: false; response: Response }> {
  const latest = await db.prepare("SELECT revision FROM workflow_versions WHERE organization_id = ? AND workflow_id = ? ORDER BY revision DESC LIMIT 1").bind(input.principal.tenantId, input.workflowId).first<{ revision: number }>();
  const actualRevision = latest?.revision ?? 0;
  if (actualRevision !== input.expectedRevision) return { ok: false, response: jsonError(`stale workflow revision; expected ${input.expectedRevision}, current ${actualRevision}`, 409) };
  const revision = actualRevision + 1;
  const revisionHash = await hashDefinition(input.definition);
  const now = new Date().toISOString();
  const commandId = crypto.randomUUID();
  const receiptId = crypto.randomUUID();
  const definitionJson = canonicalJson(input.definition);
  try {
    const auditStatement = await buildAuditEventStatement(db, { tenantId: input.principal.tenantId, matterId: input.matterId, actorId: input.principal.actorId, traceId: crypto.randomUUID(), commandId, eventType: `workflow.${input.action.toLowerCase()}`, payload: { workflowId: input.workflowId, revision, revisionHash, policyVersion: input.policyVersion, environment: input.environment, state: input.state } });
    await db.batch([
      db.prepare("INSERT INTO workflow_versions (id, organization_id, matter_id, workflow_id, revision, revision_hash, policy_version, environment, status, definition_json, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(crypto.randomUUID(), input.principal.tenantId, input.matterId, input.workflowId, revision, revisionHash, input.policyVersion, input.environment, input.status, definitionJson, input.principal.actorId, now),
      db.prepare("INSERT INTO workflow_action_receipts (id, organization_id, workflow_id, revision, command_id, action, state, payload_hash, external_effect, reason, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NONE', ?, ?, ?)").bind(receiptId, input.principal.tenantId, input.workflowId, revision, commandId, input.action, input.state, revisionHash, input.reason, input.principal.actorId, now),
      auditStatement
    ]);
  } catch (error) { return { ok: false, response: jsonError(error instanceof Error ? error.message : "workflow version could not be persisted", 400) }; }
  return { ok: true, receiptId, commandId, revision, revisionHash, state: input.state };
}

export function jsonError(message: string, status: number): Response { return new Response(JSON.stringify({ ok: false, error: message }), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } }); }

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b)).map(([key, nested]) => `${JSON.stringify(key)}:${canonicalJson(nested)}`).join(",")}}`;
  return JSON.stringify(value);
}

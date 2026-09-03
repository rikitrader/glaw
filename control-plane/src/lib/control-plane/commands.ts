import type { ControlPlaneDb, D1Statement } from "./db";
import type { LegalCommand, CommandReceipt } from "../contracts/legal";
import { validateLegalCommand } from "../contracts/legal";
import type { RequestPrincipal } from "./auth";
import { authorizeRelation } from "./authorization";
import { buildAuditEventStatement } from "./audit";

export type CommandDecision = "ALLOW" | "DENY" | "ESCALATE";

export async function decideCommand(db: ControlPlaneDb, command: LegalCommand, principal: RequestPrincipal): Promise<{ decision: CommandDecision; reason: string }> {
  if (command.tenantId !== principal.tenantId) return { decision: "DENY", reason: "tenant scope mismatch" };
  if (command.actor.actorId !== principal.actorId) return { decision: "DENY", reason: "actor identity mismatch" };
  if (!command.matterId) return { decision: "DENY", reason: "matter scope is required for governed execution" };
  const relation = await authorizeRelation(db, principal, command.action, "matter", command.matterId, command.authority.policyVersion);
  if (relation.decision === "DENY") return { decision: "DENY", reason: relation.reason };
  if (command.riskClass === "HIGH" || command.riskClass === "CRITICAL") {
    return { decision: "ESCALATE", reason: "high-risk command requires configured human approval" };
  }
  if (/^(email.send|court.file|signature.request|payment.execute|document.delete)$/.test(command.action)) {
    return { decision: "ESCALATE", reason: "external or destructive side effect requires approval and reconciliation" };
  }
  return { decision: relation.decision === "ESCALATE" ? "ESCALATE" : relation.decision, reason: relation.reason };
}

export async function acceptCommand(db: ControlPlaneDb, command: LegalCommand, principal: RequestPrincipal): Promise<{ receipt: CommandReceipt; decision: CommandDecision; reason: string; replayed: boolean }> {
  validateLegalCommand(command);
  const { decision, reason } = await decideCommand(db, command, principal);
  const now = new Date().toISOString();
  const payloadJson = JSON.stringify(command.payload) ?? "null";
  const evidenceRefsJson = JSON.stringify(command.evidenceRefs) ?? "[]";
  const approvalRefsJson = JSON.stringify(command.approvalRefs) ?? "[]";
  const payloadHash = await sha256Hex(payloadJson);
  let existing: Record<string, unknown> | null;
  try {
    existing = await db.prepare("SELECT id, command_id, idempotency_key, state, attempt, reconciliation_status, created_at, updated_at FROM command_receipts WHERE organization_id = ? AND idempotency_key = ?").bind(command.tenantId, command.idempotencyKey).first<Record<string, unknown>>();
  } catch (error) {
    throw new Error(`idempotency lookup failed: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (existing) {
    return { replayed: true, decision, reason: "idempotency key already accepted", receipt: mapReceipt(existing) };
  }

  const commandStatus = decision === "ALLOW" ? "accepted" : decision === "ESCALATE" ? "escalated" : "blocked";
  const receiptId = crypto.randomUUID();
  const receiptState = decision === "ALLOW" ? "authorized" : "accepted";
  const receipt: CommandReceipt = {
    receiptId,
    commandId: command.commandId,
    idempotencyKey: command.idempotencyKey,
    state: receiptState,
    attempt: 0,
    reconciliationStatus: "NOT_REQUIRED",
    createdAt: now,
    updatedAt: now
  };

  const commandValues: unknown[] = [command.commandId, command.idempotencyKey, command.tenantId, command.clientId ?? null, command.matterId ?? null, command.actor.actorId, command.actor.actorType, command.actor.role, command.authority.policyId, command.authority.policyVersion, command.action, payloadJson, command.riskClass, evidenceRefsJson, approvalRefsJson, command.expectedExternalEffect ?? null, commandStatus, payloadHash, now, command.expiresAt ?? null];
  commandValues.forEach((value, index) => {
    if (value !== null && typeof value !== "string" && typeof value !== "number") throw new Error(`command bind value ${index} is not scalar`);
  });

  const prepareBind = (label: string, sql: string, values: unknown[]): D1Statement => {
    try { return db.prepare(sql).bind(...values); } catch (error) { throw new Error(`${label} bind failed: ${error instanceof Error ? error.message : String(error)}`); }
  };
  const commandStatement = prepareBind("commands", "INSERT INTO commands (id, idempotency_key, organization_id, client_id, matter_id, actor_id, actor_type, actor_role, policy_id, policy_version, action, payload_json, risk_class, evidence_refs_json, approval_refs_json, expected_external_effect, status, payload_hash, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", commandValues);
  const decisionStatement = prepareBind("authorization_decisions", "INSERT INTO authorization_decisions (id, command_id, organization_id, decision, reason, policy_version, relationships_json, decided_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [crypto.randomUUID(), command.commandId, command.tenantId, decision, decision === "ALLOW" ? "tenant and actor scope matched; action is non-consequential" : decision === "ESCALATE" ? "human approval boundary" : "authorization scope failed", command.authority.policyVersion, JSON.stringify([`tenant:${command.tenantId}`, `actor:${command.actor.actorId}`, `matter:${command.matterId ?? "none"}`]), now]);
  const receiptStatement = prepareBind("command_receipts", "INSERT INTO command_receipts (id, command_id, organization_id, idempotency_key, state, attempt, reconciliation_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)", [receiptId, command.commandId, command.tenantId, command.idempotencyKey, receiptState, "NOT_REQUIRED", now, now]);
  const auditStatement = await buildAuditEventStatement(db, { tenantId: command.tenantId, matterId: command.matterId, actorId: principal.actorId, traceId: crypto.randomUUID(), commandId: command.commandId, eventType: "command.accepted", payload: { action: command.action, riskClass: command.riskClass, decision } });
  // D1 batch is atomic: command, authorization decision, receipt, and audit event commit together.
  try {
    await db.batch([commandStatement, decisionStatement, receiptStatement, auditStatement]);
  } catch (error) {
    throw new Error(`command persistence failed: ${error instanceof Error ? error.message : String(error)}`);
  }

  return { receipt, decision, reason: reason || (decision === "ALLOW" ? "accepted and authorized for preparatory execution" : decision === "ESCALATE" ? "accepted but held for human approval" : "blocked by authorization"), replayed: false };
}

async function sha256Hex(value: string): Promise<string> {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function mapReceipt(row: Record<string, unknown>): CommandReceipt {
  return {
    receiptId: String(row.id),
    commandId: String(row.command_id),
    idempotencyKey: String(row.idempotency_key),
    state: String(row.state) as CommandReceipt["state"],
    attempt: Number(row.attempt ?? 0),
    reconciliationStatus: String(row.reconciliation_status ?? "NOT_REQUIRED") as CommandReceipt["reconciliationStatus"],
    createdAt: String(row.created_at),
    updatedAt: String(row.updated_at)
  };
}

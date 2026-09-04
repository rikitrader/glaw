/**
 * Sovereign Legal Intelligence OS foundation contracts.
 *
 * These are transport and policy contracts only. They do not authorize an
 * external legal action; a policy engine and a human approval record must do
 * that at the appropriate risk boundary.
 */

export const RISK_CLASSES = ["LOW", "MODERATE", "HIGH", "CRITICAL"] as const;
export type RiskClass = (typeof RISK_CLASSES)[number];

export const ACTOR_TYPES = ["human", "agent", "service"] as const;
export type ActorType = (typeof ACTOR_TYPES)[number];

export const DECISIONS = ["ALLOW", "DENY", "ESCALATE"] as const;
export type AuthorizationDecision = (typeof DECISIONS)[number];

export const SIDE_EFFECTS = ["NONE", "REVERSIBLE", "IRREVERSIBLE"] as const;
export type SideEffect = (typeof SIDE_EFFECTS)[number];

export type LegalCommand<TPayload = unknown> = {
  commandId: string;
  idempotencyKey: string;
  tenantId: string;
  clientId?: string;
  matterId?: string;
  actor: {
    actorId: string;
    actorType: ActorType;
    role: string;
  };
  authority: {
    policyId: string;
    policyVersion: string;
    grantId?: string;
  };
  action: string;
  payload: TPayload;
  riskClass: RiskClass;
  evidenceRefs: string[];
  approvalRefs: string[];
  expectedExternalEffect?: string;
  createdAt: string;
  expiresAt?: string;
};

export type CommandReceiptState =
  | "accepted"
  | "authorized"
  | "authority_claimed"
  | "adapter_attempted"
  | "observed_effective"
  | "unknown"
  | "failed";

export type CommandReceipt = {
  receiptId: string;
  commandId: string;
  idempotencyKey: string;
  state: CommandReceiptState;
  attempt: number;
  externalRequestId?: string;
  externalTransactionId?: string;
  externalReceipt?: string;
  expectedState?: string;
  observedState?: string;
  reconciliationStatus: "NOT_REQUIRED" | "PENDING" | "CONFIRMED" | "FAILED";
  createdAt: string;
  updatedAt: string;
};

export type AuthorizationDecisionRecord = {
  decision: AuthorizationDecision;
  reason: string;
  policyVersion: string;
  relationshipsEvaluated: string[];
  decisionId: string;
  decidedAt: string;
};

export type EvidenceReference = {
  evidenceId: string;
  sourceId: string;
  sourceVersion: number;
  documentHash: string;
  locator?: {
    page?: number;
    paragraph?: number;
    startOffset?: number;
    endOffset?: number;
  };
  authorityClass: string;
  jurisdiction?: string;
  accessScope: string;
};

export type EvidencePacket = {
  conclusionId: string;
  proposition: string;
  conclusionType: "fact" | "law" | "analysis" | "prediction" | "recommendation";
  jurisdiction?: string;
  supportingEvidence: EvidenceReference[];
  contraryEvidence: EvidenceReference[];
  unsupportedElements: string[];
  freshness: {
    checkedAt: string;
    currentThrough?: string;
    staleRisk: boolean;
  };
  confidenceSignals: {
    sourceAgreement: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
    authorityWeight: "BINDING" | "PERSUASIVE" | "SECONDARY" | "UNKNOWN";
    retrievalComplete: boolean;
    contradictionRisk: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  };
  generatedBy: {
    model: string;
    modelVersion: string;
    workflowVersion: string;
    skillVersion: string;
  };
  reviewedBy?: string[];
  approvedBy?: string[];
  artifactHash?: string;
};

export type AuditEvent = {
  eventId: string;
  eventType: string;
  tenantId: string;
  matterId?: string;
  actorId: string;
  traceId: string;
  commandId?: string;
  occurredAt: string;
  payload: Record<string, unknown>;
  previousHash?: string;
  eventHash: string;
};

export function assertNonEmpty(value: unknown, field: string): asserts value is string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
}

export function validateLegalCommand(command: LegalCommand): void {
  assertNonEmpty(command.commandId, "commandId");
  assertNonEmpty(command.idempotencyKey, "idempotencyKey");
  assertNonEmpty(command.tenantId, "tenantId");
  assertNonEmpty(command.action, "action");
  assertNonEmpty(command.actor.actorId, "actor.actorId");
  assertNonEmpty(command.authority.policyId, "authority.policyId");
  assertNonEmpty(command.authority.policyVersion, "authority.policyVersion");
  if (!RISK_CLASSES.includes(command.riskClass)) throw new Error("invalid riskClass");
  if (!ACTOR_TYPES.includes(command.actor.actorType)) throw new Error("invalid actorType");
  if (!Array.isArray(command.evidenceRefs) || !Array.isArray(command.approvalRefs)) {
    throw new Error("evidenceRefs and approvalRefs must be arrays");
  }
}

export function isConsequential(command: LegalCommand): boolean {
  return command.riskClass === "HIGH" || command.riskClass === "CRITICAL";
}

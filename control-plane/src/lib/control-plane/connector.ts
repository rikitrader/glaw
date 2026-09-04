import type { LegalCommand } from "../contracts/legal";

export type ConnectorCapabilities = {
  connectorId: string;
  supportsIdempotency: boolean;
  supportsLookup: boolean;
  supportsWebhooks: boolean;
  supportsCompensation: boolean;
  maxAttempts: number;
};

export type ExternalReference = { connectorId: string; requestId?: string; transactionId?: string; idempotencyKey: string };
export type ExternalState = { status: "UNKNOWN" | "PENDING" | "EFFECTIVE" | "FAILED"; fingerprint?: string; observedAt: string };
export type ReconciliationResult = { status: "CONFIRMED" | "RECONCILIATION_REQUIRED" | "FAILED"; reason: string };
export type ConnectorAdapter = {
  submit(command: LegalCommand, reference: ExternalReference): Promise<{ requestId?: string; transactionId?: string; receipt?: string }>;
  lookup(reference: ExternalReference): Promise<ExternalState>;
};

export function validateConnectorCapabilities(capabilities: ConnectorCapabilities): void {
  if (!capabilities.connectorId || capabilities.maxAttempts < 1) throw new Error("invalid connector capabilities");
  if (!capabilities.supportsLookup && capabilities.supportsIdempotency) throw new Error("idempotent connector must expose authoritative lookup");
}

export function reconcileExternalState(command: LegalCommand, expectedFingerprint: string, observed: ExternalState): ReconciliationResult {
  if (observed.status === "UNKNOWN" || observed.status === "PENDING") return { status: "RECONCILIATION_REQUIRED", reason: "external state is not yet authoritative" };
  if (observed.status === "FAILED") return { status: "FAILED", reason: "external system reported failure" };
  if (observed.fingerprint !== expectedFingerprint) return { status: "RECONCILIATION_REQUIRED", reason: "observed state does not match expected effect" };
  if (!command.idempotencyKey) return { status: "FAILED", reason: "idempotency key is required for reconciliation" };
  return { status: "CONFIRMED", reason: "observed external state matches expected effect" };
}

/** Durable-worker decision logic. The caller persists each state transition. */
export async function executeConnectorOperation(command: LegalCommand, capabilities: ConnectorCapabilities, adapter: ConnectorAdapter, reference: ExternalReference, expectedFingerprint: string, onState: (state: string, data?: Record<string, unknown>) => Promise<void>): Promise<ReconciliationResult> {
  validateConnectorCapabilities(capabilities);
  await onState("VALIDATED");
  for (let attempt = 1; attempt <= capabilities.maxAttempts; attempt += 1) {
    try {
      const receipt = await adapter.submit(command, reference);
      await onState("RECEIPT_RECEIVED", { attempt, requestId: receipt.requestId, transactionId: receipt.transactionId });
      const observed = await adapter.lookup({ ...reference, requestId: receipt.requestId, transactionId: receipt.transactionId });
      await onState("LOOKUP_PERFORMED", { attempt, observedStatus: observed.status });
      const result = reconcileExternalState(command, expectedFingerprint, observed);
      await onState(result.status === "CONFIRMED" ? "CONFIRMED" : result.status === "FAILED" ? "FAILED" : "RECONCILIATION_REQUIRED", { reason: result.reason });
      return result;
    } catch (error) {
      await onState("ATTEMPT_FAILED", { attempt, errorCode: "CONNECTOR_FAILURE" });
      if (attempt === capabilities.maxAttempts) {
        await onState("RECONCILIATION_REQUIRED", { reason: "attempt budget exhausted; external state must be reviewed" });
        return { status: "RECONCILIATION_REQUIRED", reason: "connector attempt budget exhausted" };
      }
    }
  }
  return { status: "RECONCILIATION_REQUIRED", reason: "connector worker exited without authoritative state" };
}

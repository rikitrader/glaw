import type { ControlPlaneDb } from "./db";

export type DeadLetterItem = {
  id: string;
  tenantId: string;
  operationId?: string;
  kind: string;
  payloadHash: string;
  reasonCode: string;
  createdAt: string;
};

export async function enqueueDeadLetter(db: ControlPlaneDb, item: DeadLetterItem): Promise<void> {
  await db.prepare("INSERT INTO dead_letter_items (id, tenant_id, operation_id, kind, payload_hash, reason_code, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)")
    .bind(item.id, item.tenantId, item.operationId ?? null, item.kind, item.payloadHash, item.reasonCode, item.createdAt).run();
}

export async function recordTelemetry(db: ControlPlaneDb, input: { tenantId?: string; name: string; value: number; unit: string; dimensions: Record<string, string>; traceId?: string; recordedAt: string }): Promise<void> {
  await db.prepare("INSERT INTO telemetry_metrics (id, tenant_id, metric_name, metric_value, unit, dimensions_json, trace_id, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
    .bind(crypto.randomUUID(), input.tenantId ?? null, input.name, input.value, input.unit, JSON.stringify(input.dimensions), input.traceId ?? null, input.recordedAt).run();
}

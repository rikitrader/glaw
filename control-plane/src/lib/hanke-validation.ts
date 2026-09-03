export type HaeisRunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'BLOCKED' | 'FAILED';
export type HaeisReviewStatus = 'PENDING' | 'APPROVED' | 'REJECTED';
export type HaeisGateStatus = 'OPEN' | 'PASS' | 'BLOCKED';
export type HaeisEventType = 'RUN_STARTED' | 'NODE_STARTED' | 'NODE_FINISHED' | 'GATE_UPDATED' | 'RUN_FINISHED';

export interface HaeisRunPayload {
  run_id?: string;
  organization_id?: string;
  matter_id?: string | null;
  workflow_id?: string;
  status?: string;
  review?: { status?: string; reviewer_id?: string; note?: string };
  human_review_packet?: { status?: string; review_required?: boolean; review_stage?: string; review_scope?: string; file_path?: string };
  gate_records?: Record<string, { status: string; owner: string; evidence_ids: string[]; reason?: string }>;
  events?: Array<{ sequence: number; type: string; payload?: Record<string, unknown> }>;
}

const isRecord = (value: unknown): value is Record<string, any> => Boolean(value) && typeof value === 'object' && !Array.isArray(value);
const nonEmptyString = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0;

export function validateHaeisRunPayload(payload: HaeisRunPayload): string[] {
  const errors: string[] = [];
  if (!isRecord(payload)) return ['payload must be an object'];
  if (!nonEmptyString(payload?.run_id)) errors.push('run_id is required');
  if (!nonEmptyString(payload?.organization_id)) errors.push('organization_id is required');
  if (!nonEmptyString(payload?.workflow_id)) errors.push('workflow_id is required');
  const runStatuses = new Set<HaeisRunStatus>(['PENDING', 'RUNNING', 'COMPLETED', 'BLOCKED', 'FAILED']);
  if (!payload.status || !runStatuses.has(payload.status as HaeisRunStatus)) errors.push('invalid run status');
  if (!isRecord(payload?.gate_records)) errors.push('gate_records must be an object');
  const gateStatuses = new Set<HaeisGateStatus>(['OPEN', 'PASS', 'BLOCKED']);
  for (const [gateId, gate] of Object.entries(isRecord(payload?.gate_records) ? payload.gate_records : {})) {
    if (!gateId.trim()) errors.push('gate ID must not be empty');
    if (!isRecord(gate)) { errors.push(`gate record must be an object: ${gateId}`); continue; }
    if (!gateStatuses.has(gate.status as HaeisGateStatus)) errors.push(`invalid gate status: ${gateId}`);
    if (!nonEmptyString(gate.owner)) errors.push(`gate owner is required: ${gateId}`);
    if (!Array.isArray(gate.evidence_ids) || gate.evidence_ids.some((id) => typeof id !== 'string' || !id.trim())) errors.push(`gate evidence_ids must be non-empty strings: ${gateId}`);
  }
  if (!Array.isArray(payload.events) || payload.events.length === 0) errors.push('events must be a non-empty array');
  const eventTypes = new Set<HaeisEventType>(['RUN_STARTED', 'NODE_STARTED', 'NODE_FINISHED', 'GATE_UPDATED', 'RUN_FINISHED']);
  const sequences = new Set<number>();
  for (const event of payload.events ?? []) {
    if (!isRecord(event)) { errors.push('event must be an object'); continue; }
    if (!Number.isInteger(event.sequence) || event.sequence < 1 || sequences.has(event.sequence)) errors.push(`event sequence must be a unique positive integer: ${event.sequence}`);
    sequences.add(event.sequence);
    if (!eventTypes.has(event.type as HaeisEventType)) errors.push(`invalid event type: ${event.type}`);
  }
  if (payload.events?.length && [...sequences].sort((a, b) => a - b).some((sequence, index) => sequence !== index + 1)) errors.push('event sequences must be contiguous from 1');
  const reviewStatus = payload.review?.status ?? 'PENDING';
  const reviewStatuses = new Set<HaeisReviewStatus>(['PENDING', 'APPROVED', 'REJECTED']);
  if (!reviewStatuses.has(reviewStatus as HaeisReviewStatus)) errors.push('invalid review status');
  if (reviewStatus === 'APPROVED' && !nonEmptyString(payload.review?.reviewer_id)) errors.push('approved review requires reviewer_id');
  if (payload.status === 'COMPLETED' && (!isRecord(payload.human_review_packet) || payload.human_review_packet.status !== 'AVAILABLE_FOR_REVIEW' || payload.human_review_packet.review_required !== false)) errors.push('completed runs must include an optional post-run review packet; approval is not required');
  if (payload.status === 'COMPLETED' && Object.values(isRecord(payload?.gate_records) ? payload.gate_records : {}).some((gate) => !isRecord(gate) || gate.status !== 'PASS')) errors.push('completed runs require every persisted gate to be PASS');
  return [...new Set(errors)];
}

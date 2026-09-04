import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateHaeisRunPayload } from '../../../control-plane/src/lib/hanke-validation.ts';

test('GLAW D1 migration contains HAEIS run, gate, and event persistence tables', () => {
  const sql = readFileSync(new URL('../../../control-plane/db/migrations/0002_hanke_economics.sql', import.meta.url), 'utf8');
  for (const table of ['hanke_runs', 'hanke_gate_records', 'hanke_run_events']) assert.match(sql, new RegExp(`CREATE TABLE IF NOT EXISTS ${table}`));
  assert.match(sql, /evidence_ids_json/);
});

test('GLAW D1 review migration remains available for post-run review without gating completion', () => {
  const migration = readFileSync(new URL('../../../control-plane/db/migrations/0003_hanke_review.sql', import.meta.url), 'utf8');
  const api = readFileSync(new URL('../../../control-plane/src/pages/api/hanke-runs.ts', import.meta.url), 'utf8');
  const validation = readFileSync(new URL('../../../control-plane/src/lib/hanke-validation.ts', import.meta.url), 'utf8');
  for (const column of ['review_status', 'reviewer_id', 'review_note', 'reviewed_at']) assert.match(migration, new RegExp(`ADD COLUMN ${column}`));
  assert.match(validation, /optional post-run review packet; approval is not required/);
  assert.match(validation, /approved review requires reviewer_id/);
});

test('D1 HAEIS payload validator rejects malformed gates/events and unsafe completion', () => {
  const base = { run_id: 'R-1', organization_id: 'ORG-1', workflow_id: 'W-1', status: 'COMPLETED', gate_records: { 'critical-data': { status: 'OPEN', owner: 'agent', evidence_ids: [] } }, events: [{ sequence: 1, type: 'RUN_FINISHED' }], review: { status: 'PENDING' } };
  const errors = validateHaeisRunPayload(base);
  assert.ok(errors.includes('completed runs must include an optional post-run review packet; approval is not required'));
  assert.ok(errors.includes('completed runs require every persisted gate to be PASS'));
  const complete = { ...base, gate_records: { 'critical-data': { status: 'PASS', owner: 'agent', evidence_ids: ['SRC-1'] } }, human_review_packet: { status: 'AVAILABLE_FOR_REVIEW', review_required: false } };
  assert.deepEqual(validateHaeisRunPayload(complete), []);
  assert.deepEqual(validateHaeisRunPayload({ ...base, status: 'BLOCKED', review: { status: 'PENDING' }, gate_records: { 'critical-data': { status: 'BLOCKED', owner: 'agent', evidence_ids: ['SRC-1'] } } }), []);
  assert.ok(validateHaeisRunPayload({ ...base, status: 'BLOCKED', review: { status: 'PENDING' }, gate_records: { 'critical-data': { status: 'BLOCKED', owner: '', evidence_ids: ['SRC-1'] } }, events: [{ sequence: 2, type: 'NOPE' }] }).length > 0);
  assert.deepEqual(validateHaeisRunPayload(null as never), ['payload must be an object']);
  assert.ok(validateHaeisRunPayload({ ...base, status: 'BLOCKED', events: [null as never] }).some((error) => error === 'event must be an object'));
});

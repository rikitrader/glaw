import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { buildEvidenceLaneReport } from '../src/evidence-lanes.ts';

const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
const plan = JSON.parse(readFileSync(new URL('../intake/venezuela-evidence-search.json', import.meta.url), 'utf8'));

test('Venezuela evidence lanes preserve three dispositions without making a conclusion', () => {
  const report = buildEvidenceLaneReport(plan, documents);
  assert.deepEqual(report.validation_errors, []);
  assert.deepEqual(report.lanes.map((lane) => lane.lane), ['SUPPORTING', 'CONTRADICTORY', 'ALTERNATIVE_EXPLANATION']);
  assert.equal(report.lanes[0].disposition, 'FOUND');
  assert.equal(report.lanes[1].disposition, 'FOUND');
  assert.equal(report.lanes[1].verified_source_ids.length, 3);
  assert.equal(report.lanes[2].disposition, 'FOUND');
  assert.ok(report.lanes.every((lane) => lane.conclusion_status === 'NOT_A_CONCLUSION'));
  assert.equal(report.recommendation_status, 'BLOCKED_PENDING_EVIDENCE_REVIEW');
});

test('evidence lane validation rejects unknown sources and missing lanes', () => {
  const report = buildEvidenceLaneReport({ claim_id: 'bad', searches: [{ lane: 'SUPPORTING', query: 'q', source_ids: ['D-404'], result_status: 'FOUND', notes: 'n' }] }, documents);
  assert.ok(report.validation_errors.some((error) => error.includes('required evidence search lane missing')));
  assert.ok(report.validation_errors.some((error) => error.includes('unknown source')));
});

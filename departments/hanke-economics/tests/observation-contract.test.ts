import test from 'node:test';
import assert from 'node:assert/strict';
import { canonicalizeRedenominatedValue, readinessStatus, validateInstitutionalObservation, validateSourceConflict } from '../src/observation-contract.ts';

const observation = {
  country: 'Venezuela', variable: 'M2', date: '2025-09-30', frequency: 'monthly', value: 514062, unit: 'VES million', currency: 'VES', real_or_nominal: 'NOMINAL', source: 'UNDP report', source_id: 'DOC-VEN-UNDP-Q3-2025', publication_date: '2025-10-01', retrieval_date: '2026-08-25', dataset_id: 'VEN-MONETARY', methodology: 'reported secondary compilation', transformation_applied: [], confidence_score: 0.4, verification_status: 'DISPUTED', revision_status: 'UNKNOWN', domain: 'MONETARY'
} as const;

test('institutional observation requires complete provenance and preserves disputed status', () => {
  assert.deepEqual(validateInstitutionalObservation(observation), []);
  assert.equal(observation.verification_status, 'DISPUTED');
  assert.ok(validateInstitutionalObservation({ ...observation, value: null, verification_status: 'UNAVAILABLE', confidence_score: null }).length === 0);
  assert.ok(validateInstitutionalObservation({ ...observation, source_id: '' }).some((error) => error.includes('source_id')));
});

test('source conflicts are retained as explicit records rather than overwritten', () => {
  const conflict = { conflict_id: 'CONFLICT-1', variable: 'M2', date: '2025-09-30', source_A: 'A', value_A: 10, source_B: 'B', value_B: 12, absolute_difference: 2, percentage_difference: 20, probable_reason: 'different reporting perimeter', preferred_source: null, confidence: 0.3, analyst_note: 'Both versions remain in the registry.' };
  assert.deepEqual(validateSourceConflict(conflict), []);
  assert.ok(validateSourceConflict({ ...conflict, source_B: 'A' }).some((error) => error.includes('differ')));
});

test('redenomination canonicalization requires verified factors and records transformations', () => {
  const result = canonicalizeRedenominatedValue(1000000, '2025-09-30', 'VES', [{ record_id: 'RED-2021', currency: 'VES', effective_date: '2021-10-01', old_units_per_new_unit: 1000000, source_id: 'LAW-1', status: 'VERIFIED', notes: 'verified factor' }]);
  assert.equal(result.value, 1);
  assert.deepEqual(result.transformations, ['RED-2021: divide by 1000000']);
});

test('readiness rubric remains unresolved until every pillar has evidence', () => {
  assert.equal(readinessStatus([]), 'DATA_INSUFFICIENT');
  assert.equal(readinessStatus(Array.from({ length: 9 }, (_, index) => ({ pillar: String(index), weight: 1 / 9, status: 'UNRESOLVED' as const, evidence_ids: [], rationale: 'not verified' }))), 'DATA_INSUFFICIENT');
});

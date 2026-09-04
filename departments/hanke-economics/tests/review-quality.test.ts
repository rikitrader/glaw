import test from 'node:test';
import assert from 'node:assert/strict';
import { buildDataCompletenessDashboard, validateDataCompletenessDashboard, validateEvidenceTable } from '../src/review-quality.ts';

const base = {
  country: 'Venezuela', variable: 'M2', date: '2025-09-30', frequency: 'monthly', value: 10, unit: 'VES million', currency: 'VES', real_or_nominal: 'NOMINAL' as const,
  source: 'source', source_id: 'SRC-1', publication_date: '2025-10-01', retrieval_date: '2026-08-25', dataset_id: 'VEN-MONETARY', methodology: 'reported', transformation_applied: [], confidence_score: 0.4,
  verification_status: 'DISPUTED' as const, revision_status: 'UNKNOWN' as const, domain: 'MONETARY' as const
};

test('completeness dashboard preserves disputed observations and never imputes missing values', () => {
  const rows = buildDataCompletenessDashboard([{ variable: 'M2', domain: 'MONETARY', expected_observations: 2 }], [base], '2026-08-25');
  assert.equal(rows[0].observed_observations, 1);
  assert.equal(rows[0].missing_observations, 1);
  assert.equal(rows[0].status_counts.DISPUTED, 1);
  assert.equal(rows[0].quality, 'ORANGE');
  assert.deepEqual(validateDataCompletenessDashboard(rows), []);
});

test('empty completeness dashboard row is red and explicitly unavailable', () => {
  const rows = buildDataCompletenessDashboard([{ variable: 'M0', domain: 'MONETARY', expected_observations: 1 }], [], '2026-08-25');
  assert.equal(rows[0].coverage_percentage, 0);
  assert.equal(rows[0].quality, 'RED');
  assert.match(rows[0].notes, /No source-bound observation/);
});

test('evidence table rejects an unsupported claim without uncertainty', () => {
  const errors = validateEvidenceTable([{ claim_id: 'C-1', claim: 'unsupported', evidence_supporting: [], evidence_contradicting: [], primary_sources: [], model_result: null, confidence: 'LOW', sensitivity: 'unknown', final_assessment: 'unsupported', uncertainty: '' }]);
  assert.ok(errors.some((error) => error.includes('lacks evidence or uncertainty')));
});

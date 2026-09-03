import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateReadinessIndex, READINESS_PILLARS, validateReadinessEvidence, type ReadinessEvidence } from '../src/readiness-index.ts';

const evidence = (status: ReadinessEvidence['evidence_status'] = 'VERIFIED'): ReadinessEvidence[] => READINESS_PILLARS.map((pillar, index) => ({
  pillar,
  score: 50 + index,
  evidence_status: status,
  evidence_ids: status === 'VERIFIED' ? [`SRC-${pillar}`] : [],
  rationale: `bounded rationale for ${pillar}`
}));

test('readiness index fails closed when any pillar is not verified', () => {
  const items = evidence();
  items[3] = { ...items[3], evidence_status: 'UNAVAILABLE', evidence_ids: [] };
  const result = calculateReadinessIndex(items);
  assert.equal(result.status, 'DATA_INSUFFICIENT');
  assert.equal(result.overall_score, null);
  assert.equal(result.band, 'DATA INSUFFICIENT');
  assert.ok(result.blockers.some((blocker) => blocker.includes('RESERVES')));
});

test('readiness index validates completeness and duplicate pillars', () => {
  const items = evidence().slice(0, -1);
  items.push({ ...items[0] });
  assert.ok(validateReadinessEvidence(items).some((error) => error.includes('duplicate')));
  assert.ok(validateReadinessEvidence(items).some((error) => error.includes('missing')));
});

test('readiness index calculates only from nine verified pillars using declared weights', () => {
  const result = calculateReadinessIndex(evidence());
  assert.equal(result.status, 'CALCULATED');
  assert.equal(result.overall_score, 52.9);
  assert.equal(result.band, 'HIGH RISK');
  assert.deepEqual(result.blockers, []);
});

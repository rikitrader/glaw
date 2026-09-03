import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateConfidence } from '../src/confidence.ts';
import { scoreCourtPosition, summarizeJury } from '../src/economic-court.ts';

test('confidence engine exposes weak dimensions', () => {
  const result = calculateConfidence({ source_quality: 1, source_quantity: 0.2, method_strength: 0.8, consistency: 0.8, freshness: 0.8, uncertainty: 0.2, robustness: 0.7, adversarial_survivability: 0.7 });
  assert.equal(result.label, 'MODERATE');
  assert.ok(result.reasons.length >= 2);
});
test('Economic Court blocks all judges on unresolved critical risk', () => assert.ok(scoreCourtPosition(1, 1, 1, true).every((score) => score.vote === 'INSUFFICIENT EVIDENCE')));
test('Economic Jury preserves advisory vote counts', () => assert.equal(summarizeJury([{ member_id: 'a', role: 'scholar', vote: 'SUPPORT', reasons: [] }, { member_id: 'b', role: 'banker', vote: 'OPPOSE', reasons: [] }, { member_id: 'c', role: 'fiscal', vote: 'SUPPORT', reasons: [] }]).majority, 'SUPPORT'));

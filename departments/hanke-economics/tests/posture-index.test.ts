import test from 'node:test';
import assert from 'node:assert/strict';
import { buildPostureIndex, POSTURES } from '../src/posture-index.ts';

test('posture index creates a complete auditable matrix without inventing assessments', () => {
  const cells = buildPostureIndex(Array.from({ length: 20 }, (_, index) => `case-${index + 1}`));
  assert.equal(cells.length, 20 * POSTURES.length);
  assert.ok(cells.every((cell) => cell.status === 'PENDING_SOURCE_REVIEW' && cell.claims.length === 0));
});

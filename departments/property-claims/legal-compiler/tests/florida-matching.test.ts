import test from 'node:test';
import assert from 'node:assert/strict';
import { runFloridaMatching } from '../research/florida-matching.ts';

test('Florida matching runs the official-source pipeline and remains human-gated for case/policy review', async () => {
  const result = await runFloridaMatching('2026-03-15');
  assert.equal(result.request.jurisdiction, 'FL');
  assert.equal(result.request.issue, 'MATCHING');
  assert.equal(result.gates[0].status, 'PASSED');
  assert.equal(result.gates[2].status, 'PASSED');
  assert.equal(result.rules.length, 1);
  assert.equal(result.status, 'COMPLETE_WITH_REVIEW');
  assert.equal(result.activated.length, 0);
  assert.ok(result.blockers.some((blocker) => blocker.includes('human review')));
});

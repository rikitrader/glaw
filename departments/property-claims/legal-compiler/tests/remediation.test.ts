import test from 'node:test';
import assert from 'node:assert/strict';
import { buildRemediationMatrix, summarizeRemediation } from '../remediation/matrix.ts';
import { createSourceSnapshot, verifySnapshot } from '../sources/snapshot.ts';
import { getJurisdictionStatus } from '../core/status.ts';

test('remediation matrix covers every registered jurisdiction and core issue', () => {
  const matrix = buildRemediationMatrix();
  assert.equal(matrix.length, 51 * 13);
  assert.equal(summarizeRemediation(matrix).RESEARCH_REQUIRED_NO_PRIMARY_SOURCE, 663);
});

test('source snapshots are content-addressed and tamper-evident', () => {
  const snapshot = createSourceSnapshot({ snapshotId: 'S-1', authorityId: 'A-1', retrievedAt: '2026-09-01', sourceUrl: 'https://example.gov', officialSource: true, sourceType: 'STATE_STATUTE', content: 'verified excerpt', parserVersion: 'v1', verified: false, verificationNotes: [] });
  assert.equal(verifySnapshot(snapshot), true);
  assert.equal(verifySnapshot({ ...snapshot, content: 'changed' }), false);
});

test('Florida status exposes staged source-backed work without clearing queue', () => {
  const status = getJurisdictionStatus(new URL('../jurisdictions/', import.meta.url).pathname, 'FL');
  assert.equal(status.status, 'PARTIAL');
  assert.equal(status.verifiedSources, 4);
  assert.ok(status.queue.length > 0);
});

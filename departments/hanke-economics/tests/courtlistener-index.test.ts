import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { validateCourtListenerIndex, type CourtListenerIndex } from '../src/courtlistener-index.ts';

const index = JSON.parse(readFileSync(new URL('../legal/courtlistener-venezuela-index.json', import.meta.url), 'utf8')) as CourtListenerIndex;

test('CourtListener queue validates and remains separate from economic observations', () => {
  assert.deepEqual(validateCourtListenerIndex(index), []);
  assert.equal(index.source, 'CourtListener');
  assert.ok(index.records.length >= 3);
  assert.ok(index.records.every((record) => record.economic_observation_eligible === false));
});

test('unverified CourtListener records cannot claim local legal verification', () => {
  const unverified = index.records.filter((record) => record.status !== 'VERIFIED');
  assert.ok(unverified.length >= 1);
  assert.ok(unverified.every((record) => !record.local_path && !record.sha256 && !record.citation_anchor));
});

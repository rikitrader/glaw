import test from 'node:test';
import assert from 'node:assert/strict';
import { compareObservations } from '../src/vintage.ts';

test('vintage comparison rejects mismatched units and dates', () => {
  const base = { series_id: 'M2', observation_date: '2024-06-30', release_date: '2024-07-15', source_document_id: 'S-1', value: 1, unit: 'VES', revision_date: '2024-08-01' };
  assert.equal(compareObservations(base, { ...base, unit: 'USD' }).comparable, false);
});

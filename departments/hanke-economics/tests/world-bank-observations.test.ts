import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateInstitutionalObservation } from '../src/observation-contract.ts';

const observations = JSON.parse(readFileSync(new URL('../datasets/venezuela-world-bank-observations.json', import.meta.url), 'utf8')).observations;
const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;

test('World Bank context observations are source-bound and individually valid', () => {
  assert.ok(observations.length > 0);
  const verified = new Set(documents.filter((document: { status: string }) => document.status === 'VERIFIED').map((document: { document_id: string }) => document.document_id));
  for (const observation of observations) {
    assert.deepEqual(validateInstitutionalObservation(observation), []);
    assert.ok(verified.has(observation.source_id), observation.source_id);
    assert.equal(observation.publication_date, null);
    assert.equal(observation.verification_status, 'VERIFIED');
  }
});

test('World Bank context remains bounded and cannot satisfy monetary reform inputs', () => {
  assert.ok(observations.every((observation: { notes: string }) => observation.notes.includes('does not populate BCV')));
  assert.ok(observations.every((observation: { domain: string }) => ['MACRO', 'OIL', 'EXTERNAL'].includes(observation.domain)));
});

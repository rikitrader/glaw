import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateInstitutionalObservation } from '../src/observation-contract.ts';

const observations = JSON.parse(readFileSync(new URL('../datasets/venezuela-imf-mfs-observations.json', import.meta.url), 'utf8')).observations;
const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;

test('IMF MFS observations preserve exact historical SDMX source scope', () => {
  assert.equal(observations.length, 2324);
  const verified = new Set(documents.filter((document: { status: string }) => document.status === 'VERIFIED').map((document: { document_id: string }) => document.document_id));
  for (const observation of observations) {
    assert.deepEqual(validateInstitutionalObservation(observation), []);
    assert.ok(verified.has(observation.source_id), observation.source_id);
    assert.equal(observation.unit, 'XDC (provider-defined)');
    assert.equal(observation.currency, null);
    assert.equal(observation.publication_date, null);
    assert.equal(observation.frequency, 'monthly');
    assert.match(observation.notes, /Historical-only/);
  }
});

test('IMF MFS adapter does not relabel provider-defined series as current aggregates', () => {
  assert.ok(observations.every((observation: { notes: string }) => observation.notes.includes('cannot satisfy current Venezuela intake gates')));
  assert.ok(observations.some((observation: { variable: string }) => observation.variable === 'monetary_base'));
  assert.ok(observations.some((observation: { variable: string }) => observation.variable === 'historical_MFS_ODC_loans'));
});

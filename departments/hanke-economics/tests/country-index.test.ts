import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('country index contains every user-supplied episode and every required posture', () => {
  const index = JSON.parse(readFileSync(new URL('../country-cases/index.json', import.meta.url), 'utf8')) as { episodes: Array<Record<string, unknown>>; requiredPostures: string[] };
  assert.ok(index.episodes.length >= 20);
  assert.equal(new Set(index.episodes.map((episode) => episode.id)).size, index.episodes.length);
  assert.ok(index.episodes.some((episode) => episode.id === 'bulgaria-1996-97'));
  for (const episode of index.episodes) {
    for (const field of ['problem', 'hyperinflation_assessment', 'relevance_to_venezuela', 'stabilization', 'hanke_sources', 'counter_sources', 'data_requirements', 'non_comparabilities', 'posture_status']) assert.ok(field in episode, `${episode.id} missing ${field}`);
  }
  assert.equal(index.requiredPostures.length, 14);
});

test('source index contains both verified downloads and restricted-source handling', () => {
  const index = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')) as { documents: Array<Record<string, unknown>> };
  assert.ok(index.documents.some((document) => document.status === 'VERIFIED' && document.local_path));
  assert.ok(index.documents.some((document) => document.status === 'RESTRICTED' && document.local_path === null));
  const worldEconomics = index.documents.find((document) => document.document_id === 'DOC-HANKE-WEJ-VEN-HYPER-2017');
  assert.equal(worldEconomics?.status, 'VERIFIED');
  assert.equal(worldEconomics?.document_type, 'bibliographic-record');
  assert.equal(worldEconomics?.primary_source, false);
  const forbes = index.documents.find((document) => document.document_id === 'DOC-HANKE-FORBES-VEN-DOLLAR-2017');
  assert.equal(forbes?.status, 'VERIFIED');
  assert.match(String(forbes?.notes), /metered-access|metered/i);
});

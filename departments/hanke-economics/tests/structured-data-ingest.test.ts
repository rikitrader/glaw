import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { ingestStructuredData } from '../src/structured-data-ingest.ts';

const source = { document_id: 'IMF-MFS-CBS-VEN', title: 'synthetic verified provider response', author: ['International Monetary Fund'], source_url: 'https://data.example.test/mfs', status: 'VERIFIED', local_path: 'documents/acquired/IMF-MFS-CBS-VEN.json', citation_anchor: 'API query response; dataset and dimensions recorded', authority_level: 2, sha256: '' } as const;
const makeSource = (raw: string) => ({ ...source, sha256: createHash('sha256').update(new TextEncoder().encode(raw)).digest('hex') });
const options = (raw: string) => ({ source_document_id: source.document_id, artifact_sha256: createHash('sha256').update(new TextEncoder().encode(raw)).digest('hex'), format: 'json' as const, citation_anchor: 'API response: dataset=MFS_CBS; country=VEN; returned observation row' });

test('structured provider JSON becomes hash-bound dated observations', () => {
  const raw = JSON.stringify({ data: [{ name: 'monetary base', series_id: 'BCV_MONETARY_BASE', value: '123.5', unit: 'VES million', observation_date: '2024-12-31', release_date: '2025-02-15', revision_date: '2025-03-01', vintage: '2025-03-01' }] });
  const result = ingestStructuredData(raw, [makeSource(raw)], options(raw));
  assert.equal(result.observations[0].value, 123.5);
  assert.deepEqual(result.observations[0].source_ids, ['IMF-MFS-CBS-VEN']);
  assert.equal(result.artifact_sha256, options(raw).artifact_sha256);
});

test('structured provider CSV supports explicit row metadata', () => {
  const raw = 'name,series_id,value,unit,observation_date,release_date\nM2,BCV_M2,900,VEN million,2024-12-31,2025-02-15\n';
  const csvOptions = { ...options(raw), format: 'csv' as const };
  const result = ingestStructuredData(raw, [makeSource(raw)], csvOptions);
  assert.equal(result.observations[0].series_id, 'BCV_M2');
  assert.equal(result.observations[0].value, 900);
});

test('structured provider ingestion fails closed for restricted sources, bad hashes, and missing release dates', () => {
  const raw = JSON.stringify([{ name: 'M2', series_id: 'BCV_M2', value: 1, unit: 'VES', observation_date: '2024-01-01', release_date: '2024-02-01' }]);
  assert.throws(() => ingestStructuredData(raw, [{ ...makeSource(raw), status: 'RESTRICTED' }], options(raw)), /not verified/);
  assert.throws(() => ingestStructuredData(raw, [makeSource(raw)], { ...options(raw), artifact_sha256: '0'.repeat(64) }), /SHA-256 mismatch/);
  const missingRelease = JSON.stringify([{ name: 'M2', series_id: 'BCV_M2', value: 1, unit: 'VES', observation_date: '2024-01-01' }]);
  assert.throws(() => ingestStructuredData(missingRelease, [makeSource(missingRelease)], options(missingRelease)), /requires release_date/);
});

test('structured provider ingestion rejects duplicate series/date observations', () => {
  const raw = JSON.stringify([{ name: 'M2', series_id: 'BCV_M2', value: 1, unit: 'VES', observation_date: '2024-01-01', release_date: '2024-02-01' }, { name: 'M2', series_id: 'BCV_M2', value: 2, unit: 'VES', observation_date: '2024-01-01', release_date: '2024-02-01' }]);
  assert.throws(() => ingestStructuredData(raw, [makeSource(raw)], options(raw)), /duplicate structured observation/);
});

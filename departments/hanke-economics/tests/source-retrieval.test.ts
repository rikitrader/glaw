import test from 'node:test';
import assert from 'node:assert/strict';
import { retrievePublicSource, type RetrievalResponse } from '../src/source-retrieval.ts';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { persistRetrievedSource } from '../src/source-persistence.ts';
import { acquireIndexedDocument } from '../src/source-acquisition.ts';

const response = (body: string, status = 200, contentType = 'application/pdf'): RetrievalResponse => ({ ok: status >= 200 && status < 300, status, headers: { get: () => contentType }, arrayBuffer: async () => new TextEncoder().encode(body).buffer });

test('retrieval admits public PDF as FOUND but not VERIFIED', async () => {
  const result = await retrievePublicSource('https://example.test/a.pdf', async () => response('%PDF-1.7 body'));
  assert.equal(result.status, 'FOUND');
  assert.equal(result.is_pdf, true);
});
test('retrieval preserves anti-bot and HTTP failures as restricted', async () => {
  const result = await retrievePublicSource('https://example.test/a.pdf', async () => response('<html>blocked</html>', 403, 'text/html'));
  assert.equal(result.status, 'RESTRICTED');
  assert.equal(result.body, null);
});
test('successful HTTP status with provider error HTML is restricted', async () => {
  const result = await retrievePublicSource('https://example.test/provider-error', async () => response('<html><title>Error</title>This page can\'t be displayed. Incident ID: 123</html>', 200, 'text/html'));
  assert.equal(result.status, 'RESTRICTED');
  assert.equal(result.body, null);
});
test('successful HTTP status with a provider 404 page is restricted', async () => {
  const result = await retrievePublicSource('https://example.test/missing.pdf', async () => response('<!doctype html><html><head><title>404</title></head><body>not found</body></html>', 200, 'text/html'));
  assert.equal(result.status, 'RESTRICTED');
  assert.equal(result.body, null);
});
test('retrieval blocks insecure sources', async () => assert.equal((await retrievePublicSource('http://example.test/a.pdf', async () => response('%PDF-'))).status, 'RESTRICTED'));

test('retrieval admits valid public JSON and CSV as FOUND with provider format flags', async () => {
  const json = await retrievePublicSource('https://example.test/data.json', async () => response('{"data":[{"value":1}]}', 200, 'application/json'));
  assert.equal(json.status, 'FOUND'); assert.equal(json.is_json, true); assert.equal(json.is_csv, false);
  const csv = await retrievePublicSource('https://example.test/data.csv', async () => response('series_id,value\nGDP,1', 200, 'text/csv'));
  assert.equal(csv.status, 'FOUND'); assert.equal(csv.is_csv, true); assert.equal(csv.is_json, false);
});

test('malformed public JSON is restricted rather than admitted as evidence', async () => {
  const result = await retrievePublicSource('https://example.test/bad.json', async () => response('{"data":', 200, 'application/json'));
  assert.equal(result.status, 'RESTRICTED'); assert.equal(result.body, null); assert.match(result.reason, /malformed JSON/);
});

test('JSON persistence preserves provider format in the artifact extension', async () => {
  const result = await retrievePublicSource('https://example.test/data.json', async () => response('{"data":[]}', 200, 'application/json'));
  const persisted = persistRetrievedSource(result, mkdtempSync(join(tmpdir(), 'haeis-json-')), 'DOC-JSON-001');
  assert.match(persisted.local_path, /DOC-JSON-001\.json$/);
  assert.equal(readFileSync(persisted.local_path).toString(), '{"data":[]}');
});

test('retrieval converts transport failures into auditable restricted results', async () => {
  const result = await retrievePublicSource('https://example.test/unreachable.pdf', async () => { throw new Error('DNS unavailable'); });
  assert.equal(result.status, 'RESTRICTED');
  assert.equal(result.http_status, 0);
  assert.match(result.reason, /DNS unavailable/);
});

test('successful retrieval persists a hashed FOUND artifact without upgrading verification', async () => {
  const body = new TextEncoder().encode('%PDF-1.7 test body');
  const result = await retrievePublicSource('https://example.test/source.pdf', async () => ({ ok: true, status: 200, headers: { get: (name: string) => name === 'content-type' ? 'application/pdf' : null }, arrayBuffer: async () => body.buffer }));
  const persisted = persistRetrievedSource(result, mkdtempSync(join(tmpdir(), 'haeis-source-')), 'DOC-TEST-001');
  assert.equal(persisted.status, 'FOUND'); assert.equal(persisted.bytes, body.byteLength); assert.equal(readFileSync(persisted.local_path).toString(), '%PDF-1.7 test body'); assert.equal(persisted.sha256.length, 64);
});

test('changed bytes persist as a versioned artifact without overwriting the prior hash', async () => {
  const root = mkdtempSync(join(tmpdir(), 'haeis-version-'));
  const first = await retrievePublicSource('https://example.test/versioned.pdf', async () => response('%PDF-1.7 first'));
  const second = await retrievePublicSource('https://example.test/versioned.pdf', async () => response('%PDF-1.7 second'));
  const a = persistRetrievedSource(first, root, 'DOC-VERSION-001');
  const b = persistRetrievedSource(second, root, 'DOC-VERSION-001');
  assert.notEqual(a.local_path, b.local_path);
  assert.equal(readFileSync(a.local_path).toString(), '%PDF-1.7 first');
  assert.equal(readFileSync(b.local_path).toString(), '%PDF-1.7 second');
});

test('restricted retrieval cannot be persisted', async () => {
  const result = await retrievePublicSource('https://example.test/restricted.pdf', async () => response('blocked', 403, 'text/html'));
  assert.throws(() => persistRetrievedSource(result, tmpdir(), 'DOC-TEST-002'), /only successful public retrievals/);
});

test('indexed acquisition persists a FOUND artifact but never upgrades verification', async () => {
  const result = await acquireIndexedDocument({ document_id: 'DOC-ACQ-001', title: 'test', source_url: 'https://example.test/acq.pdf', status: 'KNOWN' }, {
    artifactRoot: mkdtempSync(join(tmpdir(), 'haeis-acq-')),
    now: () => '2026-01-01T00:00:00.000Z',
    fetchImpl: async () => response('%PDF-1.7 acquired')
  });
  assert.equal(result.attempt.resulting_status, 'FOUND');
  assert.equal(result.attempt.verification_required, true);
  assert.equal(result.attempt.previous_status, 'KNOWN');
  assert.ok(result.persisted?.sha256);
});

test('indexed acquisition records restricted and missing sources without creating evidence', async () => {
  const restricted = await acquireIndexedDocument({ document_id: 'DOC-ACQ-002', title: 'restricted', source_url: 'https://example.test/blocked.pdf', status: 'FOUND' }, {
    artifactRoot: mkdtempSync(join(tmpdir(), 'haeis-acq-')),
    fetchImpl: async () => response('blocked', 403, 'text/html')
  });
  assert.equal(restricted.attempt.resulting_status, 'RESTRICTED');
  assert.equal(restricted.persisted, null);
  const missing = await acquireIndexedDocument({ document_id: 'DOC-ACQ-003', title: 'missing', source_url: '', status: 'MISSING' }, {
    artifactRoot: mkdtempSync(join(tmpdir(), 'haeis-acq-')),
    fetchImpl: async () => response('%PDF-1.7')
  });
  assert.equal(missing.attempt.resulting_status, 'MISSING');
  assert.equal(missing.retrieved, null);
});

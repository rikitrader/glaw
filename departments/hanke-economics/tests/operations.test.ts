import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, mkdtempSync } from 'node:fs';
import { inspectLocalDocument } from '../src/document-ingest.ts';
import { HAEIS_CATALOG, toHaeisControlPlanePayload, validateCatalog } from '../src/control-plane.ts';
import { runWorkflow } from '../src/workflow.ts';
import { validateHaeisRunPayload } from '../../../control-plane/src/lib/hanke-validation.ts';
import { requirePdfAnchor } from '../src/pdf-anchors.ts';
import { validateDocumentRegistry } from '../src/document-registry.ts';
import { defaultRunPath, runAndPersistWorkflow } from '../src/durable-runner.ts';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

test('verified downloaded PDF passes magic-byte and hash inspection', () => {
  const result = inspectLocalDocument(new URL('../documents/imf-wp-2007-099-zimbabwe-high-inflation.pdf', import.meta.url).pathname);
  assert.equal(result.mime, 'application/pdf');
  assert.equal(result.valid, true);
  assert.equal(result.sha256.length, 64);
});
test('HTML anti-bot response cannot enter the PDF corpus', () => {
  const result = inspectLocalDocument(new URL('../rag/README.md', import.meta.url).pathname);
  assert.equal(result.valid, true);
  assert.equal(result.mime, 'text/plain');
});
test('verified extracted PDF resolves physical page anchors', () => {
  const text = readFileSync(new URL('../extracted/imf-wp-2007-099-zimbabwe-high-inflation.txt', import.meta.url), 'utf8');
  assert.deepEqual(requirePdfAnchor(text, 'money growth'), [10, 11]);
  assert.ok(requirePdfAnchor(text, 'Achieving Macroeconomic Stabilization in Zimbabwe').includes(10));
});

test('verified SAE 232–234 PDFs have matching local hashes and framework anchors', () => {
  const index = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8'));
  for (const id of ['PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234']) {
    const document = index.documents.find((candidate: { document_id: string }) => candidate.document_id === id);
    assert.equal(document.status, 'VERIFIED');
    const integrity = inspectLocalDocument(new URL(`../${document.local_path}`, import.meta.url).pathname);
    assert.equal(integrity.valid, true);
    assert.equal(integrity.sha256, document.sha256);
    const extracted = readFileSync(new URL(`../${document.text_path}`, import.meta.url), 'utf8');
    assert.ok(requirePdfAnchor(extracted, 'Golden Growth').length > 0);
    assert.ok(requirePdfAnchor(extracted, 'Credit Counterpart').length > 0);
  }
});
test('document registry rejects duplicate IDs, paths, hashes, and incomplete verified versions', () => {
  const errors = validateDocumentRegistry({ documents: [
    { document_id: 'D-1', title: 'a', source_url: 'https://a', status: 'VERIFIED', local_path: 'a.pdf', sha256: 'same' },
    { document_id: 'D-1', title: 'b', source_url: 'https://b', status: 'VERIFIED', local_path: 'a.pdf', sha256: 'same' },
    { document_id: 'D-3', title: 'c', source_url: 'https://c', status: 'VERIFIED', local_path: null, sha256: null }
  ] });
  assert.ok(errors.some((error) => error.includes('duplicate document_id')));
  assert.ok(errors.some((error) => error.includes('duplicate local_path')));
  assert.ok(errors.some((error) => error.includes('duplicate sha256')));
  assert.ok(errors.some((error) => error.includes('lacks local_path')));
});
test('current document index has no registry collisions', () => {
  const index = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8'));
  assert.deepEqual(validateDocumentRegistry(index), []);
});
test('control-plane catalog resolves all declared paths', () => {
  assert.deepEqual(validateCatalog((path) => HAEIS_CATALOG.some((entry) => entry.path === path)), []);
  for (const required of ['hanke-agent-manifest', 'hanke-red-team-manifest', 'hanke-blue-team-manifest', 'hanke-posture-evidence', 'hanke-legal-index', 'hanke-benchmark-catalog', 'hanke-venezuela-disputed-context-intake']) assert.ok(HAEIS_CATALOG.some((entry) => entry.id === required));
});

test('durable workflow runner persists complete run state and JSONL events', async () => {
  const root = mkdtempSync(join(tmpdir(), 'haeis-run-'));
  const eventPath = join(root, 'run.events.jsonl');
  const definition = { id: 'DURABLE-1', version: '1', nodes: [{ id: 'start', executor: 'start' }], edges: [], required_gates: [], stop_conditions: [] };
  const run = await runAndPersistWorkflow(definition, { start: () => ({ status: 'PASS', artifacts: { audit_marker: 'persisted' } }) }, 'RUN-DURABLE-1', eventPath);
  const runPath = defaultRunPath(eventPath);
  assert.equal(existsSync(eventPath), true);
  assert.equal(existsSync(runPath), true);
  const persisted = JSON.parse(readFileSync(runPath, 'utf8'));
  assert.equal(persisted.run_id, run.run_id);
  assert.equal(persisted.artifacts.audit_marker, 'persisted');
  assert.equal(persisted.events.length, run.events.length);
  assert.equal(readFileSync(eventPath, 'utf8').trim().split('\n').length, run.events.length);
});

test('GLAW adapter converts a blocked HAEIS run into an API-valid payload without requiring human approval', async () => {
  const definition = { id: 'ADAPTER-1', version: '1', nodes: [{ id: 'block', executor: 'block' }], edges: [], required_gates: ['critical'], stop_conditions: [] };
  const run = await runWorkflow(definition, { block: () => ({ status: 'BLOCKED', reason: 'evidence required', gate_updates: { critical: 'BLOCKED' }, gate_evidence: { critical: { owner: 'test', evidence_ids: ['SRC-1'] } } }) }, { run_id: 'RUN-ADAPTER-1' });
  const payload = toHaeisControlPlanePayload(run, 'ORG-1', 'MATTER-1');
  assert.deepEqual(validateHaeisRunPayload(payload), []);
  assert.equal(payload.status, 'BLOCKED');
  assert.equal(payload.gate_records.critical.status, 'BLOCKED');
  assert.equal(payload.gate_records.critical.evidence_ids[0], 'SRC-1');
  assert.equal(payload.human_review_packet, undefined);
});

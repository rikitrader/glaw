import test from 'node:test';
import assert from 'node:assert/strict';
import { promoteFoundSource } from '../src/source-verification.ts';

const found = { document_id: 'DOC-FOUND', title: 'Found', author: ['Author'], source_url: 'https://example.org/source.pdf', status: 'FOUND' as const, local_path: 'documents/acquired/DOC-FOUND.pdf', citation_anchor: null, authority_level: 1 };
const integrity = { path: found.local_path, bytes: 100, mime: 'application/pdf' as const, sha256: 'a'.repeat(64), valid: true, reason: 'PDF magic bytes verified.' };

test('only a valid FOUND artifact with an anchor can become VERIFIED', () => {
  const verified = promoteFoundSource(found, integrity, { citation_anchor: 'p. 4, section 2', verification_note: 'hash and PDF integrity checked', verified_at: '2026-08-25T23:00:00.000Z' });
  assert.equal(verified.status, 'VERIFIED');
  assert.equal(verified.sha256, integrity.sha256);
});

test('restricted, invalid, or unanchored sources cannot be promoted', () => {
  assert.throws(() => promoteFoundSource({ ...found, status: 'RESTRICTED' }, integrity, { citation_anchor: 'p. 1', verification_note: 'x', verified_at: '2026-08-25T23:00:00.000Z' }), /only FOUND/);
  assert.throws(() => promoteFoundSource(found, { ...integrity, valid: false }, { citation_anchor: 'p. 1', verification_note: 'x', verified_at: '2026-08-25T23:00:00.000Z' }), /failed integrity/);
  assert.throws(() => promoteFoundSource(found, integrity, { citation_anchor: '', verification_note: 'x', verified_at: '2026-08-25T23:00:00.000Z' }), /citation_anchor/);
});

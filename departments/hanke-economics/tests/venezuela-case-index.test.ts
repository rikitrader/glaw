import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const index = JSON.parse(readFileSync(new URL('../legal/venezuela-case-index.json', import.meta.url), 'utf8')) as {
  case_records: Array<{ case_id: string; status: string; amounts: Array<{ status: string; value: number | null }>; evidence_items: Array<{ status: string; local_path: string | null; sha256: string | null }> }>;
  source_registry: Array<{ source_id: string }>;
};

test('Venezuela case index preserves evidence, amounts, and non-double-counting structure', () => {
  assert.ok(index.case_records.length >= 4);
  assert.ok(index.source_registry.length >= 6);
  assert.equal(new Set(index.case_records.map((record) => record.case_id)).size, index.case_records.length);
  assert.ok(index.case_records.every((record) => record.evidence_items.length > 0));
  assert.ok(index.case_records.flatMap((record) => record.amounts).every((amount) => amount.status === 'VERIFIED' ? amount.value !== null : true));
});

test('verified case evidence has local artifact and hash', () => {
  for (const record of index.case_records.filter((candidate) => candidate.status === 'VERIFIED')) {
    for (const evidence of record.evidence_items.filter((candidate) => candidate.status === 'VERIFIED')) {
      assert.ok(evidence.local_path);
      assert.match(String(evidence.sha256), /^[a-f0-9]{64}$/);
    }
  }
});

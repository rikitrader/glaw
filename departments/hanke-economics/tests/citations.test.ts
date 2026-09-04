import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveCitation, validateSourceReferences, type IndexedDocument } from '../src/citations.ts';
import { validateEvidenceSearchPlan } from '../src/evidence-search.ts';
import { readFileSync } from 'node:fs';
import { validateEvidenceGraph } from '../src/evidence-graph.ts';

const documents: IndexedDocument[] = [
  { document_id: 'D-1', title: 'Verified Hanke paper', author: ['Steve H. Hanke'], source_url: 'https://example.test/paper.pdf', status: 'VERIFIED', local_path: 'documents/paper.pdf', citation_anchor: 'p. 2', authority_level: 1 },
  { document_id: 'D-2', title: 'Found paper', author: ['Other Author'], source_url: 'https://example.test/other.pdf', status: 'FOUND', local_path: null, citation_anchor: null, authority_level: 2 }
];

test('verified direct Hanke citation resolves only with locator and anchor', () => assert.equal(resolveCitation({ document_id: 'D-1', locator: 'p. 2, section 3', claim_label: 'HANKE-DIRECT' }, documents).status, 'VERIFIED'));
test('unverified documents block citation', () => assert.equal(resolveCitation({ document_id: 'D-2', locator: 'p. 1', claim_label: 'EXTERNAL-VIEW' }, documents).status, 'BLOCKED'));
test('unknown source references are rejected', () => assert.deepEqual(validateSourceReferences(['D-1', 'D-404'], documents), ['D-404']));

test('verified bibliographic metadata cannot support direct Hanke attribution', () => {
  const metadata = [{ document_id: 'META-1', title: 'metadata', author: ['Steve H. Hanke'], source_url: 'https://example.test/meta', status: 'VERIFIED', local_path: 'documents/meta.html', citation_anchor: 'title', authority_level: 4, document_type: 'bibliographic-record' }] as never;
  const result = resolveCitation({ document_id: 'META-1', locator: 'metadata title', claim_label: 'HANKE-DIRECT' }, metadata);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason, /primary Hanke publication/);
});

test('anti-confirmation search plan requires support, contradiction, and alternatives', () => {
  const plan = { claim_id: 'C-1', searches: [
    { lane: 'SUPPORTING' as const, query: 'supporting query', source_ids: ['D-1'], result_status: 'FOUND' as const, notes: 'support reviewed' },
    { lane: 'CONTRADICTORY' as const, query: 'contradictory query', source_ids: [], result_status: 'NO_RESULT' as const, notes: 'no result recorded' },
    { lane: 'ALTERNATIVE_EXPLANATION' as const, query: 'alternative query', source_ids: [], result_status: 'RESTRICTED' as const, notes: 'restricted source recorded' }
  ] };
  assert.deepEqual(validateEvidenceSearchPlan(plan, documents), []);
});

test('anti-confirmation search plan blocks missing lanes and unknown sources', () => {
  const errors = validateEvidenceSearchPlan({ claim_id: 'C-2', searches: [{ lane: 'SUPPORTING', query: 'q', source_ids: ['D-404'], result_status: 'FOUND', notes: 'n' }] }, []);
  assert.ok(errors.some((error) => error.includes('CONTRADICTORY')));
  assert.ok(errors.some((error) => error.includes('ALTERNATIVE_EXPLANATION')));
  assert.ok(errors.some((error) => error.includes('unknown source')));
});

test('claim-evidence graph has no dangling nodes or edges', () => {
  const graph = JSON.parse(readFileSync(new URL('../rag/claim-evidence-graph.json', import.meta.url), 'utf8'));
  assert.deepEqual(validateEvidenceGraph(graph), []);
  assert.ok(graph.nodes.length > 0);
  assert.ok(graph.edges.length > 0);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { runAdversarialLoop, validatePostureAssessment, type PostureAssessment } from '../src/posture-review.ts';
import { readFileSync } from 'node:fs';
import { validateEvidenceBoundAssessment } from '../src/posture-store.ts';

const assessment: PostureAssessment = { case_id: 'ecuador-1998-2000', posture_id: 'hanke', shared_facts: ['banking crisis documented'], assumptions: ['liquidity is constrained'], mechanism: 'credibility may improve while banking liquidity remains binding', supporting_evidence: ['DOC-IMF-008'], contradictory_evidence: [], falsifiers: ['verified excess liquidity'], claims: [], assessment: 'SUPPORT_WITH_CONDITIONS', confidence: 'LOW' };

test('posture assessment requires mechanism and falsifiers', () => assert.deepEqual(validatePostureAssessment(assessment), []));
test('critical unresolved risk blocks adversarial conclusion', () => {
  const result = runAdversarialLoop(assessment, 'strongest argument', [{ finding_id: 'F-1', criticism: 'liquidity failure', attacked_assumption: 'liquidity', evidence_against: ['D-1'], severity: 'CRITICAL', status: 'UNRESOLVED' }], [], []);
  assert.equal(result.final_status, 'BLOCKED');
});
test('resolved red-blue-red loop survives', () => {
  const finding = { finding_id: 'F-1', criticism: 'minor issue', attacked_assumption: 'timing', evidence_against: ['D-1'], severity: 'LOW' as const, status: 'RESOLVED' as const };
  const result = runAdversarialLoop(assessment, 'strongest argument', [finding], [{ finding_id: 'F-1', defense: 'sequencing', evidence_for_defense: ['D-2'], residual_risk: 'low', status: 'RESOLVED' }], [finding]);
  assert.equal(result.final_status, 'SURVIVES');
});

test('evidence-backed posture fixture binds claims to verified sources and anchors', () => {
  const fixture = JSON.parse(readFileSync(new URL('../postures/evidence-backed-assessments.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  assert.deepEqual(validateEvidenceBoundAssessment(fixture.assessments[0], documents), []);
});

test('Hanke posture cannot be promoted from the restricted Hanke table', () => {
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const hankeAssessment = { ...assessment, posture_id: 'hanke' as const, assessment: 'INSUFFICIENT_EVIDENCE' as const, claims: [{ text: 'blocked', label: 'HANKE-DIRECT' as const, source_ids: ['DOC-HK-001'], citation_anchors: ['table; page not established'] }] };
  assert.ok(validateEvidenceBoundAssessment(hankeAssessment, documents).some((error) => error.includes('non-verified source')));
});

test('Hanke claims cannot bind to verified bibliographic metadata', () => {
  const documents = [{ document_id: 'META-1', title: 'metadata', author: ['Steve H. Hanke'], source_url: 'https://example.test/meta', status: 'VERIFIED', local_path: 'documents/meta.html', citation_anchor: 'title', authority_level: 4, document_type: 'bibliographic-record' }] as never;
  const errors = validateEvidenceBoundAssessment({ case_id: 'C-1', posture_id: 'hanke', shared_facts: ['metadata only'], assumptions: ['full text is unavailable'], mechanism: 'No framework conclusion is supportable from metadata alone.', supporting_evidence: ['META-1'], contradictory_evidence: [], falsifiers: ['Primary text is verified.'], claims: [{ text: 'unsupported direct claim', label: 'HANKE-DIRECT', source_ids: ['META-1'], citation_anchors: ['title'] }], assessment: 'INSUFFICIENT_EVIDENCE', confidence: 'VERY LOW' }, documents);
  assert.ok(errors.some((error) => error.includes('primary publication')));
});

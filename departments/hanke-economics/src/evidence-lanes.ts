import type { IndexedDocument } from './citations.ts';
import { validateEvidenceSearchPlan, type EvidenceSearchPlan, type EvidenceSearchLane } from './evidence-search.ts';

export interface EvidenceLaneRecord {
  lane: EvidenceSearchLane;
  searches: EvidenceSearchPlan['searches'];
  source_ids: string[];
  verified_source_ids: string[];
  restricted_source_ids: string[];
  disposition: 'FOUND' | 'RESTRICTED' | 'NO_RESULT' | 'PENDING';
  conclusion_status: 'NOT_A_CONCLUSION';
}

export interface EvidenceLaneReport {
  claim_id: string;
  lanes: EvidenceLaneRecord[];
  validation_errors: string[];
  recommendation_status: 'BLOCKED_PENDING_EVIDENCE_REVIEW';
  rule: string;
}

const requiredLanes: EvidenceSearchLane[] = ['SUPPORTING', 'CONTRADICTORY', 'ALTERNATIVE_EXPLANATION'];

export function buildEvidenceLaneReport(plan: EvidenceSearchPlan, documents: IndexedDocument[]): EvidenceLaneReport {
  const validation_errors = validateEvidenceSearchPlan(plan, documents);
  const byId = new Map(documents.map((document) => [document.document_id, document]));
  const lanes = requiredLanes.map((lane) => {
    const searches = plan.searches.filter((search) => search.lane === lane);
    const source_ids = [...new Set(searches.flatMap((search) => search.source_ids))];
    const verified_source_ids = source_ids.filter((id) => byId.get(id)?.status === 'VERIFIED');
    const restricted_source_ids = source_ids.filter((id) => byId.get(id)?.status !== 'VERIFIED');
    const statuses = searches.map((search) => search.result_status);
    const disposition: EvidenceLaneRecord['disposition'] = statuses.includes('FOUND') ? 'FOUND' : statuses.includes('RESTRICTED') ? 'RESTRICTED' : statuses.includes('PENDING') ? 'PENDING' : 'NO_RESULT';
    return { lane, searches, source_ids, verified_source_ids, restricted_source_ids, disposition, conclusion_status: 'NOT_A_CONCLUSION' as const };
  });
  return {
    claim_id: plan.claim_id,
    lanes,
    validation_errors,
    recommendation_status: 'BLOCKED_PENDING_EVIDENCE_REVIEW',
    rule: 'Lane disposition records the evidence search state only; it never converts a source into a policy conclusion or upgrades restricted evidence.'
  };
}

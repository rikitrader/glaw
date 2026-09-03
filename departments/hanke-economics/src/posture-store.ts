import type { IndexedDocument } from './citations.ts';
import { POSTURES, type PostureId } from './posture-index.ts';
import { validatePostureAssessment, type PostureAssessment } from './posture-review.ts';

export interface EvidenceBoundClaim {
  text: string;
  label: PostureAssessment['claims'][number]['label'];
  source_ids: string[];
  citation_anchors: string[];
}

export interface EvidenceBoundAssessment extends Omit<PostureAssessment, 'claims'> {
  claims: EvidenceBoundClaim[];
}

/** Bind posture claims to verified source records; source IDs alone are not citation proof. */
export function validateEvidenceBoundAssessment(assessment: EvidenceBoundAssessment, documents: IndexedDocument[]): string[] {
  const errors = validatePostureAssessment(assessment);
  if (!POSTURES.includes(assessment.posture_id as PostureId)) errors.push('unknown posture');
  const byId = new Map(documents.map((document) => [document.document_id, document]));
  for (const claim of assessment.claims) {
    if (!claim.citation_anchors.length) errors.push(`claim requires citation anchors: ${claim.text}`);
    for (const sourceId of claim.source_ids) {
      const source = byId.get(sourceId);
      if (!source) errors.push(`claim references unknown source: ${sourceId}`);
      else if (source.status !== 'VERIFIED') errors.push(`claim references non-verified source: ${sourceId}`);
      else if ((claim.label === 'HANKE-DIRECT' || claim.label === 'HANKE-FRAMEWORK') && (source.document_type === 'bibliographic-record' || source.primary_source === false)) errors.push(`Hanke claim requires a verified primary publication: ${sourceId}`);
    }
  }
  return errors;
}

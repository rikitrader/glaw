import type { IndexedDocument } from './citations.ts';

export type EvidenceSearchLane = 'SUPPORTING' | 'CONTRADICTORY' | 'ALTERNATIVE_EXPLANATION';
export interface EvidenceSearchRecord { lane: EvidenceSearchLane; query: string; source_ids: string[]; result_status: 'FOUND' | 'NO_RESULT' | 'RESTRICTED' | 'PENDING'; notes: string; }
export interface EvidenceSearchPlan { claim_id: string; searches: EvidenceSearchRecord[]; }

export function validateEvidenceSearchPlan(plan: EvidenceSearchPlan, documents: IndexedDocument[]): string[] {
  const errors: string[] = []; const lanes = new Set(plan.searches.map((search) => search.lane));
  for (const lane of ['SUPPORTING', 'CONTRADICTORY', 'ALTERNATIVE_EXPLANATION'] as const) if (!lanes.has(lane)) errors.push(`required evidence search lane missing: ${lane}`);
  const known = new Set(documents.map((document) => document.document_id));
  for (const search of plan.searches) { if (!search.query) errors.push(`${search.lane} search query is required`); for (const sourceId of search.source_ids) if (!known.has(sourceId)) errors.push(`evidence search references unknown source: ${sourceId}`); if (!search.notes) errors.push(`${search.lane} search notes are required`); }
  return errors;
}

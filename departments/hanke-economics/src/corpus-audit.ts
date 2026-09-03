import type { IndexedDocument } from './citations.ts';

export interface CorpusCaseReference { id: string; hanke_sources: string[]; counter_sources: string[]; }
export interface CorpusAuditResult { complete: boolean; checked_cases: number; unknown_source_ids: string[]; restricted_source_ids: string[]; found_source_ids: string[]; verified_source_ids: string[]; cases_with_gaps: Array<{ case_id: string; missing: string[]; restricted: string[]; unverified: string[] }>; }

export function auditCorpus(cases: CorpusCaseReference[], documents: IndexedDocument[]): CorpusAuditResult {
  const byId = new Map(documents.map((document) => [document.document_id, document])); const unknown = new Set<string>(); const restricted = new Set<string>(); const found = new Set<string>(); const verified = new Set<string>(); const casesWithGaps = [] as CorpusAuditResult['cases_with_gaps'];
  const verifiedSupersessions = new Map<string, string>();
  for (const document of documents) if (document.status === 'VERIFIED') {
    for (const supersededId of document.supersedes ?? []) verifiedSupersessions.set(supersededId, document.document_id);
    for (const boundedId of document.bounded_replacement_for ?? []) verifiedSupersessions.set(boundedId, document.document_id);
  }
  for (const countryCase of cases) {
    const missing: string[] = []; const caseRestricted: string[] = []; const unverified: string[] = [];
    for (const sourceId of [...countryCase.hanke_sources, ...countryCase.counter_sources]) {
      const document = byId.get(sourceId);
      if (!document) { unknown.add(sourceId); missing.push(sourceId); continue; }
      if (document.status === 'VERIFIED') verified.add(sourceId); else if (document.status === 'RESTRICTED') {
        const replacement = verifiedSupersessions.get(sourceId);
        if (replacement) verified.add(replacement); else { restricted.add(sourceId); caseRestricted.push(sourceId); }
      } else { found.add(sourceId); unverified.push(sourceId); }
    }
    if (missing.length || caseRestricted.length || unverified.length) casesWithGaps.push({ case_id: countryCase.id, missing, restricted: caseRestricted, unverified });
  }
  return { complete: casesWithGaps.length === 0, checked_cases: cases.length, unknown_source_ids: [...unknown], restricted_source_ids: [...restricted], found_source_ids: [...found], verified_source_ids: [...verified], cases_with_gaps: casesWithGaps };
}

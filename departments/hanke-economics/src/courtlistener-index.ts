export type CourtListenerRecordStatus = 'FOUND' | 'RESTRICTED' | 'VERIFIED';

export interface CourtListenerRecord {
  record_id: string;
  title: string;
  court: string;
  date_filed: string;
  citation: string;
  docket_number: string;
  record_type: string;
  courtlistener_url: string;
  volume_url: string;
  status: CourtListenerRecordStatus;
  economic_domains: string[];
  economic_observation_eligible: false;
  verification_notes: string;
  local_path?: string;
  sha256?: string;
  citation_anchor?: string;
}

export interface CourtListenerIndex {
  schemaVersion: string;
  status: string;
  source: 'CourtListener';
  purpose: string;
  economicObservationRule: string;
  records: CourtListenerRecord[];
  retrieval_policy: string;
}

export function validateCourtListenerIndex(index: CourtListenerIndex): string[] {
  const errors: string[] = [];
  const seen = new Set<string>();
  for (const record of index.records) {
    if (seen.has(record.record_id)) errors.push(`duplicate record_id: ${record.record_id}`);
    seen.add(record.record_id);
    if (!/^https:\/\/(www\.)?courtlistener\.com\//.test(record.courtlistener_url)) {
      errors.push(`non-CourtListener URL: ${record.record_id}`);
    }
    if (record.economic_observation_eligible !== false) {
      errors.push(`court record cannot be an economic observation: ${record.record_id}`);
    }
    if (record.status === 'VERIFIED' && (!record.local_path || !record.sha256 || !record.citation_anchor)) {
      errors.push(`verified CourtListener record lacks local artifact/hash/anchor: ${record.record_id}`);
    }
  }
  return errors;
}

import { createHash } from 'node:crypto';

export interface SourceSnapshot {
  snapshotId: string;
  authorityId: string;
  retrievedAt: string;
  sourceUrl: string;
  officialSource: boolean;
  sourceType: 'STATE_STATUTE' | 'ADMINISTRATIVE_REGULATION' | 'STATE_CASE' | 'AGENCY_GUIDANCE' | 'OTHER';
  content: string;
  sha256: string;
  parserVersion: string;
  verified: boolean;
  verificationNotes: string[];
}

export function createSourceSnapshot(input: Omit<SourceSnapshot, 'sha256'>): SourceSnapshot {
  return { ...input, sha256: createHash('sha256').update(input.content, 'utf8').digest('hex') };
}

export function verifySnapshot(snapshot: SourceSnapshot): boolean {
  return snapshot.sha256 === createHash('sha256').update(snapshot.content, 'utf8').digest('hex');
}

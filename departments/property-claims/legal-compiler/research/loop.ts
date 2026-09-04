import type { LegalIssueCode, LegalAuthority, LegalProposition, CompiledLegalRule } from '../types/index.ts';
import { createSourceSnapshot, type SourceSnapshot } from '../sources/snapshot.ts';

export interface ResearchRequest { jurisdiction: string; issue: LegalIssueCode; effectiveDate: string; }
export interface ResearchProvider {
  discoverOfficialSources(request: ResearchRequest): Promise<string[]>;
  retrieve(url: string): Promise<{ content: string; retrievedAt: string; sourceType: SourceSnapshot['sourceType']; } | null>;
}
export interface ResearchResult {
  request: ResearchRequest;
  verified: boolean;
  sources: SourceSnapshot[];
  authorities: LegalAuthority[];
  propositions: LegalProposition[];
  rules: CompiledLegalRule[];
  failureReason?: string;
  missing: string[];
}

export async function remediateLegalIssue(
  request: ResearchRequest,
  provider: ResearchProvider,
): Promise<ResearchResult> {
  const urls = await provider.discoverOfficialSources(request);
  const sources: SourceSnapshot[] = [];
  for (const url of urls) {
    const fetched = await provider.retrieve(url);
    if (fetched) sources.push(createSourceSnapshot({
      snapshotId: `${request.jurisdiction.toLowerCase()}-${request.issue.toLowerCase()}-${sources.length + 1}`,
      authorityId: 'PENDING_AUTHORITY_LINK',
      retrievedAt: fetched.retrievedAt,
      sourceUrl: url,
      officialSource: true,
      sourceType: fetched.sourceType,
      content: fetched.content,
      parserVersion: 'pclc-source-parser-v1',
      verified: false,
      verificationNotes: ['snapshot persisted; authority identity and proposition verification pending'],
    }));
  }
  const missing: string[] = [];
  if (!urls.length) missing.push('official source URL');
  if (!sources.length) missing.push('retrievable source content');
  missing.push('authority identity', 'citation verification', 'temporal verification', 'compiled rule review');
  return { request, verified: false, sources, authorities: [], propositions: [], rules: [], failureReason: 'research pipeline requires authority-specific parsing and verification before activation', missing };
}

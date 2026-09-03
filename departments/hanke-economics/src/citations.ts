export interface IndexedDocument { document_id: string; title: string; author: string[]; source_url: string; status: 'KNOWN' | 'FOUND' | 'INGESTED' | 'INDEXED' | 'VERIFIED' | 'MISSING' | 'RESTRICTED'; local_path: string | null; citation_anchor: string | null; authority_level: number; sha256?: string | null; document_type?: string; primary_source?: boolean; notes?: string; supersedes?: string[]; bounded_replacement_for?: string[]; }
export interface CitationRequest { document_id: string; locator: string; claim_label: string; }
export interface ResolvedCitation { document_id: string; title: string; locator: string; source_url: string; authority_level: number; status: 'VERIFIED' | 'BLOCKED'; reason: string; }

export function resolveCitation(request: CitationRequest, documents: IndexedDocument[]): ResolvedCitation {
  const document = documents.find((item) => item.document_id === request.document_id);
  if (!document) return { document_id: request.document_id, title: '', locator: request.locator, source_url: '', authority_level: 7, status: 'BLOCKED', reason: 'SOURCE REQUIRED — document ID is not registered' };
  if (document.status !== 'VERIFIED') return { document_id: document.document_id, title: document.title, locator: request.locator, source_url: document.source_url, authority_level: document.authority_level, status: 'BLOCKED', reason: `SOURCE NOT VERIFIED — status is ${document.status}` };
  if (!document.source_url || !request.locator) return { document_id: document.document_id, title: document.title, locator: request.locator, source_url: document.source_url, authority_level: document.authority_level, status: 'BLOCKED', reason: 'CITATION BLOCKED — source URL and locator are required' };
  if (request.claim_label === 'HANKE-DIRECT' && (document.document_type === 'bibliographic-record' || document.primary_source === false || !document.author.some((author) => author.toLowerCase().includes('hanke')) || !document.citation_anchor)) return { document_id: document.document_id, title: document.title, locator: request.locator, source_url: document.source_url, authority_level: document.authority_level, status: 'BLOCKED', reason: 'ATTRIBUTION BLOCKED — a verified primary Hanke publication with a citation anchor is required' };
  return { document_id: document.document_id, title: document.title, locator: request.locator, source_url: document.source_url, authority_level: document.authority_level, status: 'VERIFIED', reason: 'Verified document and locator.' };
}

export function validateSourceReferences(sourceIds: string[], documents: IndexedDocument[]): string[] {
  const known = new Set(documents.map((document) => document.document_id));
  return sourceIds.filter((sourceId) => !known.has(sourceId));
}

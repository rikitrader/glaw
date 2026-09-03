import type { IndexedDocument } from './citations.ts';
import type { LocalDocumentIntegrity } from './document-ingest.ts';

export interface SourceVerificationMetadata {
  citation_anchor: string;
  verification_note: string;
  verified_at: string;
}

export function promoteFoundSource(document: IndexedDocument, integrity: LocalDocumentIntegrity, metadata: SourceVerificationMetadata): IndexedDocument {
  if (document.status !== 'FOUND') throw new Error(`only FOUND artifacts may be promoted; ${document.document_id} is ${document.status}`);
  if (!integrity.valid) throw new Error(`local artifact failed integrity inspection: ${integrity.reason}`);
  if (!document.local_path) throw new Error('FOUND document must have local_path before promotion');
  if (!integrity.sha256) throw new Error('local artifact hash is required');
  if (!metadata.citation_anchor.trim()) throw new Error('citation_anchor is required');
  if (!metadata.verification_note.trim()) throw new Error('verification_note is required');
  if (!/^\d{4}-\d{2}-\d{2}T/.test(metadata.verified_at)) throw new Error('verified_at must be an ISO timestamp');
  return { ...document, status: 'VERIFIED', sha256: integrity.sha256, citation_anchor: metadata.citation_anchor.trim(), notes: [document.notes, metadata.verification_note.trim(), `Verified at ${metadata.verified_at}`].filter(Boolean).join(' ') };
}

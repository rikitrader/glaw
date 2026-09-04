import type { SourceStatus } from './types.ts';

export interface RegistryDocument {
  document_id: string;
  title: string;
  source_url: string;
  status: SourceStatus;
  local_path?: string | null;
  sha256?: string | null;
  version_id?: string | null;
  supersedes_document_id?: string | null;
}

export interface DocumentRegistry { documents: RegistryDocument[]; }

/** Detect collisions before an index is ingested into RAG or durable storage. */
export function validateDocumentRegistry(registry: DocumentRegistry): string[] {
  const errors: string[] = [];
  const ids = new Set<string>();
  const paths = new Map<string, string>();
  const hashes = new Map<string, string>();
  for (const document of registry.documents) {
    if (ids.has(document.document_id)) errors.push(`duplicate document_id: ${document.document_id}`);
    ids.add(document.document_id);
    if (document.local_path) {
      const previous = paths.get(document.local_path);
      if (previous) errors.push(`duplicate local_path: ${document.local_path} (${previous}, ${document.document_id})`);
      paths.set(document.local_path, document.document_id);
    }
    if (document.sha256) {
      const previous = hashes.get(document.sha256);
      if (previous) errors.push(`duplicate sha256 requires explicit version review: ${document.sha256}`);
      hashes.set(document.sha256, document.document_id);
    }
    if (document.status === 'VERIFIED' && (!document.local_path || !document.sha256)) errors.push(`verified document lacks local_path or sha256: ${document.document_id}`);
    if (document.supersedes_document_id && document.supersedes_document_id === document.document_id) errors.push(`document cannot supersede itself: ${document.document_id}`);
  }
  return errors;
}

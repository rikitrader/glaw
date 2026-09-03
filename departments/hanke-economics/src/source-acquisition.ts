import type { RegistryDocument } from './document-registry.ts';
import { persistRetrievedSource, type PersistedSource } from './source-persistence.ts';
import { retrievePublicSource, type RetrievalResponse, type RetrievedSource } from './source-retrieval.ts';

export interface AcquisitionAttempt {
  document_id: string;
  source_url: string | null;
  previous_status: RegistryDocument['status'];
  resulting_status: 'MISSING' | 'RESTRICTED' | 'FOUND';
  attempted_at: string;
  http_status: number;
  content_type: string;
  bytes: number;
  local_path: string | null;
  sha256: string | null;
  reason: string;
  verification_required: true;
}

export interface AcquisitionResult {
  attempt: AcquisitionAttempt;
  retrieved: RetrievedSource | null;
  persisted: PersistedSource | null;
}

export interface AcquisitionOptions {
  fetchImpl: (url: string) => Promise<RetrievalResponse>;
  artifactRoot: string;
  now?: () => string;
}

/**
 * Acquire one catalog record under the HAEIS lawful-source boundary.
 *
 * This function deliberately does not mutate the document index and cannot
 * produce VERIFIED. Local integrity, metadata, page/section anchors, and
 * independent citation review remain separate steps.
 */
export async function acquireIndexedDocument(document: RegistryDocument, options: AcquisitionOptions): Promise<AcquisitionResult> {
  const attemptedAt = options.now?.() ?? new Date().toISOString();
  if (!document.source_url) {
    return {
      attempt: { document_id: document.document_id, source_url: null, previous_status: document.status, resulting_status: 'MISSING', attempted_at: attemptedAt, http_status: 0, content_type: '', bytes: 0, local_path: null, sha256: null, reason: 'No lawful public source URL is recorded.', verification_required: true },
      retrieved: null,
      persisted: null
    };
  }

  const retrieved = await retrievePublicSource(document.source_url, options.fetchImpl);
  if (retrieved.status !== 'FOUND') {
    return {
      attempt: { document_id: document.document_id, source_url: document.source_url, previous_status: document.status, resulting_status: 'RESTRICTED', attempted_at: attemptedAt, http_status: retrieved.http_status, content_type: retrieved.content_type, bytes: retrieved.bytes, local_path: null, sha256: null, reason: retrieved.reason, verification_required: true },
      retrieved,
      persisted: null
    };
  }

  const persisted = persistRetrievedSource(retrieved, options.artifactRoot, document.document_id);
  return {
    attempt: { document_id: document.document_id, source_url: document.source_url, previous_status: document.status, resulting_status: 'FOUND', attempted_at: attemptedAt, http_status: retrieved.http_status, content_type: retrieved.content_type, bytes: retrieved.bytes, local_path: persisted.local_path, sha256: persisted.sha256, reason: 'Artifact persisted; local integrity and citation verification remain required.', verification_required: true },
    retrieved,
    persisted
  };
}

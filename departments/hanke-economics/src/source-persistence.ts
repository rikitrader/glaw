import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import type { RetrievedSource } from './source-retrieval.ts';

export interface PersistedSource { status: 'FOUND'; local_path: string; sha256: string; bytes: number; source_url: string; content_type: string; }
const safeId = (value: string) => value.replace(/[^a-zA-Z0-9._-]+/g, '_');

/** Persist a retrieved public artifact without upgrading it to VERIFIED. */
export function persistRetrievedSource(retrieved: RetrievedSource, rootDir: string, documentId: string): PersistedSource {
  if (retrieved.status !== 'FOUND' || !retrieved.body) throw new Error('only successful public retrievals with a body may be persisted');
  const extension = retrieved.is_pdf ? '.pdf' : retrieved.is_json ? '.json' : retrieved.is_csv ? '.csv' : '.html'; const basePath = join(rootDir, `${safeId(documentId)}${extension}`); const bytes = retrieved.body;
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  let path = basePath;
  if (existsSync(path)) {
    const existing = createHash('sha256').update(readFileSync(path)).digest('hex');
    if (existing !== sha256) path = join(rootDir, `${safeId(documentId)}-${sha256.slice(0, 12)}${extension}`);
  }
  if (!existsSync(path)) { mkdirSync(rootDir, { recursive: true }); writeFileSync(path, bytes); }
  return { status: 'FOUND', local_path: path, sha256, bytes: bytes.byteLength, source_url: retrieved.url, content_type: retrieved.content_type };
}

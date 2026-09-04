import { appendFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { acquireIndexedDocument } from '../src/source-acquisition.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const documentId = process.argv[2];
if (!documentId) {
  console.error('Usage: node scripts/acquire-source.mjs DOC-ID');
  process.exit(2);
}

const index = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8'));
const document = index.documents.find((candidate) => candidate.document_id === documentId);
if (!document) {
  console.error(JSON.stringify({ status: 'MISSING', document_id: documentId, reason: 'document_id is not in rag/document-index.json' }));
  process.exit(1);
}

const result = await acquireIndexedDocument(document, {
  artifactRoot: resolve(root, 'documents/acquired'),
  fetchImpl: async (url) => {
    const response = await fetch(url, { redirect: 'follow' });
    return {
      ok: response.ok,
      status: response.status,
      headers: response.headers,
      arrayBuffer: () => response.arrayBuffer()
    };
  }
});

const auditPath = resolve(root, 'rag/acquisition-attempts.jsonl');
mkdirSync(dirname(auditPath), { recursive: true });
appendFileSync(auditPath, `${JSON.stringify(result.attempt)}\n`, 'utf8');
console.log(JSON.stringify(result.attempt, null, 2));
process.exit(result.attempt.resulting_status === 'FOUND' ? 0 : 1);

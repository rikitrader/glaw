import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { acquireIndexedDocument } from '../src/source-acquisition.ts';

const root = resolve(new URL('..', import.meta.url).pathname);
const index = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8'));
const attempts = [];

for (const document of index.documents) {
  try {
    const result = await acquireIndexedDocument(document, {
      artifactRoot: resolve(root, 'documents/acquired'),
      fetchImpl: async (url) => {
        const response = await fetch(url, { redirect: 'follow' });
        return { ok: response.ok, status: response.status, headers: response.headers, arrayBuffer: () => response.arrayBuffer() };
      }
    });
    attempts.push(result.attempt);
  } catch (error) {
    attempts.push({ document_id: document.document_id, source_url: document.source_url ?? null, previous_status: document.status, resulting_status: 'RESTRICTED', attempted_at: new Date().toISOString(), http_status: 0, content_type: '', bytes: 0, local_path: null, sha256: null, reason: `Acquisition exception: ${error instanceof Error ? error.message : String(error)}`, verification_required: true });
  }
}

const summary = {
  generated_at: new Date().toISOString(),
  rule: 'Sequential acquisition only; this summary never upgrades a source to VERIFIED.',
  total: attempts.length,
  by_status: Object.fromEntries(['MISSING', 'RESTRICTED', 'FOUND'].map((status) => [status, attempts.filter((attempt) => attempt.resulting_status === status).length])),
  attempts
};
writeFileSync(resolve(root, 'rag/acquisition-batch-summary.json'), JSON.stringify(summary, null, 2), 'utf8');
console.log(JSON.stringify({ total: summary.total, by_status: summary.by_status, summary_path: 'rag/acquisition-batch-summary.json' }, null, 2));
process.exit(summary.by_status.RESTRICTED || summary.by_status.MISSING ? 1 : 0);

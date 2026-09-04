import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ingestStructuredData } from '../src/structured-data-ingest.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourceDocumentId, rawPath, format, citationAnchor] = process.argv.slice(2);
if (!sourceDocumentId || !rawPath || !['json', 'csv'].includes(format) || !citationAnchor) {
  console.error('Usage: node scripts/ingest-structured-data.mjs SOURCE-DOCUMENT-ID RAW-FILE json|csv "CITATION ANCHOR"');
  process.exit(2);
}

const index = JSON.parse(readFileSync(resolve(root, 'rag/document-index.json'), 'utf8'));
const document = index.documents.find((candidate) => candidate.document_id === sourceDocumentId);
if (!document) {
  console.error(JSON.stringify({ status: 'BLOCKED', reason: `source document is not registered: ${sourceDocumentId}` }));
  process.exit(1);
}
if (document.status !== 'VERIFIED' || !document.sha256) {
  console.error(JSON.stringify({ status: 'BLOCKED', reason: `source document is not verified with a hash: ${sourceDocumentId}` }));
  process.exit(1);
}

try {
  const result = ingestStructuredData(readFileSync(resolve(root, rawPath)), [document], { source_document_id: sourceDocumentId, artifact_sha256: document.sha256, format, citation_anchor: citationAnchor, verified_at: new Date().toISOString() });
  console.log(JSON.stringify(result, null, 2));
} catch (error) {
  console.error(JSON.stringify({ status: 'BLOCKED', reason: error instanceof Error ? error.message : String(error) }));
  process.exit(1);
}

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { inspectLocalDocument, inspectLocalHtmlDocument } from '../src/document-ingest.ts';
import { promoteFoundSource } from '../src/source-verification.ts';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const documentId = process.argv[2];
const citationAnchor = process.argv.find((value) => value.startsWith('--anchor='))?.slice('--anchor='.length);
const verificationNote = process.argv.find((value) => value.startsWith('--note='))?.slice('--note='.length);
if (!documentId || !citationAnchor || !verificationNote) {
  console.error('Usage: node scripts/verify-found-source.mjs DOC-ID --anchor="page/section locator" --note="verification basis"');
  process.exit(2);
}
const indexPath = resolve(root, 'rag/document-index.json');
const index = JSON.parse(readFileSync(indexPath, 'utf8'));
const document = index.documents.find((candidate) => candidate.document_id === documentId);
if (!document) throw new Error(`document not found: ${documentId}`);
if (!document.local_path) throw new Error(`document has no local_path: ${documentId}`);
const localPath = resolve(root, document.local_path);
const integrity = document.document_type?.includes('html') ? inspectLocalHtmlDocument(localPath, []) : inspectLocalDocument(localPath);
const verified = promoteFoundSource(document, integrity, { citation_anchor: citationAnchor, verification_note: verificationNote, verified_at: new Date().toISOString() });
index.documents = index.documents.map((candidate) => candidate.document_id === documentId ? verified : candidate);
writeFileSync(indexPath, `${JSON.stringify(index, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ document_id: documentId, status: verified.status, sha256: verified.sha256, citation_anchor: verified.citation_anchor }, null, 2));

import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';

export interface LocalDocumentIntegrity { path: string; bytes: number; mime: 'application/pdf' | 'text/html' | 'text/plain' | 'unknown'; sha256: string; valid: boolean; reason: string; }

export function inspectLocalDocument(path: string): LocalDocumentIntegrity {
  const bytes = readFileSync(path); const sha256 = createHash('sha256').update(bytes).digest('hex'); const size = statSync(path).size;
  const isPdf = bytes.subarray(0, 5).toString() === '%PDF-'; const text = bytes.subarray(0, 512).toString('utf8').toLowerCase();
  if (isPdf) return { path, bytes: size, mime: 'application/pdf', sha256, valid: true, reason: 'PDF magic bytes verified.' };
  if (text.includes('<html') || text.includes('<!doctype html')) return { path, bytes: size, mime: 'text/html', sha256, valid: false, reason: 'HTML response is not a document archive PDF.' };
  if (text.length > 0) return { path, bytes: size, mime: 'text/plain', sha256, valid: true, reason: 'Text document inspected; page-level PDF anchors unavailable.' };
  return { path, bytes: size, mime: 'unknown', sha256, valid: false, reason: 'Unknown or empty document.' };
}

/** Inspect a lawful HTML source separately from the PDF/anti-bot path. */
export function inspectLocalHtmlDocument(path: string, requiredMarkers: string[] = []): LocalDocumentIntegrity {
  const bytes = readFileSync(path); const sha256 = createHash('sha256').update(bytes).digest('hex'); const size = statSync(path).size;
  const text = bytes.toString('utf8'); const lower = text.toLowerCase();
  if (!(lower.includes('<html') || lower.includes('<!doctype html'))) return { path, bytes: size, mime: 'unknown', sha256, valid: false, reason: 'HTML marker is missing.' };
  if (/(access denied|just a moment\.\.\.|captcha|cloudflare ray id|error 403)/i.test(text)) return { path, bytes: size, mime: 'text/html', sha256, valid: false, reason: 'HTML appears to be an access or anti-bot response.' };
  const missing = requiredMarkers.filter((marker) => !text.includes(marker));
  if (missing.length) return { path, bytes: size, mime: 'text/html', sha256, valid: false, reason: `Required HTML content markers are missing: ${missing.join(', ')}` };
  return { path, bytes: size, mime: 'text/html', sha256, valid: true, reason: 'Content-bearing HTML source and required markers verified.' };
}

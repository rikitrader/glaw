import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';

export type LegalStatus = 'UNVERIFIED' | 'FOUND' | 'VERIFIED' | 'RESTRICTED';

export interface LegalInstrumentRecord {
  instrument_id: string;
  jurisdiction: string;
  title: string;
  official_source_url: string | null;
  authoritative_source_url?: string | null;
  source_class?: 'official' | 'authoritative_reporter_copy' | 'translation' | 'consolidated_text';
  status: LegalStatus;
  local_path?: string | null;
  sha256?: string | null;
  text_path?: string | null;
  citation_anchor?: string | null;
}

/** Legal records are leads until the operative text is locally inspected and anchored. */
export function validateLegalInstrument(record: LegalInstrumentRecord): string[] {
  const errors: string[] = [];
  if (record.status === 'VERIFIED') {
    if (!record.official_source_url && !record.authoritative_source_url) errors.push('verified legal instrument requires official_source_url or authoritative_source_url');
    if (!record.local_path) errors.push('verified legal instrument requires local_path');
    if (!record.sha256) errors.push('verified legal instrument requires sha256');
    if (!record.citation_anchor) errors.push('verified legal instrument requires citation_anchor');
  }
  if (record.status === 'FOUND' && record.citation_anchor) errors.push('FOUND legal instrument cannot expose a final citation_anchor');
  if (record.status === 'RESTRICTED' && record.local_path) errors.push('restricted legal instrument cannot have local_path');
  return errors;
}

export function legalRelianceAllowed(record: LegalInstrumentRecord): boolean {
  return record.status === 'VERIFIED' && validateLegalInstrument(record).length === 0;
}

export interface LocalLegalVerification { valid: boolean; sha256: string | null; bytes: number; errors: string[]; }

/** Verify a locally acquired legal text without confusing acquisition with legal reliance. */
export function verifyLocalLegalText(record: LegalInstrumentRecord): LocalLegalVerification {
  const errors: string[] = [];
  if (!record.local_path || !existsSync(record.local_path)) return { valid: false, sha256: null, bytes: 0, errors: ['local legal text is missing'] };
  const bytes = readFileSync(record.local_path) as Uint8Array;
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (record.sha256 && record.sha256 !== sha256) errors.push(`local hash mismatch: expected ${record.sha256}, got ${sha256}`);
  if (!record.citation_anchor) errors.push('citation_anchor is required for local legal verification');
  else {
    const textPath = record.text_path ?? record.local_path;
    if (!existsSync(textPath)) errors.push(`legal text extraction is missing: ${textPath}`);
    else {
      const text = new TextDecoder().decode(readFileSync(textPath) as Uint8Array);
      for (const anchor of record.citation_anchor.split(';').map((part) => part.trim()).filter(Boolean)) if (!text.includes(anchor)) errors.push(`citation anchor not found in local text: ${anchor}`);
    }
  }
  return { valid: errors.length === 0, sha256, bytes: bytes.byteLength, errors };
}

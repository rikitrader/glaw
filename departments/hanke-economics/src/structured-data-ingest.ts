import { createHash } from 'node:crypto';
import type { IndexedDocument } from './citations.ts';

export interface StructuredObservation {
  name: string;
  status: 'KNOWN';
  value: number;
  unit: string;
  series_id: string;
  observation_date: string;
  release_date: string;
  revision_date?: string;
  vintage?: string;
  source_ids: string[];
  citation_anchor: string;
}

export interface StructuredDataIngestOptions {
  source_document_id: string;
  artifact_sha256: string;
  format: 'json' | 'csv';
  citation_anchor: string;
  verified_at?: string;
}

export interface StructuredDataIngestResult {
  artifact_sha256: string;
  source_document_id: string;
  ingested_at: string;
  verified_at?: string;
  observations: StructuredObservation[];
}

const datePattern = /^\d{4}-\d{2}-\d{2}$/;

function isDate(value: unknown): value is string {
  if (typeof value !== 'string' || !datePattern.test(value)) return false;
  const [year, month, day] = value.split('-').map(Number);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return parsed.getUTCFullYear() === year && parsed.getUTCMonth() === month - 1 && parsed.getUTCDate() === day;
}

function bytesOf(raw: string | Uint8Array): Uint8Array {
  return typeof raw === 'string' ? new TextEncoder().encode(raw) : raw;
}

function parseCsv(raw: string): Record<string, unknown>[] {
  const lines = raw.replace(/^\uFEFF/, '').split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (lines.length < 2) throw new Error('structured data CSV requires a header and at least one row');
  const split = (line: string) => {
    const values: string[] = []; let value = ''; let quoted = false;
    for (let index = 0; index < line.length; index += 1) {
      const character = line[index];
      if (character === '"' && line[index + 1] === '"' && quoted) { value += '"'; index += 1; continue; }
      if (character === '"') { quoted = !quoted; continue; }
      if (character === ',' && !quoted) { values.push(value.trim()); value = ''; continue; }
      value += character;
    }
    if (quoted) throw new Error('structured data CSV contains an unterminated quoted field');
    values.push(value.trim());
    return values;
  };
  const headers = split(lines[0]);
  if (headers.some((header) => !header)) throw new Error('structured data CSV has an empty header');
  if (new Set(headers).size !== headers.length) throw new Error('structured data CSV has duplicate headers');
  return lines.slice(1).map((line) => {
    const values = split(line);
    if (values.length !== headers.length) throw new Error('structured data CSV row does not match header width');
    return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
  });
}

function parseRows(raw: string | Uint8Array, format: StructuredDataIngestOptions['format']): Record<string, unknown>[] {
  const text = new TextDecoder().decode(bytesOf(raw));
  if (format === 'csv') return parseCsv(text);
  let parsed: unknown;
  try { parsed = JSON.parse(text); } catch { throw new Error('structured data JSON is invalid'); }
  const rows = Array.isArray(parsed) ? parsed : parsed && typeof parsed === 'object' && Array.isArray((parsed as { data?: unknown }).data) ? (parsed as { data: unknown[] }).data : null;
  if (!rows || rows.some((row) => !row || typeof row !== 'object' || Array.isArray(row))) throw new Error('structured data JSON must be an array of row objects or an object with a data array');
  return rows as Record<string, unknown>[];
}

function requiredString(row: Record<string, unknown>, field: string, index: number): string {
  const value = row[field];
  if (typeof value !== 'string' || !value.trim()) throw new Error(`structured observation ${index} requires ${field}`);
  return value.trim();
}

/**
 * Converts an immutable, hash-identified provider response into source-bound
 * intake observations. It intentionally does not accept restricted sources or
 * infer release dates, units, series IDs, or citation locators.
 */
export function ingestStructuredData(raw: string | Uint8Array, documents: IndexedDocument[], options: StructuredDataIngestOptions): StructuredDataIngestResult {
  const source = documents.find((document) => document.document_id === options.source_document_id);
  if (!source) throw new Error(`structured data source is not registered: ${options.source_document_id}`);
  if (source.status !== 'VERIFIED') throw new Error(`structured data source is not verified: ${options.source_document_id}`);
  if (!source.local_path || !source.sha256 || !source.source_url) throw new Error(`structured data source lacks immutable provenance: ${options.source_document_id}`);
  if (!options.citation_anchor.trim()) throw new Error('structured data requires a citation anchor');
  const bytes = bytesOf(raw);
  const artifactSha256 = createHash('sha256').update(bytes).digest('hex');
  if (artifactSha256 !== options.artifact_sha256) throw new Error('structured data artifact SHA-256 mismatch');
  if (source.sha256 !== artifactSha256) throw new Error('structured data artifact hash does not match the verified source record');
  const rows = parseRows(raw, options.format);
  const seen = new Set<string>();
  const observations = rows.map((row, index): StructuredObservation => {
    const seriesId = requiredString(row, 'series_id', index);
    const name = requiredString(row, 'name', index);
    const unit = requiredString(row, 'unit', index);
    const observationDate = requiredString(row, 'observation_date', index);
    const releaseDate = requiredString(row, 'release_date', index);
    const citationAnchor = typeof row.citation_anchor === 'string' && row.citation_anchor.trim() ? row.citation_anchor.trim() : options.citation_anchor.trim();
    if (!isDate(observationDate) || !isDate(releaseDate)) throw new Error(`structured observation ${index} requires valid ISO dates`);
    const revisionDate = row.revision_date === undefined || row.revision_date === '' ? undefined : requiredString(row, 'revision_date', index);
    if (revisionDate && !isDate(revisionDate)) throw new Error(`structured observation ${index} has invalid revision_date`);
    if (revisionDate && revisionDate < releaseDate) throw new Error(`structured observation ${index} has revision_date before release_date`);
    const numericValue = typeof row.value === 'number' ? row.value : typeof row.value === 'string' && row.value.trim() ? Number(row.value) : NaN;
    if (!Number.isFinite(numericValue)) throw new Error(`structured observation ${index} requires a finite numeric value`);
    const key = `${seriesId}|${observationDate}|${row.vintage ?? ''}`;
    if (seen.has(key)) throw new Error(`duplicate structured observation: ${key}`);
    seen.add(key);
    return { name, status: 'KNOWN', value: numericValue, unit, series_id: seriesId, observation_date: observationDate, release_date: releaseDate, ...(revisionDate ? { revision_date: revisionDate } : {}), ...(typeof row.vintage === 'string' && row.vintage ? { vintage: row.vintage } : {}), source_ids: [options.source_document_id], citation_anchor: citationAnchor };
  });
  return { artifact_sha256: artifactSha256, source_document_id: options.source_document_id, ingested_at: new Date().toISOString(), ...(options.verified_at ? { verified_at: options.verified_at } : {}), observations };
}

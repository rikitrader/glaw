import type { IndexedDocument } from './citations.ts';
import { runHistoricalBenchmark, type BenchmarkCase, type BenchmarkForecast } from './benchmark.ts';

export type BenchmarkStatus = 'fixture' | 'executable' | 'blocked';

export interface BenchmarkCatalogEntry {
  case_id: string;
  status: BenchmarkStatus;
  required_outputs: string[];
  cutoff_date?: string;
  forecast_horizon?: string;
  observations?: BenchmarkCase['observations'];
  source_ids?: string[];
  release_basis?: string;
  methodology_note?: string;
}

export interface BenchmarkCatalogValidation {
  case_id: string;
  executable: boolean;
  errors: string[];
}

/**
 * Validate benchmark eligibility without turning a fixture or a lead into evidence.
 * An executable case must carry source-bound observations, a historical cutoff, and
 * at least one post-cutoff outcome. Every cited document must already be VERIFIED.
 */
export function validateBenchmarkCatalogEntry(entry: BenchmarkCatalogEntry, documents: IndexedDocument[]): BenchmarkCatalogValidation {
  const errors: string[] = [];
  if (!entry.case_id) errors.push('case_id is required');
  if (!entry.required_outputs.length) errors.push('required_outputs are required');
  if (entry.status !== 'executable') return { case_id: entry.case_id, executable: false, errors };
  if (!entry.cutoff_date) errors.push('executable benchmark requires cutoff_date');
  if (!entry.forecast_horizon) errors.push('executable benchmark requires forecast_horizon');
  if (!entry.observations?.length) errors.push('executable benchmark requires observations');
  if (!entry.source_ids?.length) errors.push('executable benchmark requires source_ids');
  if (!entry.release_basis) errors.push('executable benchmark requires release_basis');
  if (!entry.methodology_note) errors.push('executable benchmark requires methodology_note');
  const byId = new Map(documents.map((document) => [document.document_id, document]));
  for (const sourceId of entry.source_ids ?? []) {
    const source = byId.get(sourceId);
    if (!source) errors.push(`benchmark source not found: ${sourceId}`);
    else if (source.status !== 'VERIFIED') errors.push(`benchmark source is not verified: ${sourceId}`);
    else if (!source.citation_anchor) errors.push(`benchmark source lacks citation anchor: ${sourceId}`);
  }
  for (const observation of entry.observations ?? []) {
    if (!entry.source_ids?.includes(observation.source_id)) errors.push(`observation source is not declared: ${observation.source_id}`);
    if (!observation.series_id) errors.push(`observation series_id is required: ${observation.source_id}`);
    if (!observation.unit) errors.push(`observation unit is required: ${observation.source_id}`);
    if (!observation.citation_anchor) errors.push(`observation citation_anchor is required: ${observation.source_id}`);
  }
  if (entry.cutoff_date && !(entry.observations ?? []).some((observation) => observation.date > entry.cutoff_date!)) errors.push('executable benchmark requires a post-cutoff outcome');
  return { case_id: entry.case_id, executable: errors.length === 0, errors };
}

export function validateBenchmarkCatalog(entries: BenchmarkCatalogEntry[], documents: IndexedDocument[]): BenchmarkCatalogValidation[] {
  return entries.map((entry) => validateBenchmarkCatalogEntry(entry, documents));
}

export function runExecutableBenchmarks(entries: BenchmarkCatalogEntry[], documents: IndexedDocument[], forecast: (observations: BenchmarkCase['observations']) => number): { results: BenchmarkForecast[]; blocked: BenchmarkCatalogValidation[] } {
  const validations = validateBenchmarkCatalog(entries, documents);
  const results: BenchmarkForecast[] = [];
  const blocked: BenchmarkCatalogValidation[] = [];
  for (const [index, validation] of validations.entries()) {
    const entry = entries[index];
    if (!validation.executable || entry.status !== 'executable') {
      if (entry.status === 'executable') blocked.push(validation);
      continue;
    }
    results.push(runHistoricalBenchmark({ case_id: entry.case_id, cutoff_date: entry.cutoff_date!, forecast_horizon: entry.forecast_horizon!, observations: entry.observations! }, forecast));
  }
  return { results, blocked };
}

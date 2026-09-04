import type { InstitutionalObservation, ObservationStatus } from './observation-contract.ts';

export const DATA_QUALITY_COLORS = ['GREEN', 'YELLOW', 'ORANGE', 'RED'] as const;
export type DataQualityColor = typeof DATA_QUALITY_COLORS[number];

export interface DataCompletenessRow {
  variable: string;
  domain: string;
  coverage_percentage: number;
  expected_observations: number;
  observed_observations: number;
  missing_observations: number;
  latest_observation: string | null;
  reporting_lag_days: number | null;
  source_count: number;
  confidence: number | null;
  status_counts: Partial<Record<ObservationStatus, number>>;
  quality: DataQualityColor;
  notes: string;
}

export interface EvidenceTableRow {
  claim_id: string;
  claim: string;
  evidence_supporting: string[];
  evidence_contradicting: string[];
  primary_sources: string[];
  model_result: string | null;
  confidence: 'VERY HIGH' | 'HIGH' | 'MODERATE' | 'LOW' | 'VERY LOW' | 'UNRESOLVED';
  sensitivity: string;
  final_assessment: string;
  uncertainty: string;
}

const asOfDate = (value: string): Date => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(`invalid as_of date: ${value}`);
  const date = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(date.getTime())) throw new Error(`invalid as_of date: ${value}`);
  return date;
};

const dateOnly = (value: string): Date => new Date(`${value}T00:00:00Z`);
const daysBetween = (later: Date, earlier: Date): number => Math.max(0, Math.floor((later.getTime() - earlier.getTime()) / 86_400_000));

function qualityFor(coverage: number, confidence: number | null, latest: string | null, asOf: Date): DataQualityColor {
  if (!latest || coverage === 0) return 'RED';
  const lag = daysBetween(asOf, dateOnly(latest));
  if (coverage >= 100 && confidence !== null && confidence >= 0.8 && lag <= 90) return 'GREEN';
  if (coverage >= 75 && confidence !== null && confidence >= 0.6 && lag <= 365) return 'YELLOW';
  if (coverage > 0) return 'ORANGE';
  return 'RED';
}

/** Build a completeness dashboard without imputing missing observations. */
export function buildDataCompletenessDashboard(
  expected: Array<{ variable: string; domain: string; expected_observations: number }>,
  observations: InstitutionalObservation[],
  asOf: string
): DataCompletenessRow[] {
  const asOfValue = asOfDate(asOf);
  return expected.map((item) => {
    if (!Number.isInteger(item.expected_observations) || item.expected_observations <= 0) throw new Error(`expected_observations must be a positive integer: ${item.variable}`);
    const matched = observations.filter((observation) => observation.variable === item.variable && observation.domain === item.domain && observation.value !== null && observation.verification_status !== 'UNAVAILABLE');
    const statusCounts: Partial<Record<ObservationStatus, number>> = {};
    for (const observation of matched) statusCounts[observation.verification_status] = (statusCounts[observation.verification_status] ?? 0) + 1;
    const latest = matched.map((observation) => observation.date).sort().at(-1) ?? null;
    const sourceIds = new Set(matched.map((observation) => observation.source_id));
    const confidenceValues = matched.map((observation) => observation.confidence_score).filter((value): value is number => value !== null);
    const confidence = confidenceValues.length ? confidenceValues.reduce((sum, value) => sum + value, 0) / confidenceValues.length : null;
    const coverage = Math.min(100, (matched.length / item.expected_observations) * 100);
    const quality = qualityFor(coverage, confidence, latest, asOfValue);
    return {
      variable: item.variable,
      domain: item.domain,
      coverage_percentage: coverage,
      expected_observations: item.expected_observations,
      observed_observations: matched.length,
      missing_observations: Math.max(0, item.expected_observations - matched.length),
      latest_observation: latest,
      reporting_lag_days: latest ? daysBetween(asOfValue, dateOnly(latest)) : null,
      source_count: sourceIds.size,
      confidence,
      status_counts: statusCounts,
      quality,
      notes: matched.length ? 'Coverage is based only on source-bound non-UNAVAILABLE observations; disputed and provisional observations remain visibly classified.' : 'No source-bound observation was admitted for this variable; no value was imputed.'
    };
  });
}

export function validateDataCompletenessDashboard(rows: DataCompletenessRow[]): string[] {
  const errors: string[] = [];
  const variables = new Set<string>();
  for (const row of rows) {
    if (!row.variable.trim()) errors.push('dashboard variable is required');
    const key = `${row.domain}:${row.variable}`;
    if (variables.has(key)) errors.push(`duplicate dashboard variable: ${key}`);
    variables.add(key);
    if (!Number.isFinite(row.coverage_percentage) || row.coverage_percentage < 0 || row.coverage_percentage > 100) errors.push(`invalid coverage: ${row.variable}`);
    if (!Number.isInteger(row.expected_observations) || row.expected_observations <= 0) errors.push(`invalid expected count: ${row.variable}`);
    if (!Number.isInteger(row.observed_observations) || row.observed_observations < 0) errors.push(`invalid observed count: ${row.variable}`);
    if (!DATA_QUALITY_COLORS.includes(row.quality)) errors.push(`invalid quality color: ${row.variable}`);
    if (row.confidence !== null && (!Number.isFinite(row.confidence) || row.confidence < 0 || row.confidence > 1)) errors.push(`invalid confidence: ${row.variable}`);
  }
  return [...new Set(errors)];
}

export function validateEvidenceTable(rows: EvidenceTableRow[]): string[] {
  const errors: string[] = [];
  const ids = new Set<string>();
  for (const row of rows) {
    if (!row.claim_id.trim()) errors.push('claim_id is required');
    if (ids.has(row.claim_id)) errors.push(`duplicate claim_id: ${row.claim_id}`);
    ids.add(row.claim_id);
    if (!row.claim.trim()) errors.push(`claim is required: ${row.claim_id}`);
    if (!Array.isArray(row.evidence_supporting) || !Array.isArray(row.evidence_contradicting) || !Array.isArray(row.primary_sources)) errors.push(`evidence arrays are required: ${row.claim_id}`);
    if (!row.evidence_supporting.length && !row.evidence_contradicting.length && !row.uncertainty.trim()) errors.push(`claim lacks evidence or uncertainty: ${row.claim_id}`);
    if (!row.final_assessment.trim()) errors.push(`final assessment is required: ${row.claim_id}`);
    if (!row.sensitivity.trim()) errors.push(`sensitivity is required: ${row.claim_id}`);
  }
  return [...new Set(errors)];
}

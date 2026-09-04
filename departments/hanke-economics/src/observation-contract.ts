export const OBSERVATION_STATUSES = ['VERIFIED', 'PROVISIONAL', 'ESTIMATED', 'MODELED', 'IMPUTED', 'DISPUTED', 'STALE', 'UNAVAILABLE'] as const;
export type ObservationStatus = typeof OBSERVATION_STATUSES[number];
export const DATASET_DOMAINS = ['MACRO', 'MONETARY', 'BANKING', 'FX', 'FISCAL', 'OIL', 'EXTERNAL', 'TRADE', 'DEBT', 'HOUSEHOLDS', 'LABOR', 'PRICES', 'SOCIAL', 'LEGAL', 'SANCTIONS', 'INSTITUTIONS', 'POLITICAL-RISK', 'CAPITAL-FLOWS', 'INVESTMENT', 'INFRASTRUCTURE'] as const;
export type DatasetDomain = typeof DATASET_DOMAINS[number];

export interface InstitutionalObservation {
  country: string;
  variable: string;
  date: string;
  frequency: string;
  value: number | null;
  unit: string;
  currency: string | null;
  real_or_nominal: 'REAL' | 'NOMINAL' | 'NOT_APPLICABLE' | 'UNKNOWN';
  source: string;
  source_id: string;
  publication_date: string | null;
  retrieval_date: string;
  dataset_id: string;
  methodology: string;
  transformation_applied: string[];
  confidence_score: number | null;
  verification_status: ObservationStatus;
  revision_status: 'INITIAL' | 'REVISED' | 'FINAL' | 'NOT_APPLICABLE' | 'UNKNOWN';
  domain: DatasetDomain;
  notes?: string;
}

export interface SourceConflictRecord {
  conflict_id: string;
  variable: string;
  date: string;
  source_A: string;
  value_A: number | string | null;
  source_B: string;
  value_B: number | string | null;
  absolute_difference: number | null;
  percentage_difference: number | null;
  probable_reason: string;
  preferred_source: string | null;
  confidence: number | null;
  analyst_note: string;
}

export interface RedenominationRecord { record_id: string; currency: string; effective_date: string; old_units_per_new_unit: number; source_id: string; status: ObservationStatus; notes: string; }

const date = (value: unknown) => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value);
const nonEmpty = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0;

export function validateInstitutionalObservation(observation: InstitutionalObservation): string[] {
  const errors: string[] = [];
  if (!nonEmpty(observation.country)) errors.push('country is required');
  if (!nonEmpty(observation.variable)) errors.push('variable is required');
  if (!date(observation.date)) errors.push('date must be YYYY-MM-DD');
  if (!nonEmpty(observation.frequency)) errors.push('frequency is required');
  if (!nonEmpty(observation.unit)) errors.push('unit is required');
  if (!nonEmpty(observation.source)) errors.push('source is required');
  if (!nonEmpty(observation.source_id)) errors.push('source_id is required');
  if (!nonEmpty(observation.dataset_id)) errors.push('dataset_id is required');
  if (!date(observation.retrieval_date)) errors.push('retrieval_date must be YYYY-MM-DD');
  if (observation.publication_date !== null && !date(observation.publication_date)) errors.push('publication_date must be YYYY-MM-DD or null');
  if (!nonEmpty(observation.methodology)) errors.push('methodology is required');
  if (!OBSERVATION_STATUSES.includes(observation.verification_status)) errors.push('invalid verification_status');
  if (!DATASET_DOMAINS.includes(observation.domain)) errors.push('invalid dataset domain');
  if (observation.value !== null && (!Number.isFinite(observation.value) || typeof observation.value !== 'number')) errors.push('numeric value must be finite');
  if (observation.verification_status === 'UNAVAILABLE' && observation.value !== null) errors.push('UNAVAILABLE observation must have null value');
  if (observation.value !== null && observation.confidence_score === null) errors.push('numeric observation requires confidence_score');
  if (observation.confidence_score !== null && (!Number.isFinite(observation.confidence_score) || observation.confidence_score < 0 || observation.confidence_score > 1)) errors.push('confidence_score must be between 0 and 1');
  return errors;
}

export function validateSourceConflict(record: SourceConflictRecord): string[] {
  const errors: string[] = [];
  for (const field of ['conflict_id', 'variable', 'date', 'source_A', 'source_B', 'probable_reason', 'analyst_note'] as const) if (!nonEmpty(record[field])) errors.push(`${field} is required`);
  if (!date(record.date)) errors.push('conflict date must be YYYY-MM-DD');
  if (record.source_A === record.source_B) errors.push('conflict sources must differ');
  if (record.confidence !== null && (!Number.isFinite(record.confidence) || record.confidence < 0 || record.confidence > 1)) errors.push('conflict confidence must be between 0 and 1');
  return errors;
}

export function canonicalizeRedenominatedValue(value: number, observationDate: string, currency: string, records: RedenominationRecord[]): { value: number; transformations: string[] } {
  if (!date(observationDate)) throw new Error('observationDate must be YYYY-MM-DD');
  let canonical = value;
  const transformations: string[] = [];
  for (const record of records.filter((candidate) => candidate.currency === currency && candidate.status === 'VERIFIED' && candidate.effective_date <= observationDate).sort((a, b) => a.effective_date.localeCompare(b.effective_date))) {
    if (!(record.old_units_per_new_unit > 0)) throw new Error(`invalid redenomination factor: ${record.record_id}`);
    canonical /= record.old_units_per_new_unit;
    transformations.push(`${record.record_id}: divide by ${record.old_units_per_new_unit}`);
  }
  return { value: canonical, transformations };
}

export interface ReadinessDeclaration { pillar: string; weight: number; status: 'UNRESOLVED' | 'DATA_INSUFFICIENT' | 'EVIDENCE_READY'; evidence_ids: string[]; rationale: string; }
export const READINESS_PILLARS = [
  ['MONETARY', 0.15], ['BANKING', 0.20], ['FISCAL', 0.15], ['RESERVES', 0.15], ['EXTERNAL', 0.10], ['DEBT', 0.10], ['LEGAL', 0.05], ['INSTITUTIONAL', 0.05], ['SOCIAL', 0.05]
] as const;
export const READINESS_BANDS = [
  { min: 0, max: 39, label: 'NOT READY' }, { min: 40, max: 59, label: 'HIGH RISK' }, { min: 60, max: 74, label: 'CONDITIONAL' }, { min: 75, max: 89, label: 'READY WITH SAFEGUARDS' }, { min: 90, max: 100, label: 'STRONG READINESS' }
] as const;

/** Deliberately does not calculate a readiness score; evidence must be supplied and reviewed first. */
export function readinessStatus(declarations: ReadinessDeclaration[]): 'UNRESOLVED' | 'DATA_INSUFFICIENT' | 'EVIDENCE_READY' {
  if (declarations.length !== READINESS_PILLARS.length) return 'DATA_INSUFFICIENT';
  if (declarations.some((declaration) => declaration.status !== 'EVIDENCE_READY' || !declaration.evidence_ids.length)) return 'DATA_INSUFFICIENT';
  return 'EVIDENCE_READY';
}

import type { IndexedDocument } from './citations.ts';

export type ForecastOutcome = 'SUCCESSFUL' | 'UNSUCCESSFUL' | 'AMBIGUOUS' | 'UNTESTABLE';
export interface ForecastAuditEntry {
  audit_id: string;
  date: string;
  prediction: string;
  source_id: string;
  country: string;
  time_horizon: string;
  assumptions: string[];
  actual_outcome: string | null;
  forecast_value?: number | null;
  forecast_lower?: number | null;
  forecast_upper?: number | null;
  actual_value?: number | null;
  outcome: ForecastOutcome;
  context: string;
}

export function validateForecastAuditEntry(entry: ForecastAuditEntry, documents: IndexedDocument[]): string[] {
  const errors: string[] = []; const source = documents.find((document) => document.document_id === entry.source_id);
  if (!entry.prediction) errors.push('prediction is required');
  if (!entry.source_id) errors.push('primary source_id is required');
  if (!source) errors.push(`source not found: ${entry.source_id}`);
  else { if (source.status !== 'VERIFIED') errors.push(`forecast source is not verified: ${entry.source_id}`); if (!source.author.some((author) => author.toLocaleLowerCase().includes('hanke'))) errors.push(`forecast source is not identified as Hanke-authored: ${entry.source_id}`); }
  if (!entry.assumptions.length) errors.push('assumptions are required');
  if (entry.outcome !== 'UNTESTABLE' && !entry.actual_outcome) errors.push('actual_outcome is required for testable forecast');
  const hasPointForecast = typeof entry.forecast_value === 'number';
  const hasLower = typeof entry.forecast_lower === 'number';
  const hasUpper = typeof entry.forecast_upper === 'number';
  if (hasPointForecast && (hasLower || hasUpper)) errors.push('point and interval forecasts cannot be supplied together');
  if (hasLower !== hasUpper) errors.push('forecast_lower and forecast_upper must be supplied together');
  if (hasLower && hasUpper && (entry.forecast_lower! > entry.forecast_upper!)) errors.push('forecast_lower cannot exceed forecast_upper');
  if ((entry.forecast_value === null) !== (entry.actual_value === null) && !hasLower) errors.push('forecast_value and actual_value must be supplied together');
  if ((hasLower || hasUpper) && typeof entry.actual_value !== 'number' && entry.outcome !== 'UNTESTABLE') errors.push('interval forecast requires actual_value for a testable outcome');
  return errors;
}

export function forecastAbsoluteError(entry: ForecastAuditEntry): number | null {
  if (typeof entry.forecast_value !== 'number' || typeof entry.actual_value !== 'number') return null;
  return Math.abs(entry.forecast_value - entry.actual_value);
}

export function forecastIntervalAssessment(entry: ForecastAuditEntry): { contains: boolean; distance: number } | null {
  if (typeof entry.forecast_lower !== 'number' || typeof entry.forecast_upper !== 'number' || typeof entry.actual_value !== 'number') return null;
  if (entry.forecast_lower > entry.forecast_upper) return null;
  const distance = entry.actual_value < entry.forecast_lower
    ? entry.forecast_lower - entry.actual_value
    : entry.actual_value > entry.forecast_upper
      ? entry.actual_value - entry.forecast_upper
      : 0;
  return { contains: distance === 0, distance };
}

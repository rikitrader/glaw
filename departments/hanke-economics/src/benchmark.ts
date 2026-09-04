export interface HistoricalObservation {
  date: string;
  release_date: string;
  value: number;
  source_id: string;
  series_id?: string;
  unit?: string;
  citation_anchor?: string;
}
export interface BenchmarkCase { case_id: string; cutoff_date: string; observations: HistoricalObservation[]; forecast_horizon: string; }
export interface BenchmarkForecast { case_id: string; cutoff_date: string; information_set: HistoricalObservation[]; forecast: number; actual: HistoricalObservation | null; score: number | null; lookahead_blocked: boolean; warnings: string[]; }

export function runHistoricalBenchmark(caseFile: BenchmarkCase, forecast: (observations: HistoricalObservation[]) => number): BenchmarkForecast {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(caseFile.cutoff_date)) throw new Error('cutoff_date must be YYYY-MM-DD');
  for (const observation of caseFile.observations) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(observation.date) || !/^\d{4}-\d{2}-\d{2}$/.test(observation.release_date)) throw new Error(`invalid benchmark date for ${observation.source_id}`);
  }
  const information = caseFile.observations.filter((observation) => observation.date <= caseFile.cutoff_date && observation.release_date <= caseFile.cutoff_date);
  const future = caseFile.observations.filter((observation) => observation.date > caseFile.cutoff_date).sort((a, b) => a.date.localeCompare(b.date));
  const releasedFuture = future.filter((observation) => observation.release_date <= caseFile.cutoff_date);
  const warnings = releasedFuture.map((observation) => `Future-dated observation ${observation.date} was released by cutoff; excluded from information set to prevent lookahead.`);
  const forecastValue = forecast(information);
  const actual = future[0] ?? null;
  if (!actual) warnings.push('No post-cutoff outcome available.');
  return { case_id: caseFile.case_id, cutoff_date: caseFile.cutoff_date, information_set: information, forecast: forecastValue, actual, score: actual ? Math.abs(forecastValue - actual.value) : null, lookahead_blocked: information.every((observation) => observation.date <= caseFile.cutoff_date && observation.release_date <= caseFile.cutoff_date), warnings };
}

export interface TimeSeriesPoint { date: string; value: number; release_date?: string; source_id: string; }
export interface AdfLikeResult { method: 'ADF_LIKE_NO_TREND'; observations: number; coefficient: number; t_statistic: number; residual_variance: number; assessment: 'REQUIRES_CRITICAL_VALUES'; warnings: string[]; source_ids: string[]; }
export interface CointegrationScreenResult { method: 'ENGLE_GRANGER_SCREEN_NO_CRITICAL_VALUES'; observations: number; slope: number; residual_variance: number; assessment: 'SCREEN_ONLY'; warnings: string[]; source_ids: string[]; }

const sorted = (series: TimeSeriesPoint[]) => [...series].sort((a, b) => a.date.localeCompare(b.date));
const sourceIds = (series: TimeSeriesPoint[]) => [...new Set(series.map((point) => point.source_id))];
const assertSeries = (series: TimeSeriesPoint[], minimum: number) => {
  if (series.length < minimum) throw new Error(`at least ${minimum} observations are required`);
  if (series.some((point) => !Number.isFinite(point.value))) throw new Error('series contains a non-finite value');
};

/** A reproducible ADF-style regression. It does not assign significance without critical values. */
export function adfLikeNoTrend(series: TimeSeriesPoint[]): AdfLikeResult {
  assertSeries(series, 8); const points = sorted(series); const x = points.slice(0, -1).map((point) => point.value); const y = points.slice(1).map((point, index) => point.value - x[index]);
  const xBar = x.reduce((sum, value) => sum + value, 0) / x.length; const yBar = y.reduce((sum, value) => sum + value, 0) / y.length;
  const denominator = x.reduce((sum, value) => sum + (value - xBar) ** 2, 0); if (denominator === 0) throw new Error('lagged level has no variation');
  const coefficient = x.reduce((sum, value, index) => sum + (value - xBar) * (y[index] - yBar), 0) / denominator; const intercept = yBar - coefficient * xBar;
  const residuals = y.map((value, index) => value - (intercept + coefficient * x[index])); const dof = Math.max(1, residuals.length - 2); const residualVariance = residuals.reduce((sum, value) => sum + value ** 2, 0) / dof; const standardError = Math.sqrt(residualVariance / denominator);
  return { method: 'ADF_LIKE_NO_TREND', observations: y.length, coefficient, t_statistic: standardError === 0 ? 0 : coefficient / standardError, residual_variance: residualVariance, assessment: 'REQUIRES_CRITICAL_VALUES', warnings: ['This is a diagnostic regression, not a formal ADF decision.', 'Supply sample-specific critical values, deterministic-term choices, lag selection, and a documented data vintage before classifying stationarity.'], source_ids: sourceIds(series) };
}

/** Engle-Granger-style residual screen; no cointegration conclusion is allowed without critical values and specification review. */
export function cointegrationScreen(xSeries: TimeSeriesPoint[], ySeries: TimeSeriesPoint[]): CointegrationScreenResult {
  const yByDate = new Map(sorted(ySeries).map((point) => [point.date, point])); const pairs = sorted(xSeries).flatMap((x) => { const y = yByDate.get(x.date); return y ? [{ x: x.value, y: y.value, source_ids: [x.source_id, y.source_id] }] : []; });
  if (pairs.length < 8) throw new Error('at least eight overlapping observations are required');
  const xBar = pairs.reduce((sum, pair) => sum + pair.x, 0) / pairs.length; const yBar = pairs.reduce((sum, pair) => sum + pair.y, 0) / pairs.length; const denominator = pairs.reduce((sum, pair) => sum + (pair.x - xBar) ** 2, 0); if (denominator === 0) throw new Error('regressor has no variation');
  const slope = pairs.reduce((sum, pair) => sum + (pair.x - xBar) * (pair.y - yBar), 0) / denominator; const intercept = yBar - slope * xBar; const residualVariance = pairs.reduce((sum, pair) => sum + (pair.y - (intercept + slope * pair.x)) ** 2, 0) / Math.max(1, pairs.length - 2);
  return { method: 'ENGLE_GRANGER_SCREEN_NO_CRITICAL_VALUES', observations: pairs.length, slope, residual_variance: residualVariance, assessment: 'SCREEN_ONLY', warnings: ['This is a residual screen, not a cointegration finding.', 'Critical values, deterministic terms, structural breaks, lag selection, and vintage alignment are required before inference.'], source_ids: [...new Set(pairs.flatMap((pair) => pair.source_ids))] };
}

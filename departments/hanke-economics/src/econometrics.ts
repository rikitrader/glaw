export interface RegressionObservation { date: string; y: number; x: number; release_date: string; source_id: string; }
export interface RegressionResult { method: 'OLS_ONE_REGRESSOR'; observations: number; intercept: number; slope: number; r_squared: number; residuals: number[]; warnings: string[]; source_ids: string[]; }

export function olsOneRegressor(observations: RegressionObservation[]): RegressionResult {
  if (observations.length < 3) throw new Error('at least three observations are required');
  const xBar = observations.reduce((sum, item) => sum + item.x, 0) / observations.length;
  const yBar = observations.reduce((sum, item) => sum + item.y, 0) / observations.length;
  const denominator = observations.reduce((sum, item) => sum + (item.x - xBar) ** 2, 0);
  if (denominator === 0) throw new Error('regressor has no variation');
  const slope = observations.reduce((sum, item) => sum + (item.x - xBar) * (item.y - yBar), 0) / denominator;
  const intercept = yBar - slope * xBar;
  const residuals = observations.map((item) => item.y - (intercept + slope * item.x));
  const total = observations.reduce((sum, item) => sum + (item.y - yBar) ** 2, 0);
  const explained = observations.reduce((sum, item) => sum + (intercept + slope * item.x - yBar) ** 2, 0);
  const warnings: string[] = ['OLS is descriptive and does not establish causality.', 'No stationarity, cointegration, heteroskedasticity, or autocorrelation test is implied by this adapter.'];
  if (observations.some((item, index) => index > 0 && item.date < observations[index - 1].date)) warnings.push('observations are not sorted by date');
  return { method: 'OLS_ONE_REGRESSOR', observations: observations.length, intercept, slope, r_squared: total === 0 ? 0 : explained / total, residuals, warnings, source_ids: [...new Set(observations.map((item) => item.source_id))] };
}

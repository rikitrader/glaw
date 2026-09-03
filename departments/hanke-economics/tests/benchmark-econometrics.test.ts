import test from 'node:test';
import assert from 'node:assert/strict';
import { runHistoricalBenchmark } from '../src/benchmark.ts';
import { olsOneRegressor } from '../src/econometrics.ts';
import { adfLikeNoTrend, cointegrationScreen } from '../src/econometrics-diagnostics.ts';
import { readFileSync } from 'node:fs';
import { forecastAbsoluteError, forecastIntervalAssessment, validateForecastAuditEntry, type ForecastAuditEntry } from '../src/forecast-audit.ts';
import { runExecutableBenchmarks, validateBenchmarkCatalogEntry, type BenchmarkCatalogEntry } from '../src/benchmark-catalog.ts';

test('historical benchmark excludes unreleased information', () => {
  const result = runHistoricalBenchmark({ case_id: 'C-1', cutoff_date: '2000-01-01', forecast_horizon: 'one-period', observations: [{ date: '1999-12-01', release_date: '1999-12-15', value: 1, source_id: 'S-1' }, { date: '2000-02-01', release_date: '2000-02-15', value: 2, source_id: 'S-2' }] }, (observations) => observations[0].value);
  assert.equal(result.information_set.length, 1);
  assert.equal(result.lookahead_blocked, true);
  assert.equal(result.score, 1);
});

test('historical benchmark excludes future-dated observations even if misreleased before cutoff', () => {
  const result = runHistoricalBenchmark({ case_id: 'C-2', cutoff_date: '2000-01-01', forecast_horizon: 'one-period', observations: [{ date: '1999-12-01', release_date: '1999-12-15', value: 1, source_id: 'S-1' }, { date: '2000-02-01', release_date: '1999-12-20', value: 9, source_id: 'S-2' }] }, (observations) => observations[0].value);
  assert.equal(result.information_set.length, 1);
  assert.equal(result.actual?.value, 9);
  assert.equal(result.lookahead_blocked, true);
  assert.ok(result.warnings.some((warning) => warning.includes('Future-dated observation')));
});

test('historical benchmark rejects malformed dates', () => {
  assert.throws(() => runHistoricalBenchmark({ case_id: 'C-3', cutoff_date: '2000/01/01', forecast_horizon: 'one-period', observations: [] }, () => 0), /cutoff_date/);
});

test('OLS adapter returns coefficients and causal warnings', () => {
  const result = olsOneRegressor([{ date: '1', release_date: '1', x: 1, y: 2, source_id: 'S-1' }, { date: '2', release_date: '2', x: 2, y: 4, source_id: 'S-1' }, { date: '3', release_date: '3', x: 3, y: 6, source_id: 'S-1' }]);
  assert.equal(result.slope, 2);
  assert.ok(result.warnings.some((warning) => warning.includes('causality')));
});

test('ADF-like diagnostic is reproducible but refuses an unsupported stationarity conclusion', () => {
  const series = Array.from({ length: 10 }, (_, index) => ({ date: `2000-${String(index + 1).padStart(2, '0')}-01`, value: index + 1, release_date: `2000-${String(index + 1).padStart(2, '0')}-15`, source_id: 'S-1' }));
  const result = adfLikeNoTrend(series);
  assert.equal(result.method, 'ADF_LIKE_NO_TREND');
  assert.equal(result.assessment, 'REQUIRES_CRITICAL_VALUES');
  assert.ok(result.warnings.some((warning) => warning.includes('formal ADF')));
});

test('cointegration screen requires aligned observations and remains screen-only', () => {
  const x = Array.from({ length: 8 }, (_, index) => ({ date: `2000-${String(index + 1).padStart(2, '0')}-01`, value: index + 1, source_id: 'S-X' }));
  const y = x.map((point) => ({ ...point, value: point.value * 2, source_id: 'S-Y' }));
  const result = cointegrationScreen(x, y);
  assert.equal(result.observations, 8);
  assert.equal(result.assessment, 'SCREEN_ONLY');
  assert.deepEqual(result.source_ids.sort(), ['S-X', 'S-Y']);
});

test('forecast audit registry preserves verified but untestable conditional Hanke forecasts', () => {
  const lines = readFileSync(new URL('../benchmarks/hanke-forecast-audit.jsonl', import.meta.url), 'utf8').trim().split('\n').filter(Boolean);
  assert.equal(lines.length, 1);
  const entry = JSON.parse(lines[0]) as ForecastAuditEntry;
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  assert.deepEqual(validateForecastAuditEntry(entry, documents), []);
  assert.equal(entry.outcome, 'UNTESTABLE');
  assert.equal(entry.actual_outcome, null);
  assert.equal(forecastAbsoluteError(entry), null);
});

test('forecast audit rejects restricted or non-Hanke sources and computes error only when outcomes exist', () => {
  const documents = [{ document_id: 'D-1', title: 'restricted', author: ['Steve H. Hanke'], source_url: 'https://example.test', status: 'RESTRICTED', local_path: null, citation_anchor: null, authority_level: 1 }] as never;
  const entry: ForecastAuditEntry = { audit_id: 'F-1', date: '2020-01-01', prediction: 'testable claim', source_id: 'D-1', country: 'X', time_horizon: 'one year', assumptions: ['A'], actual_outcome: null, forecast_value: 1, actual_value: 2, outcome: 'UNTESTABLE', context: 'context' };
  assert.ok(validateForecastAuditEntry(entry, documents).some((error) => error.includes('not verified')));
  assert.equal(forecastAbsoluteError(entry), 1);
});

test('forecast audit represents interval forecasts without inventing a point estimate', () => {
  const documents = [{ document_id: 'D-HANKE', title: 'primary forecast', author: ['Steve H. Hanke', 'John Greenwood'], source_url: 'https://example.test/primary', status: 'VERIFIED', local_path: 'primary.pdf', citation_anchor: 'p. 1', authority_level: 1 }] as never;
  const entry: ForecastAuditEntry = {
    audit_id: 'F-INTERVAL-1', date: '2021-07-20', prediction: 'year-end inflation within the stated range', source_id: 'D-HANKE', country: 'United States', time_horizon: 'end of 2021', assumptions: ['source range is evaluated as published'], actual_outcome: 'official release outcome', forecast_lower: 6, forecast_upper: 9, actual_value: 7, outcome: 'SUCCESSFUL', context: 'interval forecast'
  };
  assert.deepEqual(validateForecastAuditEntry(entry, documents), []);
  assert.deepEqual(forecastIntervalAssessment(entry), { contains: true, distance: 0 });
  assert.equal(forecastAbsoluteError(entry), null);
  assert.deepEqual(forecastIntervalAssessment({ ...entry, actual_value: 10 }), { contains: false, distance: 1 });
  assert.ok(validateForecastAuditEntry({ ...entry, forecast_value: 7.5 }, documents).some((error) => error.includes('point and interval')));
});

test('benchmark catalog refuses executable cases without verified source-bound outcomes', () => {
  const entry: BenchmarkCatalogEntry = { case_id: 'B-1', status: 'executable', required_outputs: ['forecast'], cutoff_date: '2000-01-01', forecast_horizon: 'one-period', source_ids: ['S-1'], observations: [{ date: '1999-12-01', release_date: '1999-12-15', value: 1, source_id: 'S-1' }, { date: '2000-02-01', release_date: '2000-02-15', value: 2, source_id: 'S-1' }] };
  const documents = [{ document_id: 'S-1', title: 'not verified', author: ['World Bank'], source_url: 'https://example.test', status: 'FOUND', local_path: null, citation_anchor: null, authority_level: 2 }] as never;
  const validation = validateBenchmarkCatalogEntry(entry, documents);
  assert.equal(validation.executable, false);
  assert.ok(validation.errors.some((error) => error.includes('not verified')));
  const run = runExecutableBenchmarks([entry], documents, () => 1);
  assert.equal(run.results.length, 0);
  assert.equal(run.blocked.length, 1);
});

test('CBBH benchmark executes only on verified source-bound observations', () => {
  const entries = readFileSync(new URL('../benchmarks/cases.jsonl', import.meta.url), 'utf8').trim().split('\n').map((line) => JSON.parse(line)) as BenchmarkCatalogEntry[];
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const entry = entries.find((candidate) => candidate.case_id === 'bosnia-cbbh-net-free-fx-reserves-2001');
  assert.ok(entry);
  const run = runExecutableBenchmarks([entry], documents, (observations) => observations.at(-1)!.value);
  assert.equal(run.blocked.length, 0);
  assert.equal(run.results.length, 1);
  assert.equal(run.results[0].forecast, 48);
  assert.equal(run.results[0].actual?.value, 75);
  assert.equal(run.results[0].score, 27);
  assert.equal(run.results[0].lookahead_blocked, true);
});

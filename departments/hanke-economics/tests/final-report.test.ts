import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildIndexedFinalReport, validateIndexedFinalReport } from '../src/final-report.ts';
import { validateDataCompletenessDashboard, validateEvidenceTable } from '../src/review-quality.ts';

const index = JSON.parse(readFileSync(new URL('../reports/final-report-index.json', import.meta.url), 'utf8'));
const blockedRun = {
  run_id: 'REPORT-TEST', workflow_id: 'venezuela-monetary-reform', status: 'BLOCKED', nodes: {},
  gates: { 'critical-data-reconciled': 'BLOCKED' },
  gate_records: { 'critical-data-reconciled': { status: 'BLOCKED', owner: 'data-forensics', at: '2026-01-01T00:00:00.000Z', evidence_ids: [], reason: 'source data unavailable' } },
  artifacts: {}, findings: [], events: []
} as never;

test('enforced final report index contains all 24 parts, required formulas, and chart slots', () => {
  assert.equal(index.parts.length, 24);
  assert.ok(index.parts.every((part: { sections: unknown[] }) => part.sections.length > 0));
  assert.ok(index.required_formulas.length >= 15);
  assert.ok(index.required_derived_indicators.length >= 50);
  assert.ok(index.required_charts.length >= 50);
  assert.deepEqual(index.required_data_statuses, ['VERIFIED', 'PROVISIONAL', 'ESTIMATED', 'MODELED', 'IMPUTED', 'DISPUTED', 'STALE', 'UNAVAILABLE']);
});

test('blocked final report renders every indexed section and explicit unavailable data', () => {
  const report = buildIndexedFinalReport(index, blockedRun);
  assert.equal(validateIndexedFinalReport(report, index).length, 0);
  assert.equal(report.report_status, 'BLOCKED');
  assert.equal(report.sections.length, index.parts.flatMap((part: { sections: unknown[] }) => part.sections).length);
  assert.ok(report.sections.every((section) => section.status === 'BLOCKED' && section.data_status === 'UNAVAILABLE'));
  assert.ok(report.charts.every((chart) => chart.status === 'UNAVAILABLE'));
  assert.ok(report.formulas.every((formula) => formula.status === 'BLOCKED'));
  assert.equal(report.formulas.length, index.required_formulas.length + index.required_derived_indicators.length);
  assert.equal(report.charts.length, 200);
  assert.equal(validateDataCompletenessDashboard(report.data_completeness).length, 0);
  assert.equal(validateEvidenceTable(report.evidence_table).length, 0);
});

test('indexed report preserves disputed input status instead of relabeling it as verified or unavailable', () => {
  const run = { ...blockedRun, artifacts: { data_bundle: [{ status: 'DISPUTED', value: 10, source_ids: ['SRC-1'] }], verified_source_ids: ['SRC-1'] } } as never;
  const report = buildIndexedFinalReport(index, run);
  assert.ok(report.data_inventory.every((metric) => metric.status === 'DISPUTED'));
  assert.ok(report.data_inventory[0].notes.includes('not promoted'));
});

test('final report validator rejects an omitted required section and an unlabeled claim', () => {
  const report = buildIndexedFinalReport(index, blockedRun);
  report.sections.pop();
  report.sections[0].claims = [{ text: 'unsupported', label: 'UNRESOLVED', source_ids: [] }];
  const errors = validateIndexedFinalReport(report, index);
  assert.ok(errors.some((error) => error.includes('missing required report section')));
  assert.ok(errors.some((error) => error.includes('claim lacks evidence or uncertainty')));
});

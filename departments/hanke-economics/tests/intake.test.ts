import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { classifyIntakeReadiness, intakeCanStartAnalysis, validateIntake } from '../src/intake.ts';
import { createIntakeRunReport } from '../src/intake-runner.ts';

test('Venezuela template is research intake only and contains no invented values', () => {
  const intake = JSON.parse(readFileSync(new URL('../intake/venezuela-dollarization.json', import.meta.url), 'utf8'));
  assert.equal(intake.status, 'RESEARCH_INTAKE_ONLY');
  assert.ok(intake.data_intake.every((item: { status: string; value: unknown }) => item.status === 'UNAVAILABLE' && item.value === null));
});

test('policy intake can execute without a human reviewer', () => {
  const intake = { intake_id: 'I-1', question: 'q', country: 'Venezuela', output_mode: 'POLICY', data_intake: [], source_ids: [], human_reviewer: '', status: 'DRAFT' as const };
  assert.equal(intakeCanStartAnalysis(intake), true);
  assert.ok(!validateIntake(intake).some((error) => error.includes('human_reviewer')));
});

test('intake rejects unknown sources and invalid output modes', () => {
  const intake = { intake_id: 'I-2', question: 'q', country: 'Venezuela', output_mode: 'UNKNOWN', data_intake: [], source_ids: ['D-404'], human_reviewer: 'reviewer', status: 'DRAFT' as const };
  const errors = validateIntake(intake, ['D-1']);
  assert.ok(errors.some((error) => error.includes('invalid output_mode')));
  assert.ok(errors.some((error) => error.includes('unknown source_id')));
});

test('populated data requires lineage and valid temporal metadata', () => {
  const intake = { intake_id: 'I-3', question: 'q', country: 'Venezuela', output_mode: 'RESEARCH', data_intake: [{ name: 'M2', status: 'KNOWN', value: 10, unit: 'local currency', observation_date: 'June 2024', source_ids: ['D-1'] }], source_ids: ['D-1'], human_reviewer: '', status: 'DRAFT' as const };
  const errors = validateIntake(intake, ['D-1']);
  assert.ok(errors.some((error) => error.includes('series_id')));
  assert.ok(errors.some((error) => error.includes('observation_date')));
});

test('research and policy intake do not require a reviewer', () => {
  const research = { intake_id: 'I-4', question: 'q', country: 'Venezuela', output_mode: 'RESEARCH', data_intake: [], source_ids: [], human_reviewer: '', status: 'DRAFT' as const };
  assert.equal(intakeCanStartAnalysis(research), true);
  const policy = { ...research, output_mode: 'POLICY' };
  assert.equal(intakeCanStartAnalysis(policy), true);
});

test('intake readiness distinguishes research, analysis, and recommendation states', () => {
  const base = { intake_id: 'I-5', question: 'q', country: 'Venezuela', output_mode: 'ANALYSIS', data_intake: [{ name: 'M2', status: 'KNOWN', value: 10, unit: 'currency', series_id: 'M2', observation_date: '2024-01-01', source_ids: ['D-1'] }], source_ids: ['D-1'], human_reviewer: '', status: 'DRAFT' as const };
  assert.equal(classifyIntakeReadiness({ ...base, source_ids: [] }, [], []).readiness, 'RESEARCH_READY');
  assert.equal(classifyIntakeReadiness(base, ['D-1'], ['D-1']).readiness, 'ANALYSIS_READY');
  assert.equal(classifyIntakeReadiness({ ...base, output_mode: 'POLICY' }, ['D-1'], ['D-1']).readiness, 'RECOMMENDATION_READY');
});

test('matter-scoped intake runner reports source counts and blocks unsafe recommendations', () => {
  const template = JSON.parse(readFileSync(new URL('../intake/venezuela-dollarization.json', import.meta.url), 'utf8'));
  const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
  const report = createIntakeRunReport({ ...template, human_reviewer: 'reviewer-1' }, documents);
  assert.equal(report.intake_id, 'INTAKE-VEN-DOLLARIZATION-001');
  assert.equal(report.recommendation_allowed, false);
  assert.equal(report.readiness.readiness, 'RESEARCH_READY');
  assert.ok(report.source_status_counts.VERIFIED >= 1);
  assert.ok(report.readiness.blockers.some((blocker) => blocker.includes('unavailable')));
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHaeisExecutors } from '../src/executors.ts';
import { runWorkflow } from '../src/workflow.ts';

const readJson = (path: string) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const definition = readJson('../workflows/venezuela-monetary-reform.json');
const baseIntake = readJson('../intake/venezuela-dollarization.json');
const documents = readJson('../rag/document-index.json').documents;
const audit = readJson('../datasets/venezuela-historical-monetary-flow-audit.json');

test('historical monetary-flow evidence runs through HAEIS without opening current policy gates', async () => {
  const row = audit.rows[0];
  const frameworkIds = ['PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234'];
  const sourceIds = [...new Set([...row.source_ids, ...frameworkIds])];
  const intake = {
    ...baseIntake,
    intake_id: 'INTAKE-VEN-HISTORICAL-MONETARY-FLOW-2009',
    output_mode: 'HISTORICAL',
    status: 'RESEARCH_INTAKE_ONLY',
    source_ids: sourceIds,
    critical_unknowns: ['current Venezuela monetary and banking observations are not available in this historical fixture'],
    data_intake: baseIntake.data_intake.map((item: Record<string, unknown>) => ({ ...item, status: 'UNAVAILABLE', value: null, source_ids: [] })),
    monetary_flow_input: {
      golden_growth: {
        observed_money_growth: row.inputs.observed_money_growth,
        real_growth_potential: row.inputs.real_growth,
        inflation_objective: row.inputs.inflation,
        tolerance: row.calculation.tolerance,
        source_ids: sourceIds
      }
    }
  };

  const run = await runWorkflow(
    definition,
    createHaeisExecutors({ intake, documents }),
    { run_id: 'VEN-HISTORICAL-MONETARY-FLOW-2009', initial_artifacts: { monetary_flow_input: intake.monetary_flow_input } }
  );

  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.nodes['source-verification'], 'PASS');
  assert.equal(run.nodes['venezuela-data-intake'], 'BLOCKED');
  assert.equal(run.nodes['monetary-flow-analysis'], 'PASS');
  assert.equal(run.nodes['red-team-1'], 'PASS');
  assert.equal(run.nodes['blue-team-1'], 'PASS');
  assert.equal(run.nodes['red-team-2'], 'BLOCKED');
  assert.equal(run.gates['critical-data-reconciled'], 'BLOCKED');
  assert.equal(run.gates['red-blue-red-complete'], 'BLOCKED');
  assert.equal(run.gates['chief-approved'], 'BLOCKED');

  const analysis = run.artifacts.monetary_flow_analysis as {
    status: string;
    attribution_status: string;
    calculations: Array<{ result: number; gap: number; source_data: string[] }>;
  };
  assert.equal(analysis.status, 'COMPUTED');
  assert.equal(analysis.attribution_status, 'FRAMEWORK_VERIFIED_SAE_232_234');
  assert.equal(analysis.calculations[0].result, row.calculation.result);
  assert.equal(analysis.calculations[0].gap, row.calculation.gap);
  assert.deepEqual(new Set(analysis.calculations[0].source_data), new Set(sourceIds));

  const red = run.artifacts.red_team as { status: string; findings: Array<{ finding_id: string; severity: string }> };
  assert.equal(red.status, 'DIAGNOSTIC_ONLY');
  assert.ok(red.findings.some((finding) => finding.finding_id === 'RED-DATA-001' && finding.severity === 'CRITICAL'));
});

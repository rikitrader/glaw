import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHaeisExecutors } from '../src/executors.ts';
import { runWorkflow } from '../src/workflow.ts';

const definition = JSON.parse(readFileSync(new URL('../workflows/venezuela-monetary-reform.json', import.meta.url), 'utf8'));
const productionDocuments = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;
const evidencePlan = JSON.parse(readFileSync(new URL('../intake/venezuela-evidence-search.json', import.meta.url), 'utf8'));

const fixtureDocument = {
  document_id: 'TEST-HAEIS-VEN-FIXTURE', title: 'Synthetic integration fixture — not economic evidence',
  author: ['HAEIS test harness'], source_url: 'https://example.invalid/haeis-test-fixture', status: 'VERIFIED',
  local_path: null, citation_anchor: 'synthetic integration fixture', authority_level: 7,
  document_type: 'test-fixture', primary_source: false
};

const item = (name: string, value: number, series_id: string) => ({ name, status: 'KNOWN', value, unit: 'synthetic test units', series_id, observation_date: '2024-01-01', release_date: '2024-02-01', source_ids: ['TEST-HAEIS-VEN-FIXTURE'] });

test('complete source-bound Venezuela workflow reaches conditional arbitration', async () => {
  const intake = {
    intake_id: 'INTAKE-VEN-INTEGRATION-001', question: 'Synthetic integration fixture only.', country: 'Venezuela', output_mode: 'POLICY',
    source_ids: ['TEST-HAEIS-VEN-FIXTURE', 'PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234', 'DOC-IMF-VEN-REO-2025'],
    human_reviewer: 'integration-test-reviewer', critical_unknowns: [], status: 'READY_FOR_ANALYSIS',
    data_intake: [
      item('money supply', 200, 'TEST-M2'), item('monetary base', 100, 'TEST-M0'), item('loans', 80, 'TEST-LOANS'),
      item('deposits', 100, 'TEST-DEPOSITS'), item('bank reserves', 10, 'TEST-RESERVES'), item('bank equity', 15, 'TEST-EQUITY'),
      item('risk weighted assets', 100, 'TEST-RWA'), item('government revenue', 80, 'TEST-REVENUE'), item('government spending', 100, 'TEST-SPENDING'),
      item('GDP', 200, 'TEST-GDP'), item('parallel FX', 12, 'TEST-PARALLEL-FX'), item('official FX', 10, 'TEST-OFFICIAL-FX'),
      item('dollar deposits', 30, 'TEST-FX-DEPOSITS'), item('eligible foreign reserves', 110, 'TEST-ELIGIBLE-RESERVES'),
      item('currency board liabilities', 100, 'TEST-CB-LIABILITIES'), item('exposure', 100, 'TEST-EXPOSURE'), item('LGD', 0.4, 'TEST-LGD')
    ],
    monetary_flow_input: {
      golden_growth_qtm: { observed_money_growth: 0.0609, inflation_target: 0.02, real_growth: 0.0225, velocity_change: -0.0201, source_ids: ['PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234'] },
      credit_counterparts_asset: { observation_date: '2023-12-31', release_date: '2024-01-31', unit: 'synthetic percent', broad_money_change: 0.08, bank_lending_change: 0.03, securities_change: 0.02, bank_reserves_change: 0.01, other_items_net_change: 0.02, source_ids: ['PAPER-HANKE-GG-232', 'PAPER-HANKE-GG-233', 'PAPER-HANKE-GG-234'] }
    },
    historical_comparables: [{ case_id: 'ecuador-1998-2000', source_ids: ['DOC-IMF-VEN-REO-2025'], scope: 'synthetic integration reference only' }]
  } as never;
  const documents = [...productionDocuments, fixtureDocument];
  const run = await runWorkflow(definition, createHaeisExecutors({ intake, documents, evidence_search_plan: evidencePlan }), {
    run_id: 'VEN-INTEGRATION-001',
    initial_artifacts: { human_approval: { status: 'APPROVED', reviewer_id: 'integration-test-reviewer' } }
  });
  assert.equal(run.status, 'COMPLETED');
  assert.equal(run.gates['intake-ready'], 'PASS');
  assert.equal(run.gates['citations-verified'], 'PASS');
  assert.equal(run.gates['critical-data-reconciled'], 'PASS');
  assert.equal(run.gates['calculations-reproduced'], 'PASS');
  assert.equal(run.gates['red-blue-red-complete'], 'PASS');
  assert.equal(run.gates['chief-approved'], 'PASS');
  assert.equal((run.artifacts.second_red_team as { status: string }).status, 'CONDITIONAL');
  assert.equal((run.artifacts.policy_decision as { status: string }).status, 'REVIEWED');
});

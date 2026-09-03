import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHaeisExecutors } from '../src/executors.ts';
import { runWorkflow } from '../src/workflow.ts';

const definition = JSON.parse(readFileSync(new URL('../workflows/venezuela-monetary-reform.json', import.meta.url), 'utf8'));
const intake = JSON.parse(readFileSync(new URL('../intake/venezuela-dollarization.json', import.meta.url), 'utf8'));
const documents = JSON.parse(readFileSync(new URL('../rag/document-index.json', import.meta.url), 'utf8')).documents;

test('real HAEIS executors pass source verification and block before unsupported economic analysis', async () => {
  const run = await runWorkflow(definition, createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents }), { run_id: 'VEN-TEST' });
  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.nodes['source-verification'], 'PASS');
  assert.equal(run.artifacts.verified_source_count, documents.filter((document) => document.status === 'VERIFIED').length);
  assert.equal(run.gate_records['intake-ready'].status, 'PASS');
  assert.equal(run.gate_records['citations-verified'].status, 'PASS');
  assert.equal(run.gate_records['citations-verified'].owner, 'haeis-executor');
  assert.ok(run.gate_records['citations-verified'].at);
  assert.deepEqual(run.gate_records['citations-verified'].evidence_ids, intake.source_ids);
  assert.equal(run.gate_records['critical-data-reconciled'].status, 'BLOCKED');
  assert.match(run.events.map((event) => JSON.stringify(event)).join('\n'), /unavailable|critical|data/i);
});

test('Venezuela diagnostic continuation reaches posture and the full Red/Blue/Red-II chain without opening policy gates', async () => {
  const run = await runWorkflow(definition, createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents }), { run_id: 'VEN-DIAGNOSTIC-INTEGRATION' });
  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.nodes['posture-matrix'], 'PASS');
  assert.equal(run.nodes['red-team-1'], 'PASS');
  assert.equal(run.nodes['blue-team-1'], 'PASS');
  assert.equal(run.nodes['red-team-2'], 'BLOCKED');
  assert.equal((run.artifacts.red_team as { status: string }).status, 'DIAGNOSTIC_ONLY');
  assert.equal((run.artifacts.second_red_team as { status: string }).status, 'UNRESOLVED');
  assert.equal(run.gates['critical-data-reconciled'], 'BLOCKED');
  assert.equal(run.gates['red-blue-red-complete'], 'BLOCKED');
  assert.equal(run.gates['chief-approved'], 'BLOCKED');
});

test('analysis executors compute only from complete, lineaged numeric inputs', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const context = { run_id: 'RUN-1', artifacts: { verified_source_count: 1, data_bundle: [
    { name: 'loans', value: 80, source_ids: ['DOC-IMF-001'] },
    { name: 'deposits', value: 100, source_ids: ['DOC-IMF-001'] },
    { name: 'bank reserves', value: 10, source_ids: ['DOC-IMF-001'] }
  ] }, gates: {}, nodes: {}, events: [] } as never;
  const result = executors['banking-analysis'](context);
  assert.equal(result.status, 'PASS');
  assert.equal((result.artifacts.banking_analysis as { status: string }).status, 'COMPUTED');
  assert.equal(((result.artifacts.banking_analysis as { calculations: Array<{ result: number }> }).calculations[0]).result, 0.8);
});

test('analysis executors block when a required metric is missing', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['exchange-rate-analysis']({ run_id: 'RUN-2', artifacts: { verified_source_count: 1, data_bundle: [{ name: 'official FX', value: 10, source_ids: ['DOC-IMF-001'] }] }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason ?? '', /supported numeric inputs/);
});

test('monetary-flow executor computes only source-verified Golden Growth and Credit Counterparts inputs', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['monetary-flow-analysis']({ run_id: 'RUN-FLOW-1', artifacts: { monetary_flow_input: {
    golden_growth: { observed_money_growth: 0.08, real_growth_potential: 0.03, inflation_objective: 0.02, source_ids: ['DOC-IMF-001'] },
    credit_counterparts: { observation_date: '2024-01-01', release_date: '2024-02-01', unit: 'percent of GDP', broad_money_change: 0.05, private_credit_change: 0.03, public_credit_change: 0.01, net_foreign_assets_change: 0.02, other_items_net_change: 0.01, source_ids: ['DOC-IMF-001'] }
  } }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  const analysis = result.artifacts.monetary_flow_analysis as { status: string; calculations: Array<{ formula: string; result: number }>; interpretation_blocked: boolean };
  assert.equal(analysis.status, 'COMPUTED');
  assert.equal(analysis.calculations.length, 2);
  assert.ok(Math.abs(analysis.calculations[1].result - 0.05) < 1e-12);
  assert.equal(analysis.interpretation_blocked, false);
});

test('monetary-flow executor runs the source-faithful SAE QTM and asset-side identities', () => {
  const verifiedDocs = documents.map((document: any) => document.document_id === 'PAPER-HANKE-GG-232' ? { ...document, status: 'VERIFIED' } : document);
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents: verifiedDocs });
  const result = executors['monetary-flow-analysis']({ run_id: 'RUN-FLOW-SAE', artifacts: { monetary_flow_input: {
    golden_growth_qtm: { observed_money_growth: 0.0609, inflation_target: 0.02, real_growth: 0.0225, velocity_change: -0.0201, source_ids: ['PAPER-HANKE-GG-232'] },
    credit_counterparts_asset: { observation_date: '2023-12-31', release_date: '2024-01-31', unit: 'percent', broad_money_change: 0.08, bank_lending_change: 0.03, securities_change: 0.02, bank_reserves_change: 0.01, other_items_net_change: 0.02, source_ids: ['PAPER-HANKE-GG-232'] }
  } }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  const analysis = result.artifacts.monetary_flow_analysis as { calculations: Array<{ formula: string }> };
  assert.ok(analysis.calculations.some((calculation) => calculation.formula === 'ΔM = ΔP + Δy − ΔV'));
  assert.ok(analysis.calculations.some((calculation) => calculation.formula.includes('Commercial Bank Lending')));
});

test('monetary-flow executor blocks restricted or unresolved paper lineage', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['monetary-flow-analysis']({ run_id: 'RUN-FLOW-2', artifacts: { monetary_flow_input: {
    golden_growth: { observed_money_growth: 0.08, real_growth_potential: 0.03, inflation_objective: 0.02, source_ids: ['DOC-HK-001'] }
  } }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason ?? '', /unverified or restricted/);
});

test('monetary-flow executor preserves a non-reconciled identity as an interpretation block', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['monetary-flow-analysis']({ run_id: 'RUN-FLOW-3', artifacts: { monetary_flow_input: {
    credit_counterparts: { observation_date: '2024-01-01', release_date: '2024-02-01', unit: 'currency', broad_money_change: 10, private_credit_change: 1, public_credit_change: 1, net_foreign_assets_change: 1, other_items_net_change: 1, source_ids: ['DOC-IMF-001'] }
  } }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  const analysis = result.artifacts.monetary_flow_analysis as { interpretation_blocked: boolean; warnings: string[] };
  assert.equal(analysis.interpretation_blocked, true);
  assert.match(analysis.warnings[0], /does not reconcile/);
});

test('Red Team, Blue Team, and second Red Team execute with residual-risk evidence', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const base = { run_id: 'RUN-3', artifacts: { verified_source_count: 1, data_bundle: [{ name: 'official FX', value: 10, source_ids: ['DOC-IMF-001'] }], exchange_rate_analysis: { status: 'COMPUTED', calculations: [{ result: 1, source_data: ['DOC-IMF-001'] }] } }, gates: {}, nodes: {}, events: [] } as never;
  const red = executors['red-team'](base);
  assert.equal(red.status, 'PASS');
  assert.ok(red.artifacts.red_team);
  const blue = executors['blue-team']({ ...base, artifacts: { ...base.artifacts, ...(red.artifacts ?? {}) } });
  assert.equal(blue.status, 'PASS');
  const second = executors['red-team-2']({ ...base, artifacts: { ...base.artifacts, ...(red.artifacts ?? {}), ...(blue.artifacts ?? {}) } });
  assert.equal(second.status, 'BLOCKED');
  assert.equal(second.gate_updates?.['red-blue-red-complete'], 'BLOCKED');
});

test('diagnostic Red Team records missing critical data without fabricating an analysis', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const definitionWithDiagnostic = { ...definition, diagnostic_continuation: { trigger_nodes: ['monetary-flow-analysis'], allowed_nodes: ['red-team-1'] } };
  const result = executors['red-team']({ run_id: 'RUN-DIAGNOSTIC-RED', workflow: definitionWithDiagnostic, node: { id: 'red-team-1', executor: 'red-team' }, artifacts: { verified_source_count: 1, verified_source_ids: ['DOC-IMF-001'] }, gates: {} } as never);
  assert.equal(result.status, 'PASS');
  const red = result.artifacts?.red_team as { status: string; findings: Array<{ finding_id: string; severity: string }> };
  assert.equal(red.status, 'DIAGNOSTIC_ONLY');
  assert.deepEqual(red.findings.map((finding) => [finding.finding_id, finding.severity]), [['RED-DATA-001', 'CRITICAL']]);
});

test('second Red Team passes conditionally when no critical risk remains', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const base = { run_id: 'RUN-3-CONDITIONAL', artifacts: {
    verified_source_count: 1,
    data_bundle: [{ name: 'official FX', value: 10, source_ids: ['DOC-IMF-001'] }],
    exchange_rate_analysis: { status: 'COMPUTED', calculations: [{ result: 1, source_data: ['DOC-IMF-001'] }] },
    'stress-test_analysis': { status: 'COMPUTED', calculations: [{ result: 1, source_data: ['DOC-IMF-001'] }] }
  }, gates: {}, nodes: {}, events: [] } as never;
  const red = executors['red-team'](base);
  const blue = executors['blue-team']({ ...base, artifacts: { ...base.artifacts, ...(red.artifacts ?? {}) } });
  const second = executors['red-team-2']({ ...base, artifacts: { ...base.artifacts, ...(red.artifacts ?? {}), ...(blue.artifacts ?? {}) } });
  assert.equal(second.status, 'PASS');
  assert.equal(second.gate_updates?.['red-blue-red-complete'], 'PASS');
  assert.equal((second.artifacts.second_red_team as { status: string }).status, 'CONDITIONAL');
});

test('math audit independently recomputes emitted calculations and updates the gate', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const context = { run_id: 'RUN-4', artifacts: { banking_analysis: { status: 'COMPUTED', calculations: [{ formula: 'loans / deposits', inputs: { loans: 80, deposits: 100 }, result: 0.8, source_data: ['DOC-IMF-001'] }] } }, gates: {}, nodes: {}, events: [] } as never;
  const result = executors['math-audit'](context);
  assert.equal(result.status, 'PASS');
  assert.equal(result.gate_updates?.['calculations-reproduced'], 'PASS');
});

test('math audit blocks tampered calculation output', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['math-audit']({ run_id: 'RUN-5', artifacts: { banking_analysis: { calculations: [{ formula: 'loans / deposits', inputs: { loans: 80, deposits: 100 }, result: 0.9, source_data: ['DOC-IMF-001'] }] } }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'BLOCKED');
  assert.equal(result.gate_updates?.['calculations-reproduced'], 'BLOCKED');
});

test('data forensics validates item-level verified lineage and temporal metadata', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['data-forensics']({ run_id: 'RUN-6', artifacts: { data_bundle: [{ name: 'M2', status: 'KNOWN', value: 10, unit: 'currency', series_id: 'M2', observation_date: '2024-01-01', release_date: '2024-02-01', revision_date: '2024-03-01', source_ids: ['DOC-IMF-001'] }] }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  assert.equal((result.artifacts.data_forensics as { checked: number }).checked, 1);
});

test('data forensics blocks unknown data source and duplicate series', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['data-forensics']({ run_id: 'RUN-7', artifacts: { data_bundle: [
    { name: 'M2', status: 'KNOWN', value: 10, unit: 'currency', series_id: 'M2', observation_date: '2024-01-01', source_ids: ['DOC-404'] },
    { name: 'M2 duplicate', status: 'KNOWN', value: 11, unit: 'currency', series_id: 'M2', observation_date: '2024-02-01', source_ids: ['DOC-404'] }
  ] }, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason ?? '', /non-verified source/);
  assert.match(result.reason ?? '', /duplicate data series/);
});

test('Chief passes automated arbitration and emits a final human-review packet', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const base = { run_id: 'RUN-8', artifacts: {}, gates: { 'red-blue-red-complete': 'PASS' }, nodes: {}, events: [] } as never;
  const result = executors.chief(base);
  assert.equal(result.gate_updates?.['chief-approved'], 'PASS');
  assert.equal((result.artifacts?.human_review_packet as { status: string }).status, 'AVAILABLE_FOR_REVIEW');
  assert.equal((result.artifacts?.human_review_packet as { review_required: boolean }).review_required, false);
});

test('policy decision blocks without recommendation readiness and anti-confirmation plans', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const gates = { 'critical-data-reconciled': 'PASS', 'calculations-reproduced': 'PASS', 'citations-verified': 'PASS', 'red-blue-red-complete': 'PASS', 'chief-approved': 'PASS' };
  const base = { run_id: 'RUN-9', artifacts: { intake_readiness: { readiness: 'RECOMMENDATION_READY' } }, gates, nodes: {}, events: [] } as never;
  const result = executors['policy-decision'](base);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason ?? '', /evidence-search plans/);
});

test('source search forwards the explicit evidence plan to the policy gate', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents, evidence_search_plan: {
    claim_id: 'C-1',
    searches: [
      { lane: 'SUPPORTING', query: 'support', source_ids: ['DOC-IMF-VEN-REO-2025'], result_status: 'FOUND', notes: 'verified' },
      { lane: 'CONTRADICTORY', query: 'contradictory', source_ids: [], result_status: 'NO_RESULT', notes: 'none' },
      { lane: 'ALTERNATIVE_EXPLANATION', query: 'alternative', source_ids: ['DOC-IMF-VEN-1999-SA'], result_status: 'FOUND', notes: 'historical' }
    ]
  } });
  const result = executors['source-search']({ run_id: 'RUN-LANES', artifacts: {}, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  assert.equal((result.artifacts.evidence_search_plans as unknown[]).length, 1);
});

test('historical and data-audit nodes pass from explicit evidence artifacts', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer', historical_comparables: [{ case_id: 'ecuador-1998-2000', source_ids: ['DOC-IMF-VEN-REO-2025'] }] }, documents });
  const context = { run_id: 'RUN-EVIDENCE', artifacts: { verified_source_count: 1, historical_comparables: [{ case_id: 'ecuador-1998-2000' }], data_forensics: { errors: [], checked: 12 } }, gates: {}, nodes: {}, events: [] } as never;
  assert.equal(executors['historical-comparables'](context).status, 'PASS');
  assert.equal(executors['data-audit'](context).status, 'PASS');
});

test('posture executor emits a complete pending matrix without inventing assessments', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents });
  const result = executors['posture-matrix']({ run_id: 'RUN-10', artifacts: {}, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'PASS');
  const matrix = result.artifacts.posture_matrix as { status: string; cells: Array<{ status: string }> };
  assert.equal(matrix.status, 'PENDING_SOURCE_REVIEW');
  assert.equal(matrix.cells.length, 14);
  assert.ok(matrix.cells.every((cell) => cell.status === 'PENDING_SOURCE_REVIEW'));
});

test('posture executor blocks evidence claims bound to restricted sources', () => {
  const executors = createHaeisExecutors({ intake: { ...intake, human_reviewer: 'test-reviewer' }, documents, posture_assessments: [{ case_id: 'venezuela-current', posture_id: 'hanke', shared_facts: ['x'], assumptions: ['x'], mechanism: 'x', supporting_evidence: ['DOC-HK-001'], contradictory_evidence: [], falsifiers: ['x'], claims: [{ text: 'x', label: 'HANKE-DIRECT', source_ids: ['DOC-HK-001'], citation_anchors: ['x'] }], assessment: 'INSUFFICIENT_EVIDENCE', confidence: 'VERY LOW' }] });
  const result = executors['posture-matrix']({ run_id: 'RUN-11', artifacts: {}, gates: {}, nodes: {}, events: [] } as never);
  assert.equal(result.status, 'BLOCKED');
  assert.match(result.reason ?? '', /non-verified source/);
});

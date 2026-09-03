import test from 'node:test';
import assert from 'node:assert/strict';
import { creditCounterpartAssetResidual, creditCounterpartsResidual, goldenGrowthGap, goldenGrowthRate, goldenGrowthRateQtm } from '../src/monetary-flow.ts';
import { auditCalculationArtifacts } from '../src/math-audit.ts';

test('golden growth rate compounds explicit real-growth and inflation inputs', () => {
  const result = goldenGrowthRate(0.02, 0.02, ['SAE-232']);
  assert.equal(result.formula, '(1 + real_growth_potential) * (1 + inflation_objective) - 1');
  assert.ok(Math.abs(result.result - 0.0404) < 1e-12);
  assert.deepEqual(result.source_ids, ['SAE-232']);
});

test('golden growth gap classifies observed money growth with tolerance', () => {
  const result = goldenGrowthGap(0.06, 0.02, 0.02, 0.005, ['SAE-232']);
  assert.equal(result.interpretation, 'ABOVE_BENCHMARK');
  assert.ok(Math.abs(result.gap - 0.0196) < 1e-12);
});

test('credit counterparts identity reconciles and preserves provenance', () => {
  const result = creditCounterpartsResidual({ observation_date: '2023-12-31', release_date: '2024-02-15', unit: 'VES million', broad_money_change: 100, private_credit_change: 40, public_credit_change: 30, net_foreign_assets_change: 50, other_items_net_change: 20, source_ids: ['BCV-M2-2023', 'BCV-BALANCE-SHEET-2023'] });
  assert.equal(result.implied_broad_money_change, 100);
  assert.equal(result.identity_error, 0);
  assert.equal(result.reconciled, true);
});

test('credit counterparts blocks unexplained residual interpretation', () => {
  const result = creditCounterpartsResidual({ observation_date: '2023-12-31', release_date: '2024-02-15', unit: 'VES million', broad_money_change: 100, private_credit_change: 40, public_credit_change: 30, net_foreign_assets_change: 50, other_items_net_change: 10, source_ids: ['S-1'] });
  assert.equal(result.reconciled, false);
  assert.ok(result.warnings.some((warning) => warning.includes('does not reconcile')));
});

test('math audit independently recomputes monetary-flow formulas', () => {
  const benchmark = goldenGrowthRate(0.02, 0.02, ['SAE-232']);
  const flow = creditCounterpartsResidual({ observation_date: '2023-12-31', release_date: '2024-02-15', unit: 'VES million', broad_money_change: 100, private_credit_change: 40, public_credit_change: 30, net_foreign_assets_change: 50, other_items_net_change: 20, source_ids: ['S-1'] });
  const audit = auditCalculationArtifacts({ monetary: { calculations: [{ formula: benchmark.formula, inputs: benchmark.inputs, result: benchmark.result, source_data: benchmark.source_ids }, { formula: flow.formula, inputs: { private_credit_change: 40, public_credit_change: 30, net_foreign_assets_change: 50, other_items_net_change: 20 }, result: flow.implied_broad_money_change, source_data: flow.source_ids }] } });
  assert.equal(audit.checked, 2);
  assert.deepEqual(audit.errors, []);
});

test('math audit independently recomputes the SAE QTM and asset-side formulas', () => {
  const audit = auditCalculationArtifacts({ monetary: { calculations: [
    { formula: 'ΔM = ΔP + Δy − ΔV', inputs: { inflation_target: 0.02, real_growth: 0.0225, velocity_change: -0.0201 }, result: 0.0626, source_data: ['PAPER-HANKE-GG-232'] },
    { formula: 'Δ Broad Money = Δ Commercial Bank Lending + Δ Securities + Δ Commercial Bank Reserves +/− Δ Others (net)', inputs: { bank_lending_change: 0.03, securities_change: 0.02, bank_reserves_change: 0.01, other_items_net_change: 0.02 }, result: 0.08, source_data: ['PAPER-HANKE-GG-232'] }
  ] } });
  assert.equal(audit.checked, 2);
  assert.deepEqual(audit.errors, []);
});

test('SAE Golden Growth formula uses percent-change QTM with velocity', () => {
  const result = goldenGrowthRateQtm(0.02, 0.0225, -0.0201, ['PAPER-HANKE-GG-232']);
  assert.equal(result.formula, 'ΔM = ΔP + Δy − ΔV');
  assert.ok(Math.abs(result.result - 0.0626) < 1e-12);
  assert.deepEqual(result.source_ids, ['PAPER-HANKE-GG-232']);
});

test('SAE Credit Counterpart asset identity reconciles lending, securities, reserves, and others', () => {
  const result = creditCounterpartAssetResidual({ observation_date: '2023-12-31', release_date: '2024-01-31', unit: 'percent', broad_money_change: 0.08, bank_lending_change: 0.03, securities_change: 0.02, bank_reserves_change: 0.01, other_items_net_change: 0.02, source_ids: ['PAPER-HANKE-GG-232'] });
  assert.equal(result.reconciled, true);
  assert.equal(result.formula, 'Δ Broad Money = Δ Commercial Bank Lending + Δ Securities + Δ Commercial Bank Reserves +/− Δ Others (net)');
});

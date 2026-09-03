import test from 'node:test';
import assert from 'node:assert/strict';
import { runAggregateAgentBasedModel, runLinearizedMacroModel, runSystemDynamics } from '../src/advanced-models.ts';

const shocks = [{ oil: 1, inflation: 0.1, fiscal: 0.1, deposit: 0.05, capital_flight: 0.02, productivity: 0, sanctions: 0, fdi: 0.1 }, { oil: -0.5, inflation: 0.2, fiscal: 0.2, deposit: 0.3, capital_flight: 0.1, productivity: -0.1, sanctions: 0.1, fdi: 0 }];
const parameters = { output_persistence: 0.8, inflation_persistence: 0.7, credit_persistence: 0.8, reserve_persistence: 0.9, inflation_sensitivity_to_output: 0.1, credit_sensitivity_to_liquidity: 0.5, reserve_sensitivity_to_oil: 1, reserve_sensitivity_to_fdi: 1, import_sensitivity_to_output: 0.2, fiscal_sensitivity_to_output: 0.1, sovereign_liquidity_support: 0.05, dollarized_liquidity_constraint: 0.5 };

test('linearized macro model is deterministic, source-bound, and explicitly limited', () => {
  const input = { regime: 'DOLLARIZED' as const, initial_state: { output_gap: 0, inflation: 0.1, credit: 100, reserves: 50, fiscal_balance: -0.1 }, shocks, parameters, source_ids: ['SRC-MODEL'] };
  const first = runLinearizedMacroModel(input); const second = runLinearizedMacroModel(input);
  assert.deepEqual(first, second);
  assert.equal(first.model, 'LINEARIZED_DSGE_STYLE_PROTOTYPE');
  assert.equal(first.rows[0].status, 'MODELED');
  assert.ok(first.limitations.some((item) => item.includes('causal')));
});

test('system-dynamics loop preserves reserves-after-imports state transitions', () => {
  const rows = runSystemDynamics({ initial: { output_gap: 0, inflation: 0, credit: 10, reserves: 50, fiscal_balance: 0 }, shocks, source_ids: ['SRC-SYSTEM'] });
  assert.equal(rows.length, 2);
  assert.ok(Number.isFinite(rows[1].reserves_after_imports));
  assert.equal(rows[0].status, 'MODELED');
});

test('aggregate agent model keeps preferences bounded and deterministic', () => {
  const rows = runAggregateAgentBasedModel({ households: 100, banks: 10, businesses: 50, initial_usd_preference: 0.5, initial_deposit_preference: 0.8, shocks, source_ids: ['SRC-ABM'] });
  assert.equal(rows.length, 2);
  for (const row of rows) for (const value of Object.values(row).filter((value): value is number => typeof value === 'number')) assert.ok(value >= 0 && value <= 1 || Number.isInteger(value));
});

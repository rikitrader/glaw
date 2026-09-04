import test from 'node:test';
import assert from 'node:assert/strict';
import { creditContractionStressGrid, depositWithdrawalStressGrid, oilStressGrid } from '../src/stress-matrix.ts';

test('deposit withdrawal grid is deterministic and exposes liquidity shortfalls', () => {
  const rows = depositWithdrawalStressGrid({ deposits: 100, liquid_assets: 10, emergency_buffer: 5, baseline_credit: 80, baseline_gdp: 200, credit_elasticity: 1, source_ids: ['SRC-1'] }, [0.05, 0.3, 0.5]);
  assert.equal(rows.length, 3);
  assert.equal(rows[0].outputs.liquidity_shortfall, 0);
  assert.equal(rows[2].outputs.emergency_liquidity_needed, 35);
  assert.equal(rows[2].outputs.modeled_credit, 52);
  assert.equal(rows[2].status, 'MODELED');
});

test('oil grid preserves source lineage and separates gross from usable FX', () => {
  const rows = oilStressGrid({ production_bpd: 1000, oil_price: 60, deduction_rate: 0.25, government_take: 0.5, source_ids: ['OIL-SRC'] }, [40, 60], [1000, 2000]);
  assert.equal(rows.length, 4);
  assert.equal(rows[0].outputs.gross_annual_revenue, 40 * 1000 * 365);
  assert.equal(rows[0].outputs.usable_sovereign_fx, rows[0].outputs.gross_annual_revenue * 0.75 * 0.5);
  assert.deepEqual(rows[0].source_ids, ['OIL-SRC']);
});

test('credit-contraction grid is bounded and does not claim causal identification', () => {
  const rows = creditContractionStressGrid({ baseline_credit: 100, baseline_gdp: 200, credit_to_gdp_elasticity: 0.5, source_ids: ['CREDIT-SRC'] }, [0, 0.2, 0.5]);
  assert.equal(rows[1].outputs.remaining_credit, 80);
  assert.equal(rows[2].outputs.modeled_gdp_effect, -50);
  assert.ok(rows[2].assumptions.some((assumption) => assumption.includes('does not establish causality')));
});

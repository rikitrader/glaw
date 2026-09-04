import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { goldenGrowthGap } from '../src/monetary-flow.ts';

const audit = JSON.parse(readFileSync(new URL('../datasets/venezuela-historical-monetary-flow-audit.json', import.meta.url), 'utf8'));

test('historical monetary-flow audit is source-bound and reproducible', () => {
  assert.deepEqual(audit.rows.map((row: { year: number }) => row.year), [2009, 2010, 2011, 2012, 2013]);
  for (const row of audit.rows) {
    const recomputed = goldenGrowthGap(row.inputs.observed_money_growth, row.inputs.real_growth, row.inputs.inflation, 0.005, row.source_ids);
    assert.equal(recomputed.result, row.calculation.result);
    assert.equal(recomputed.gap, row.calculation.gap);
    assert.equal(row.status, 'HISTORICAL_ONLY');
    assert.equal(row.calculation.unit, 'ratio');
    assert.equal(row.source_ids.length, 3);
  }
});

test('historical monetary-flow audit does not claim current policy evidence', () => {
  assert.ok(audit.rows.every((row: { notes: string }) => row.notes.includes('does not') && row.notes.includes('policy recommendation')));
});

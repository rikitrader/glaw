import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { goldenGrowthGap } from '../src/monetary-flow.ts';

const root = resolve(new URL('..', import.meta.url).pathname);
const worldBank = JSON.parse(readFileSync(resolve(root, 'datasets/venezuela-world-bank-observations.json'), 'utf8')).observations;
const imf = JSON.parse(readFileSync(resolve(root, 'datasets/venezuela-imf-mfs-observations.json'), 'utf8')).observations;
const byVariableYear = (variable) => new Map(worldBank.filter((observation) => observation.variable === variable).map((observation) => [observation.date.slice(0, 4), observation]));
const growth = byVariableYear('real_GDP_growth');
const inflation = byVariableYear('CPI_inflation');
const broadMoney = new Map(imf.filter((observation) => observation.variable === 'broad_money').map((observation) => [observation.date, observation]));
const rows = [];
for (let year = 2002; year <= 2014; year += 1) {
  const current = broadMoney.get(`${year}-12-31`);
  const previous = broadMoney.get(`${year - 1}-12-31`);
  const realGrowth = growth.get(String(year));
  const cpi = inflation.get(String(year));
  if (!current || !previous || !realGrowth || !cpi) continue;
  if (current.unit !== previous.unit) throw new Error(`broad-money unit mismatch: ${year}`);
  const observed = current.value / previous.value - 1;
  const result = goldenGrowthGap(observed, realGrowth.value / 100, cpi.value / 100, 0.005, [current.source_id, previous.source_id, realGrowth.source_id, cpi.source_id]);
  rows.push({
    year, observation_date: current.date, previous_observation_date: previous.date, unit: current.unit, source_ids: result.source_ids,
    inputs: { observed_money_growth: observed, real_growth: realGrowth.value / 100, inflation: cpi.value / 100 },
    calculation: result, status: 'HISTORICAL_ONLY',
    notes: 'Deterministic historical comparison only. It does not estimate velocity, establish causality, validate current monetary conditions, or authorize a policy recommendation.'
  });
}
if (!rows.length) throw new Error('no aligned historical monetary-flow rows were found');
writeFileSync(resolve(root, 'datasets/venezuela-historical-monetary-flow-audit.json'), JSON.stringify({ dataset_id: 'VEN-HISTORICAL-MONETARY-FLOW-AUDIT', status: 'VERIFIED_SOURCE_BOUND_HISTORICAL_ONLY', rows }, null, 2));
console.log(JSON.stringify({ status: 'PASS', rows: rows.length, years: rows.map((row) => row.year), output: 'datasets/venezuela-historical-monetary-flow-audit.json' }, null, 2));

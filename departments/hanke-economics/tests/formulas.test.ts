import test from 'node:test';
import assert from 'node:assert/strict';
import { compoundInflation, debtToGdp, parallelPremium, reserveCoverage, stressLoss } from '../src/formulas.ts';

test('compound inflation is deterministic', () => assert.equal(compoundInflation([0.1, 0.1]).result, 0.2100000000000002));
test('parallel premium uses the documented convention', () => assert.ok(Math.abs(parallelPremium(120, 100).result - 0.2) < 1e-12));
test('reserve coverage is a ratio of eligible reserves to liabilities', () => assert.equal(reserveCoverage(110, 100).result, 1.1));
test('debt to GDP rejects non-positive GDP', () => assert.throws(() => debtToGdp(100, 0), /gdp must be positive/));
test('stress loss is exposure times LGD', () => assert.equal(stressLoss(100, 0.4).result, 40));

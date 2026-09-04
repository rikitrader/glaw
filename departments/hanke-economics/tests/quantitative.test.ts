import test from 'node:test';
import assert from 'node:assert/strict';
import { capitalAdequacy, compoundInflation, creditToGdp, currentAccount, debtSustainability, debtToGdp, depositDollarization, depositsToGdp, fiscalDeficitToGdp, fxDepreciation, fxMismatch, inflationRate, interestToRevenue, liquidityGap, loanToDeposit, monetaryGrowth, moneyMultiplier, parallelPremium, realCreditGrowth, realInterestRate, reserveCoverage, reserveRatio, stressLoss } from '../src/formulas.ts';
import { REQUIRED_SCENARIOS, validateScenarios } from '../src/scenarios.ts';
import { uniformMonteCarlo } from '../src/monte-carlo.ts';
import { auditCalculationArtifacts } from '../src/math-audit.ts';

test('required banking and public-finance formulas are deterministic', () => {
  assert.equal(moneyMultiplier(200, 100).result, 2);
  assert.equal(creditToGdp(50, 100).result, 0.5);
  assert.equal(loanToDeposit(120, 100).result, 1.2);
  assert.equal(reserveRatio(10, 100).result, 0.1);
  assert.equal(liquidityGap(80, 100).result, -20);
  assert.equal(fxMismatch(40, 60).result, -20);
  assert.equal(interestToRevenue(20, 100).result, 0.2);
  assert.equal(capitalAdequacy(10, 100).result, 0.1);
});

test('current account, real credit growth, and debt sustainability are explicit', () => {
  assert.equal(currentAccount(100, 70, -10, 20).result, 40);
  assert.ok(Math.abs(realCreditGrowth(0.2, 0.1).result - 0.09090909090909083) < 1e-12);
  assert.equal(debtSustainability(2, 0.1, 0.05, 100).result, 3);
});

test('all core formula families expose deterministic inputs and outputs', () => {
  assert.ok(Math.abs(inflationRate(100, 110).result - 0.1) < 1e-12);
  assert.ok(Math.abs(compoundInflation([0.1, 0.2]).result - 0.32) < 1e-12);
  assert.equal(monetaryGrowth(100, 125).result, 0.25);
  assert.ok(Math.abs(fxDepreciation(10, 12).result - 0.2) < 1e-12);
  assert.ok(Math.abs(parallelPremium(12, 10).result - 0.2) < 1e-12);
  assert.equal(reserveCoverage(110, 100).result, 1.1);
  assert.equal(fiscalDeficitToGdp(80, 100, 200).result, 0.1);
  assert.equal(realInterestRate(0.1, 0.05).result, (1.1 / 1.05) - 1);
  assert.equal(depositDollarization(30, 100).result, 0.3);
  assert.equal(stressLoss(100, 0.4).result, 40);
});

test('independent math audit covers the complete core formula library', () => {
  const calculations = [
    inflationRate(100, 110), compoundInflation([0.1, 0.2]), monetaryGrowth(100, 125), fxDepreciation(10, 12),
    parallelPremium(12, 10), reserveCoverage(110, 100), debtToGdp(50, 100), fiscalDeficitToGdp(80, 100, 200),
    realInterestRate(0.1, 0.05), depositDollarization(30, 100), stressLoss(100, 0.4), moneyMultiplier(200, 100),
    creditToGdp(50, 100), loanToDeposit(120, 100), depositsToGdp(40, 100), reserveRatio(10, 100),
    liquidityGap(80, 100), fxMismatch(40, 60), interestToRevenue(20, 100), currentAccount(100, 70, -10, 20),
    realCreditGrowth(0.2, 0.1), capitalAdequacy(10, 100), debtSustainability(2, 0.1, 0.05, 100)
  ];
  const audit = auditCalculationArtifacts({ complete_formula_fixture: { calculations } });
  assert.equal(audit.checked, calculations.length);
  assert.deepEqual(audit.errors, []);
});

test('scenario engine requires all five cases', () => assert.deepEqual(validateScenarios(REQUIRED_SCENARIOS.map((kind) => ({ id: kind, kind, assumptions: [], inputs: {}, source_ids: [] }))), []));
test('Monte Carlo output is reproducible by seed', () => assert.deepEqual(uniformMonteCarlo({ name: 'oil', min: 50, max: 100 }, 100, 42), uniformMonteCarlo({ name: 'oil', min: 50, max: 100 }, 100, 42)));

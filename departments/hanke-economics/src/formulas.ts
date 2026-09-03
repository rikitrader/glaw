import type { CalculationResult } from './types.ts';

const finite = (name: string, value: number) => {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
};

const result = (formula: string, inputs: Record<string, number | string | number[]>, value: number, unit: string, assumptions: string[] = []): CalculationResult => ({
  formula, inputs, result: finite('result', value), unit, source_data: [], assumptions, verification: 'PASS'
});

export function inflationRate(oldPrice: number, newPrice: number): CalculationResult {
  finite('oldPrice', oldPrice); finite('newPrice', newPrice);
  if (oldPrice <= 0) throw new Error('oldPrice must be positive');
  return result('(newPrice / oldPrice) - 1', { oldPrice, newPrice }, newPrice / oldPrice - 1, 'ratio');
}

export function compoundInflation(rates: number[]): CalculationResult {
  if (!rates.length) throw new Error('rates must not be empty');
  const factor = rates.reduce((acc, rate) => acc * (1 + finite('rate', rate)), 1);
  return result('product(1 + rate_i) - 1', { rates: [...rates] }, factor - 1, 'ratio');
}

export function monetaryGrowth(oldMoney: number, newMoney: number): CalculationResult {
  if (oldMoney <= 0) throw new Error('oldMoney must be positive');
  return result('(newMoney / oldMoney) - 1', { oldMoney, newMoney }, newMoney / oldMoney - 1, 'ratio');
}

export function fxDepreciation(oldFx: number, newFx: number): CalculationResult {
  if (oldFx <= 0) throw new Error('oldFx must be positive');
  return result('(newFx / oldFx) - 1', { oldFx, newFx }, newFx / oldFx - 1, 'ratio');
}

export function parallelPremium(parallelFx: number, officialFx: number): CalculationResult {
  if (officialFx <= 0) throw new Error('officialFx must be positive');
  return result('parallelFx / officialFx - 1', { parallelFx, officialFx }, parallelFx / officialFx - 1, 'ratio');
}

export function reserveCoverage(liquidReserves: number, monetaryLiabilities: number): CalculationResult {
  if (monetaryLiabilities <= 0) throw new Error('monetaryLiabilities must be positive');
  return result('liquidEligibleForeignReserves / currencyBoardMonetaryLiabilities', { liquidReserves, monetaryLiabilities }, liquidReserves / monetaryLiabilities, 'ratio');
}

export function debtToGdp(debt: number, gdp: number): CalculationResult {
  if (gdp <= 0) throw new Error('gdp must be positive');
  return result('debt / gdp', { debt, gdp }, debt / gdp, 'ratio');
}

export function fiscalDeficitToGdp(revenue: number, spending: number, gdp: number): CalculationResult {
  if (gdp <= 0) throw new Error('gdp must be positive');
  return result('(spending - revenue) / gdp', { revenue, spending, gdp }, (spending - revenue) / gdp, 'ratio');
}

export function realInterestRate(nominalRate: number, inflation: number): CalculationResult {
  return result('(1 + nominalRate) / (1 + inflation) - 1', { nominalRate, inflation }, (1 + nominalRate) / (1 + inflation) - 1, 'ratio');
}

export function depositDollarization(fxDeposits: number, totalDeposits: number): CalculationResult {
  if (totalDeposits <= 0) throw new Error('totalDeposits must be positive');
  return result('fxDeposits / totalDeposits', { fxDeposits, totalDeposits }, fxDeposits / totalDeposits, 'ratio');
}

export function stressLoss(exposure: number, lossGivenDefault: number): CalculationResult {
  if (exposure < 0 || lossGivenDefault < 0 || lossGivenDefault > 1) throw new Error('invalid stress inputs');
  return result('exposure * lossGivenDefault', { exposure, lossGivenDefault }, exposure * lossGivenDefault, 'currency');
}

export function moneyMultiplier(moneySupply: number, monetaryBase: number): CalculationResult {
  if (monetaryBase <= 0) throw new Error('monetaryBase must be positive');
  return result('moneySupply / monetaryBase', { moneySupply, monetaryBase }, moneySupply / monetaryBase, 'ratio');
}

export function creditToGdp(credit: number, gdp: number): CalculationResult {
  if (gdp <= 0) throw new Error('gdp must be positive');
  return result('credit / gdp', { credit, gdp }, credit / gdp, 'ratio');
}

export function loanToDeposit(loans: number, deposits: number): CalculationResult {
  if (deposits <= 0) throw new Error('deposits must be positive');
  return result('loans / deposits', { loans, deposits }, loans / deposits, 'ratio');
}

export function depositsToGdp(deposits: number, gdp: number): CalculationResult {
  if (gdp <= 0) throw new Error('gdp must be positive');
  return result('deposits / gdp', { deposits, gdp }, deposits / gdp, 'ratio');
}

export function reserveRatio(reserves: number, deposits: number): CalculationResult {
  if (deposits <= 0) throw new Error('deposits must be positive');
  return result('reserves / deposits', { reserves, deposits }, reserves / deposits, 'ratio');
}

export function liquidityGap(liquidAssets: number, shortTermLiabilities: number): CalculationResult {
  return result('liquidAssets - shortTermLiabilities', { liquidAssets, shortTermLiabilities }, liquidAssets - shortTermLiabilities, 'currency');
}

export function fxMismatch(fxAssets: number, fxLiabilities: number): CalculationResult {
  return result('fxAssets - fxLiabilities', { fxAssets, fxLiabilities }, fxAssets - fxLiabilities, 'currency');
}

export function interestToRevenue(interest: number, revenue: number): CalculationResult {
  if (revenue <= 0) throw new Error('revenue must be positive');
  return result('interest / revenue', { interest, revenue }, interest / revenue, 'ratio');
}

export function currentAccount(goodExports: number, goodImports: number, netIncome: number, netTransfers: number): CalculationResult {
  return result('exports - imports + netIncome + netTransfers', { goodExports, goodImports, netIncome, netTransfers }, goodExports - goodImports + netIncome + netTransfers, 'currency');
}

export function realCreditGrowth(nominalCreditGrowth: number, inflation: number): CalculationResult {
  return result('(1 + nominalCreditGrowth) / (1 + inflation) - 1', { nominalCreditGrowth, inflation }, (1 + nominalCreditGrowth) / (1 + inflation) - 1, 'ratio');
}

export function capitalAdequacy(capital: number, riskWeightedAssets: number): CalculationResult {
  if (riskWeightedAssets <= 0) throw new Error('riskWeightedAssets must be positive');
  return result('capital / riskWeightedAssets', { capital, riskWeightedAssets }, capital / riskWeightedAssets, 'ratio');
}

export function debtSustainability(primaryBalance: number, nominalInterestRate: number, nominalGrowthRate: number, debt: number): CalculationResult {
  if (debt <= 0) throw new Error('debt must be positive');
  return result('(nominalInterestRate - nominalGrowthRate) * debt - primaryBalance', { primaryBalance, nominalInterestRate, nominalGrowthRate, debt }, (nominalInterestRate - nominalGrowthRate) * debt - primaryBalance, 'currency', ['A positive result indicates an increase in the debt ratio absent offsetting changes.']);
}

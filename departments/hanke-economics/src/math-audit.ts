export interface AuditableCalculation { formula: string; inputs: Record<string, number | string | number[]>; result: number; source_data?: string[]; }
export interface MathAuditResult { checked: number; errors: string[]; source_ids: string[]; }

function numeric(inputs: Record<string, number | string | number[]>, key: string): number {
  const value = inputs[key];
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`input ${key} is not a finite number`);
  return value;
}

function numbers(inputs: Record<string, number | string | number[]>, key: string): number[] {
  const value = inputs[key];
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'number' || !Number.isFinite(item))) throw new Error(`input ${key} must be an array of finite numbers`);
  return value;
}

/** Independent arithmetic recomputation. It intentionally does not call the production formula functions. */
export function recomputeCalculation(calculation: AuditableCalculation): number {
  const i = calculation.inputs;
  switch (calculation.formula) {
    case '(newPrice / oldPrice) - 1': return numeric(i, 'newPrice') / numeric(i, 'oldPrice') - 1;
    case 'product(1 + rate_i) - 1': return numbers(i, 'rates').reduce((acc, rate) => acc * (1 + rate), 1) - 1;
    case '(newMoney / oldMoney) - 1': return numeric(i, 'newMoney') / numeric(i, 'oldMoney') - 1;
    case '(newFx / oldFx) - 1': return numeric(i, 'newFx') / numeric(i, 'oldFx') - 1;
    case 'debt / gdp': return numeric(i, 'debt') / numeric(i, 'gdp');
    case 'real interest rate': return (1 + numeric(i, 'nominalRate')) / (1 + numeric(i, 'inflation')) - 1;
    case '(1 + nominalRate) / (1 + inflation) - 1': return (1 + numeric(i, 'nominalRate')) / (1 + numeric(i, 'inflation')) - 1;
    case 'credit / gdp': return numeric(i, 'credit') / numeric(i, 'gdp');
    case 'deposits / gdp': return numeric(i, 'deposits') / numeric(i, 'gdp');
    case 'liquidAssets - shortTermLiabilities': return numeric(i, 'liquidAssets') - numeric(i, 'shortTermLiabilities');
    case 'fxAssets - fxLiabilities': return numeric(i, 'fxAssets') - numeric(i, 'fxLiabilities');
    case 'interest / revenue': return numeric(i, 'interest') / numeric(i, 'revenue');
    case 'exports - imports + netIncome + netTransfers': return numeric(i, 'goodExports') - numeric(i, 'goodImports') + numeric(i, 'netIncome') + numeric(i, 'netTransfers');
    case '(1 + nominalCreditGrowth) / (1 + inflation) - 1': return (1 + numeric(i, 'nominalCreditGrowth')) / (1 + numeric(i, 'inflation')) - 1;
    case '(nominalInterestRate - nominalGrowthRate) * debt - primaryBalance': return (numeric(i, 'nominalInterestRate') - numeric(i, 'nominalGrowthRate')) * numeric(i, 'debt') - numeric(i, 'primaryBalance');
    case 'moneySupply / monetaryBase': return numeric(i, 'moneySupply') / numeric(i, 'monetaryBase');
    case 'loans / deposits': return numeric(i, 'loans') / numeric(i, 'deposits');
    case 'reserves / deposits': return numeric(i, 'reserves') / numeric(i, 'deposits');
    case 'capital / riskWeightedAssets': return numeric(i, 'capital') / numeric(i, 'riskWeightedAssets');
    case '(spending - revenue) / gdp': return (numeric(i, 'spending') - numeric(i, 'revenue')) / numeric(i, 'gdp');
    case 'parallelFx / officialFx - 1': return numeric(i, 'parallelFx') / numeric(i, 'officialFx') - 1;
    case 'fxDeposits / totalDeposits': return numeric(i, 'fxDeposits') / numeric(i, 'totalDeposits');
    case 'liquidEligibleForeignReserves / currencyBoardMonetaryLiabilities': return numeric(i, 'liquidReserves') / numeric(i, 'monetaryLiabilities');
    case 'exposure * lossGivenDefault': return numeric(i, 'exposure') * numeric(i, 'lossGivenDefault');
    case '(1 + real_growth_potential) * (1 + inflation_objective) - 1': return (1 + numeric(i, 'real_growth_potential')) * (1 + numeric(i, 'inflation_objective')) - 1;
    case 'ΔM = ΔP + Δy − ΔV': return numeric(i, 'inflation_target') + numeric(i, 'real_growth') - numeric(i, 'velocity_change');
    case 'Δbroad_money = Δprivate_credit + Δpublic_credit + Δnet_foreign_assets − Δother_items_net': return numeric(i, 'private_credit_change') + numeric(i, 'public_credit_change') + numeric(i, 'net_foreign_assets_change') - numeric(i, 'other_items_net_change');
    case 'Δ Broad Money = Δ Commercial Bank Lending + Δ Securities + Δ Commercial Bank Reserves +/− Δ Others (net)': return numeric(i, 'bank_lending_change') + numeric(i, 'securities_change') + numeric(i, 'bank_reserves_change') + numeric(i, 'other_items_net_change');
    default: throw new Error(`unsupported formula for independent audit: ${calculation.formula}`);
  }
}

export function auditCalculationArtifacts(artifacts: Record<string, unknown>, tolerance = 1e-10): MathAuditResult {
  const calculations = Object.values(artifacts).flatMap((artifact) => {
    if (!artifact || typeof artifact !== 'object' || !Array.isArray((artifact as { calculations?: unknown[] }).calculations)) return [];
    return (artifact as { calculations: AuditableCalculation[] }).calculations;
  });
  const errors: string[] = [];
  const source_ids = [...new Set(calculations.flatMap((calculation) => calculation.source_data ?? []))];
  calculations.forEach((calculation, index) => {
    try {
      const expected = recomputeCalculation(calculation);
      if (!Number.isFinite(calculation.result) || Math.abs(expected - calculation.result) > tolerance * Math.max(1, Math.abs(expected))) errors.push(`calculation ${index} mismatch for ${calculation.formula}`);
    } catch (error) { errors.push(`calculation ${index} audit error: ${error instanceof Error ? error.message : String(error)}`); }
  });
  return { checked: calculations.length, errors, source_ids };
}

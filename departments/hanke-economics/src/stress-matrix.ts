export interface StressScenarioPoint {
  scenario_id: string;
  shock: number;
  shock_unit: string;
  outputs: Record<string, number>;
  status: 'MODELED';
  source_ids: string[];
  assumptions: string[];
}

export interface DepositRunInput {
  deposits: number;
  liquid_assets: number;
  emergency_buffer: number;
  baseline_credit: number;
  baseline_gdp: number;
  credit_elasticity: number;
  source_ids: string[];
}

export interface OilStressInput {
  production_bpd: number;
  oil_price: number;
  annual_days?: number;
  deduction_rate: number;
  government_take: number;
  source_ids: string[];
}

export interface CreditStressInput {
  baseline_credit: number;
  baseline_gdp: number;
  credit_to_gdp_elasticity: number;
  source_ids: string[];
}

const finiteNonNegative = (name: string, value: number): void => {
  if (!Number.isFinite(value) || value < 0) throw new Error(`${name} must be a finite non-negative number`);
};

const requireSources = (sourceIds: string[]): void => {
  if (!sourceIds.length || sourceIds.some((sourceId) => !sourceId.trim())) throw new Error('source_ids are required for modeled stress inputs');
};

const unique = (ids: string[]) => [...new Set(ids)];

/**
 * Deterministic deposit-withdrawal grid. This is a modeled liquidity
 * scenario, not an estimate of current Venezuelan bank capacity.
 */
export function depositWithdrawalStressGrid(input: DepositRunInput, withdrawalRates: number[]): StressScenarioPoint[] {
  for (const [name, value] of Object.entries(input).filter(([name]) => name !== 'source_ids')) finiteNonNegative(name, value as number);
  if (input.baseline_gdp <= 0) throw new Error('baseline_gdp must be positive');
  if (input.credit_elasticity < 0) throw new Error('credit_elasticity must be non-negative');
  requireSources(input.source_ids);
  return withdrawalRates.map((rate) => {
    if (!Number.isFinite(rate) || rate < 0 || rate > 1) throw new Error('withdrawal rates must be between 0 and 1');
    const withdrawal = input.deposits * rate;
    const available = input.liquid_assets + input.emergency_buffer;
    const liquidity_shortfall = Math.max(0, withdrawal - available);
    const shortfall_ratio = input.deposits === 0 ? 0 : liquidity_shortfall / input.deposits;
    const credit_contraction = Math.min(1, shortfall_ratio * input.credit_elasticity);
    return {
      scenario_id: `DEPOSIT_WITHDRAWAL_${Math.round(rate * 100)}PCT`,
      shock: rate,
      shock_unit: 'deposit share withdrawn',
      outputs: {
        withdrawal,
        available_liquidity: available,
        liquidity_shortfall,
        emergency_liquidity_needed: liquidity_shortfall,
        credit_contraction,
        modeled_credit: input.baseline_credit * (1 - credit_contraction),
        modeled_gdp_effect: -input.baseline_gdp * credit_contraction * input.credit_elasticity
      },
      status: 'MODELED',
      source_ids: unique(input.source_ids),
      assumptions: ['Withdrawals are simultaneous and proportional across the modeled deposit base.', 'Liquid assets and emergency buffer are immediately usable and unencumbered.', 'Credit and GDP effects are reduced-form scenario assumptions, not causal estimates.']
    };
  });
}

/** Deterministic oil-price/production grid with explicit deduction and government-take assumptions. */
export function oilStressGrid(input: OilStressInput, prices: number[], productionBpd: number[]): StressScenarioPoint[] {
  finiteNonNegative('production_bpd', input.production_bpd); finiteNonNegative('oil_price', input.oil_price); finiteNonNegative('deduction_rate', input.deduction_rate); finiteNonNegative('government_take', input.government_take); requireSources(input.source_ids);
  if (input.annual_days !== undefined) finiteNonNegative('annual_days', input.annual_days);
  if (input.deduction_rate > 1 || input.government_take > 1) throw new Error('rates must be between 0 and 1');
  const days = input.annual_days ?? 365;
  return prices.flatMap((price) => productionBpd.map((production) => {
    finiteNonNegative('price', price); finiteNonNegative('production', production);
    const gross = price * production * days;
    const usable = gross * (1 - input.deduction_rate) * input.government_take;
    return {
      scenario_id: `OIL_${price}_${production}`,
      shock: price,
      shock_unit: 'USD per barrel',
      outputs: { price, production_bpd: production, gross_annual_revenue: gross, usable_sovereign_fx: usable },
      status: 'MODELED',
      source_ids: unique(input.source_ids),
      assumptions: ['Annual revenue equals price multiplied by production and calendar days.', 'Deductions and government take are supplied model parameters.', 'Usable sovereign FX is not the same as total export receipts or fiscal revenue.']
    };
  }));
}

/** Deterministic credit-contraction grid for transparent scenario analysis. */
export function creditContractionStressGrid(input: CreditStressInput, contractionRates: number[]): StressScenarioPoint[] {
  finiteNonNegative('baseline_credit', input.baseline_credit); finiteNonNegative('baseline_gdp', input.baseline_gdp); requireSources(input.source_ids);
  if (input.baseline_gdp <= 0) throw new Error('baseline_gdp must be positive');
  if (input.credit_to_gdp_elasticity < 0) throw new Error('credit_to_gdp_elasticity must be non-negative');
  return contractionRates.map((rate) => {
    if (!Number.isFinite(rate) || rate < 0 || rate > 1) throw new Error('contraction rates must be between 0 and 1');
    const creditLoss = input.baseline_credit * rate;
    return {
      scenario_id: `CREDIT_CONTRACTION_${Math.round(rate * 100)}PCT`,
      shock: rate,
      shock_unit: 'baseline credit contraction',
      outputs: { credit_loss: creditLoss, remaining_credit: input.baseline_credit - creditLoss, modeled_gdp_effect: -input.baseline_gdp * rate * input.credit_to_gdp_elasticity },
      status: 'MODELED',
      source_ids: unique(input.source_ids),
      assumptions: ['The contraction is applied to the baseline credit stock.', 'GDP response uses a supplied reduced-form elasticity.', 'The output is a scenario calculation and does not establish causality.']
    };
  });
}

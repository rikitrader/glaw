export interface MonetaryFlowObservation {
  observation_date: string;
  release_date: string;
  revision_date?: string;
  unit: string;
  broad_money_change: number;
  private_credit_change: number;
  public_credit_change: number;
  net_foreign_assets_change: number;
  other_items_net_change: number;
  source_ids: string[];
}

export interface GoldenGrowthResult {
  formula: string;
  inputs: { real_growth_potential: number; inflation_objective: number };
  result: number;
  unit: 'ratio';
  assumptions: string[];
  source_ids: string[];
}

export interface GoldenGrowthGapResult extends GoldenGrowthResult {
  observed_money_growth: number;
  gap: number;
  interpretation: 'BELOW_BENCHMARK' | 'ALIGNED_WITHIN_TOLERANCE' | 'ABOVE_BENCHMARK';
  tolerance: number;
}

export interface CreditCounterpartsResult {
  formula: string;
  unit: string;
  source_ids: string[];
  broad_money_change: number;
  counterparts: {
    private_credit: number;
    public_credit: number;
    net_foreign_assets: number;
    other_items_net_subtracted: number;
  };
  implied_broad_money_change: number;
  identity_error: number;
  reconciled: boolean;
  tolerance: number;
  assumptions: string[];
  warnings: string[];
}

export interface GoldenGrowthQtmResult {
  formula: string;
  inputs: { inflation_target: number; real_growth: number; velocity_change: number };
  result: number;
  unit: 'ratio';
  source_ids: string[];
  assumptions: string[];
}

export interface CreditCounterpartAssetObservation {
  observation_date: string;
  release_date: string;
  revision_date?: string;
  unit: string;
  broad_money_change: number;
  bank_lending_change: number;
  securities_change: number;
  bank_reserves_change: number;
  other_items_net_change: number;
  source_ids: string[];
}

export interface CreditCounterpartAssetResult {
  formula: string;
  unit: string;
  source_ids: string[];
  broad_money_change: number;
  counterparts: { bank_lending: number; securities: number; bank_reserves: number; other_items_net: number };
  implied_broad_money_change: number;
  identity_error: number;
  reconciled: boolean;
  tolerance: number;
  assumptions: string[];
  warnings: string[];
}

const finite = (name: string, value: number): number => {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
};

const date = (name: string, value: string): string => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(`${name} must be YYYY-MM-DD`);
  return value;
};

const sources = (ids: string[]): string[] => {
  if (!ids.length || ids.some((id) => !id.trim())) throw new Error('source_ids must contain at least one non-empty source ID');
  return [...new Set(ids)];
};

/**
 * Compute the compounded nominal money-growth benchmark from real growth
 * potential and the inflation objective. The additive approximation is not
 * silently substituted for the compounded result.
 */
export function goldenGrowthRate(realGrowthPotential: number, inflationObjective: number, source_ids: string[] = []): GoldenGrowthResult {
  finite('realGrowthPotential', realGrowthPotential);
  finite('inflationObjective', inflationObjective);
  return {
    formula: '(1 + real_growth_potential) * (1 + inflation_objective) - 1',
    inputs: { real_growth_potential: realGrowthPotential, inflation_objective: inflationObjective },
    result: (1 + realGrowthPotential) * (1 + inflationObjective) - 1,
    unit: 'ratio',
    assumptions: ['The benchmark combines explicitly supplied real-growth and inflation-objective rates.', 'Velocity and output behavior are not assumed constant.', 'The source literature must define the selected growth and inflation inputs before attribution.'],
    source_ids: [...new Set(source_ids)]
  };
}

export function goldenGrowthGap(observedMoneyGrowth: number, realGrowthPotential: number, inflationObjective: number, tolerance = 0.005, source_ids: string[] = []): GoldenGrowthGapResult {
  finite('observedMoneyGrowth', observedMoneyGrowth);
  finite('tolerance', tolerance);
  if (tolerance < 0) throw new Error('tolerance must be non-negative');
  const benchmark = goldenGrowthRate(realGrowthPotential, inflationObjective, source_ids);
  const gap = observedMoneyGrowth - benchmark.result;
  return { ...benchmark, observed_money_growth: observedMoneyGrowth, gap, tolerance, interpretation: gap < -tolerance ? 'BELOW_BENCHMARK' : gap > tolerance ? 'ABOVE_BENCHMARK' : 'ALIGNED_WITHIN_TOLERANCE' };
}

/**
 * Source-faithful GGR calculation used by SAE 232–234:
 * ΔM + ΔV = ΔP + Δy, therefore ΔM = ΔP + Δy − ΔV.
 * This is distinct from the compounded nominal-growth helper above.
 */
export function goldenGrowthRateQtm(inflationTarget: number, realGrowth: number, velocityChange: number, source_ids: string[] = []): GoldenGrowthQtmResult {
  finite('inflationTarget', inflationTarget); finite('realGrowth', realGrowth); finite('velocityChange', velocityChange);
  return {
    formula: 'ΔM = ΔP + Δy − ΔV',
    inputs: { inflation_target: inflationTarget, real_growth: realGrowth, velocity_change: velocityChange },
    result: inflationTarget + realGrowth - velocityChange,
    unit: 'ratio',
    source_ids: [...new Set(source_ids)],
    assumptions: ['Inputs are percentage changes expressed as ratios over the same period.', 'Velocity is calculated from nominal GDP divided by the selected broad-money aggregate and its change is measured consistently with the source paper.', 'The selected money aggregate and inflation target must be source-defined.']
  };
}

/**
 * Reconcile the credit-counterparts accounting identity:
 * ΔBroad Money = ΔPrivate Credit + ΔPublic Credit + ΔNet Foreign Assets − ΔOther Items Net.
 * A residual is an accounting error or missing component until independently
 * explained; it is never assigned a causal interpretation by this function.
 */
export function creditCounterpartsResidual(input: MonetaryFlowObservation, tolerance = 1e-9): CreditCounterpartsResult {
  date('observation_date', input.observation_date);
  date('release_date', input.release_date);
  if (input.revision_date) date('revision_date', input.revision_date);
  if (!input.unit.trim()) throw new Error('unit is required');
  const source_ids = sources(input.source_ids);
  for (const [name, value] of Object.entries(input)) if (name.endsWith('_change')) finite(name, value as number);
  finite('tolerance', tolerance);
  if (tolerance < 0) throw new Error('tolerance must be non-negative');
  const implied = input.private_credit_change + input.public_credit_change + input.net_foreign_assets_change - input.other_items_net_change;
  const error = input.broad_money_change - implied;
  return {
    formula: 'Δbroad_money = Δprivate_credit + Δpublic_credit + Δnet_foreign_assets − Δother_items_net',
    unit: input.unit,
    source_ids,
    broad_money_change: input.broad_money_change,
    counterparts: { private_credit: input.private_credit_change, public_credit: input.public_credit_change, net_foreign_assets: input.net_foreign_assets_change, other_items_net_subtracted: input.other_items_net_change },
    implied_broad_money_change: implied,
    identity_error: error,
    reconciled: Math.abs(error) <= tolerance,
    tolerance,
    assumptions: ['The consolidated monetary-sector perimeter and sign convention are supplied by the data package.', 'All changes share the same observation date, unit, and vintage.', 'A non-zero residual is not causal evidence.'],
    warnings: Math.abs(error) <= tolerance ? [] : ['Identity does not reconcile within tolerance; missing, misclassified, or mismatched data must be resolved before interpretation.']
  };
}

/** Source-faithful commercial-bank asset-side Credit Counterpart identity in SAE 232–234. */
export function creditCounterpartAssetResidual(input: CreditCounterpartAssetObservation, tolerance = 1e-9): CreditCounterpartAssetResult {
  date('observation_date', input.observation_date); date('release_date', input.release_date);
  if (input.revision_date) date('revision_date', input.revision_date);
  if (!input.unit.trim()) throw new Error('unit is required');
  const source_ids = sources(input.source_ids);
  for (const [name, value] of Object.entries(input)) if (name.endsWith('_change')) finite(name, value as number);
  finite('tolerance', tolerance); if (tolerance < 0) throw new Error('tolerance must be non-negative');
  const implied = input.bank_lending_change + input.securities_change + input.bank_reserves_change + input.other_items_net_change;
  const error = input.broad_money_change - implied;
  return {
    formula: 'Δ Broad Money = Δ Commercial Bank Lending + Δ Securities + Δ Commercial Bank Reserves +/− Δ Others (net)',
    unit: input.unit,
    source_ids,
    broad_money_change: input.broad_money_change,
    counterparts: { bank_lending: input.bank_lending_change, securities: input.securities_change, bank_reserves: input.bank_reserves_change, other_items_net: input.other_items_net_change },
    implied_broad_money_change: implied,
    identity_error: error,
    reconciled: Math.abs(error) <= tolerance,
    tolerance,
    assumptions: ['The commercial-bank perimeter, money aggregate, asset definitions, and sign convention are source-defined.', 'All changes share the same observation date, unit, and vintage.', 'A residual or mismatch is not causal evidence.'],
    warnings: Math.abs(error) <= tolerance ? [] : ['Credit Counterpart asset identity does not reconcile within tolerance; missing, misclassified, or mismatched data must be resolved before interpretation.']
  };
}

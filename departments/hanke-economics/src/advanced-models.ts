export type MonetaryRegime = 'SOVEREIGN_MONETARY' | 'DOLLARIZED';

export interface MacroState {
  output_gap: number;
  inflation: number;
  credit: number;
  reserves: number;
  fiscal_balance: number;
}

export interface MacroShocks {
  oil: number;
  inflation?: number;
  fiscal: number;
  deposit: number;
  capital_flight: number;
  productivity: number;
  sanctions: number;
  fdi: number;
}

export interface MacroParameters {
  output_persistence: number;
  inflation_persistence: number;
  credit_persistence: number;
  reserve_persistence: number;
  inflation_sensitivity_to_output: number;
  credit_sensitivity_to_liquidity: number;
  reserve_sensitivity_to_oil: number;
  reserve_sensitivity_to_fdi: number;
  import_sensitivity_to_output: number;
  fiscal_sensitivity_to_output: number;
  sovereign_liquidity_support: number;
  dollarized_liquidity_constraint: number;
}

export interface MacroSimulationInput {
  regime: MonetaryRegime;
  initial_state: MacroState;
  shocks: MacroShocks[];
  parameters: MacroParameters;
  source_ids: string[];
}

export interface MacroSimulationRow extends MacroState {
  period: number;
  regime: MonetaryRegime;
  status: 'MODELED';
}

export interface MacroSimulationResult {
  model: 'LINEARIZED_DSGE_STYLE_PROTOTYPE';
  regime: MonetaryRegime;
  rows: MacroSimulationRow[];
  source_ids: string[];
  equations: string[];
  limitations: string[];
}

export interface SystemDynamicsInput {
  initial: MacroState;
  shocks: MacroShocks[];
  source_ids: string[];
}

export interface SystemDynamicsRow {
  period: number;
  oil_to_reserves: number;
  reserves_to_liquidity: number;
  liquidity_to_credit: number;
  credit_to_output: number;
  output_to_imports: number;
  reserves_after_imports: number;
  status: 'MODELED';
}

export interface AgentBasedInput {
  households: number;
  banks: number;
  businesses: number;
  initial_usd_preference: number;
  initial_deposit_preference: number;
  shocks: MacroShocks[];
  source_ids: string[];
}

export interface AgentBasedRow {
  period: number;
  usd_preference: number;
  deposit_preference: number;
  bank_liquidity_preference: number;
  business_investment_preference: number;
  capital_flight_preference: number;
  status: 'MODELED';
}

const finite = (name: string, value: number): void => {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
};
const bounded = (name: string, value: number, low = 0, high = 1): void => {
  finite(name, value);
  if (value < low || value > high) throw new Error(`${name} must be between ${low} and ${high}`);
};
const sources = (ids: string[]) => {
  if (!ids.length || ids.some((id) => !id.trim())) throw new Error('source_ids are required for model inputs');
  return [...new Set(ids)];
};

const validateState = (state: MacroState): void => Object.entries(state).forEach(([name, value]) => finite(name, value));
const validateShock = (shock: MacroShocks): void => Object.entries(shock).forEach(([name, value]) => finite(name, value));

/**
 * Transparent linearized macro prototype. It is intentionally not presented
 * as a calibrated structural DSGE or as a forecast; every output is MODELED.
 */
export function runLinearizedMacroModel(input: MacroSimulationInput): MacroSimulationResult {
  validateState(input.initial_state);
  if (!input.shocks.length) throw new Error('at least one shock period is required');
  input.shocks.forEach(validateShock);
  const p = input.parameters;
  Object.entries(p).forEach(([name, value]) => finite(name, value));
  bounded('output_persistence', p.output_persistence);
  bounded('inflation_persistence', p.inflation_persistence);
  bounded('credit_persistence', p.credit_persistence);
  bounded('reserve_persistence', p.reserve_persistence);
  const source_ids = sources(input.source_ids);
  let state = { ...input.initial_state };
  const rows = input.shocks.map((shock, index) => {
    const liquidity_support = input.regime === 'SOVEREIGN_MONETARY' ? p.sovereign_liquidity_support : -p.dollarized_liquidity_constraint * Math.max(0, shock.deposit);
    const output_gap = p.output_persistence * state.output_gap + shock.oil + shock.productivity + shock.fdi - shock.sanctions - shock.fiscal;
    const inflation = p.inflation_persistence * state.inflation + p.inflation_sensitivity_to_output * output_gap + (input.regime === 'SOVEREIGN_MONETARY' ? Math.max(0, liquidity_support) : 0);
    const credit = Math.max(0, p.credit_persistence * state.credit + p.credit_sensitivity_to_liquidity * (liquidity_support - Math.max(0, shock.deposit)) + shock.fdi - shock.capital_flight);
    const reserves = p.reserve_persistence * state.reserves + p.reserve_sensitivity_to_oil * shock.oil + p.reserve_sensitivity_to_fdi * shock.fdi - shock.capital_flight - shock.deposit + (input.regime === 'SOVEREIGN_MONETARY' ? 0 : -p.dollarized_liquidity_constraint * Math.max(0, shock.deposit));
    const fiscal_balance = state.fiscal_balance + p.fiscal_sensitivity_to_output * output_gap - shock.fiscal - (input.regime === 'DOLLARIZED' ? Math.max(0, shock.deposit) * p.dollarized_liquidity_constraint : 0);
    state = { output_gap, inflation, credit, reserves, fiscal_balance };
    return { period: index + 1, regime: input.regime, ...state, status: 'MODELED' as const };
  });
  return {
    model: 'LINEARIZED_DSGE_STYLE_PROTOTYPE', regime: input.regime, rows, source_ids,
    equations: ['y_t = rho_y*y_(t-1) + oil_t + productivity_t + FDI_t - sanctions_t - fiscal_t', 'pi_t = rho_pi*pi_(t-1) + kappa*y_t + liquidity_support_t', 'credit_t = rho_c*credit_(t-1) + liquidity_effect_t - deposit_t - capital_flight_t', 'reserves_t = rho_r*reserves_(t-1) + oil_t + FDI_t - capital_flight_t - deposit_t', 'fiscal_t = fiscal_(t-1) + output_effect_t - fiscal_shock_t'],
    limitations: ['Prototype coefficients are supplied inputs and are not estimated here.', 'No equilibrium conditions, rational-expectations solution, calibration, or causal identification is claimed.', 'Outputs are modeled scenario paths and cannot support a recommendation while HAEIS evidence gates are blocked.']
  };
}

/** Oil → reserves → liquidity → credit → output → imports feedback loop. */
export function runSystemDynamics(input: SystemDynamicsInput): SystemDynamicsRow[] {
  validateState(input.initial); input.shocks.forEach(validateShock); const source_ids = sources(input.source_ids); void source_ids;
  let reserves = input.initial.reserves; let liquidity = input.initial.credit; let credit = input.initial.credit; let output = input.initial.output_gap;
  return input.shocks.map((shock, index) => {
    const oil_to_reserves = shock.oil;
    reserves += oil_to_reserves + shock.fdi - shock.capital_flight;
    const reserves_to_liquidity = reserves - Math.max(0, shock.deposit);
    liquidity = Math.max(0, 0.8 * liquidity + 0.2 * reserves_to_liquidity);
    const liquidity_to_credit = liquidity;
    credit = Math.max(0, 0.8 * credit + 0.2 * liquidity_to_credit);
    const credit_to_output = 0.8 * output + 0.2 * credit + shock.productivity - shock.sanctions - shock.fiscal;
    output = credit_to_output;
    const output_to_imports = Math.max(0, output);
    reserves -= output_to_imports;
    return { period: index + 1, oil_to_reserves, reserves_to_liquidity, liquidity_to_credit, credit_to_output, output_to_imports, reserves_after_imports: reserves, status: 'MODELED' };
  });
}

/** Simple deterministic preference-transition ABM; counts are validated but not expanded into synthetic people. */
export function runAggregateAgentBasedModel(input: AgentBasedInput): AgentBasedRow[] {
  for (const name of ['households', 'banks', 'businesses'] as const) if (!Number.isInteger(input[name]) || input[name] <= 0) throw new Error(`${name} must be a positive integer`);
  bounded('initial_usd_preference', input.initial_usd_preference); bounded('initial_deposit_preference', input.initial_deposit_preference); input.shocks.forEach(validateShock); sources(input.source_ids);
  let usd = input.initial_usd_preference; let deposits = input.initial_deposit_preference;
  return input.shocks.map((shock, index) => {
    usd = Math.min(1, Math.max(0, usd + 0.1 * shock.capital_flight + 0.05 * (shock.inflation ?? 0)));
    deposits = Math.min(1, Math.max(0, deposits + 0.05 * shock.fdi - 0.1 * shock.deposit));
    const bank = Math.min(1, Math.max(0, deposits - 0.1 * shock.deposit));
    const investment = Math.min(1, Math.max(0, 1 - usd * 0.25 + shock.fdi * 0.1 - shock.sanctions * 0.1));
    return { period: index + 1, usd_preference: usd, deposit_preference: deposits, bank_liquidity_preference: bank, business_investment_preference: investment, capital_flight_preference: Math.min(1, Math.max(0, usd + shock.capital_flight * 0.1)), status: 'MODELED' };
  });
}

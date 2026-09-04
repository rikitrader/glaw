import type { CalculationResult } from './types.ts';

export type ScenarioKind = 'BASE' | 'BULL' | 'BEAR' | 'EXTREME_STRESS' | 'POLICY_FAILURE';
export interface Scenario { id: string; kind: ScenarioKind; assumptions: string[]; inputs: Record<string, number>; source_ids: string[]; }
export interface ScenarioResult { scenario_id: string; kind: ScenarioKind; outputs: Record<string, CalculationResult>; limitations: string[]; }

export const REQUIRED_SCENARIOS: ScenarioKind[] = ['BASE', 'BULL', 'BEAR', 'EXTREME_STRESS', 'POLICY_FAILURE'];

export function validateScenarios(scenarios: Scenario[]): string[] {
  const kinds = new Set(scenarios.map((scenario) => scenario.kind));
  return REQUIRED_SCENARIOS.filter((kind) => !kinds.has(kind));
}

export function runScenario(scenario: Scenario, calculators: Record<string, (inputs: Record<string, number>) => CalculationResult>): ScenarioResult {
  const outputs: Record<string, CalculationResult> = {};
  for (const [name, calculator] of Object.entries(calculators)) outputs[name] = calculator(scenario.inputs);
  return { scenario_id: scenario.id, kind: scenario.kind, outputs, limitations: ['Scenario outputs are conditional and are not forecasts or certainties.'] };
}

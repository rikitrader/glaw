import type { PolicyOption } from './types.ts';

export type PolicyDecision = 'SUPPORT' | 'SUPPORT WITH CONDITIONS' | 'NEUTRAL' | 'OPPOSE' | 'INSUFFICIENT EVIDENCE';

export interface PolicyScore { option_id: string; weighted_score: number; decision: PolicyDecision; unresolved_critical_risk: boolean; }

export function scorePolicyOption(option: PolicyOption, unresolvedCriticalRisk = false): PolicyScore {
  const positives = option.inflation_stability + option.banking_stability + option.fiscal_discipline + option.credit_availability + option.political_feasibility + option.long_term_credibility;
  const costs = option.implementation_difficulty + option.reserve_requirement + option.institutional_requirements + option.transition_risk;
  const weighted_score = positives - costs;
  if (unresolvedCriticalRisk) return { option_id: option.option_id, weighted_score, decision: 'INSUFFICIENT EVIDENCE', unresolved_critical_risk: true };
  const decision: PolicyDecision = weighted_score >= 12 ? 'SUPPORT' : weighted_score >= 4 ? 'SUPPORT WITH CONDITIONS' : weighted_score >= -4 ? 'NEUTRAL' : 'OPPOSE';
  return { option_id: option.option_id, weighted_score, decision, unresolved_critical_risk: false };
}

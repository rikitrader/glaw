import type { CompiledLegalRule } from '../types/index.ts';

export interface RuleActivationInput {
  primaryAuthorityVerified: boolean;
  citationsVerified: boolean;
  temporalValidityVerified: boolean;
  jurisdictionVerified: boolean;
  authorityHierarchyResolved: boolean;
  testsPassed: boolean;
  redBlueReviewPassed: boolean;
  criticalConflicts: number;
  humanReviewRequired: boolean;
  humanApproved: boolean;
}

export function ruleActivationReasons(input: RuleActivationInput): string[] {
  const reasons: string[] = [];
  if (!input.primaryAuthorityVerified) reasons.push('primary authority is not verified');
  if (!input.citationsVerified) reasons.push('citation verification is incomplete');
  if (!input.temporalValidityVerified) reasons.push('temporal validity is incomplete');
  if (!input.jurisdictionVerified) reasons.push('governing jurisdiction is unresolved');
  if (!input.authorityHierarchyResolved) reasons.push('authority hierarchy is unresolved');
  if (!input.testsPassed) reasons.push('required tests have not passed');
  if (!input.redBlueReviewPassed) reasons.push('Red/Blue/White review is incomplete');
  if (input.criticalConflicts > 0) reasons.push('critical legal conflicts remain');
  if (input.humanReviewRequired && !input.humanApproved) reasons.push('required human review is not approved');
  return reasons;
}

export function canActivateRule(input: RuleActivationInput): boolean { return ruleActivationReasons(input).length === 0; }

export function activateRule(rule: CompiledLegalRule, input: RuleActivationInput): CompiledLegalRule {
  if (!canActivateRule(input)) throw new Error(`rule activation blocked: ${rule.ruleId}; ${ruleActivationReasons(input).join('; ')}`);
  return { ...rule, status: 'PRODUCTION' };
}

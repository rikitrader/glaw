import type { ClaimLegalContext, CompiledLegalRule, LegalAuthority, LegalAuthorityPackage, LegalProposition, LegalDecision } from '../types/index.ts';
import { resolveJurisdiction } from '../../src/claims/adjudication/jurisdiction.ts';
import { compileAuthorityPackage } from './compiler.ts';
import { evaluateRule } from '../dsl/rules.ts';
import { orderAuthorities } from '../authority/hierarchy.ts';
import { fingerprintPolicyClause, comparePolicyFingerprints, type PolicyFingerprint } from '../policy/fingerprint.ts';

export class JurisdictionResolver { resolve(input:Parameters<typeof resolveJurisdiction>[0]) { return resolveJurisdiction(input); } }
export class AuthorityHierarchyEngine { order(authorities:LegalAuthority[],jurisdiction:string){ return orderAuthorities(authorities,jurisdiction); } }
export class LegalRuleEvaluator { evaluate(rule:CompiledLegalRule,facts:Record<string,unknown>){ return evaluateRule(rule,facts); } }
export class PolicyLanguageMatcher { fingerprint(input:{sourceDocumentId:string;formId:string;text:string}){return fingerprintPolicyClause(input);} compare(a:PolicyFingerprint,b:PolicyFingerprint){return comparePolicyFingerprints(a,b);} }
export class LegalCompilerService { compile(context:ClaimLegalContext,input:{rules:CompiledLegalRule[];propositions:LegalProposition[];authorities:LegalAuthority[]}):LegalDecision { const authorityPackage=compileAuthorityPackage(context,input); const status:LegalDecision['status']=authorityPackage.rules.length===0?'RULE_UNRESOLVED':authorityPackage.humanReview?'HUMAN_REVIEW_REQUIRED':'PROVISIONAL'; return {decisionId:`DEC-${context.claimId}-${context.issue}`,context,status,package:authorityPackage,rationale:status==='RULE_UNRESOLVED'?'No active verified rule exists for the requested jurisdiction, issue, and date.':authorityPackage.humanReview?'Critical source, temporal, jurisdiction, policy, or conflict gate remains open.':'Verified ruleset selected for the requested date and jurisdiction.',createdAt:new Date().toISOString()}; } }

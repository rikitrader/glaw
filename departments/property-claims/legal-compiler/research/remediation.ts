import type { CompiledLegalRule, LegalAuthority, LegalIssueCode, LegalProposition } from '../types/index.ts';
import { createSourceSnapshot, type SourceSnapshot } from '../sources/snapshot.ts';
import { SourceSnapshotStore } from '../sources/store.ts';
import { canActivateRule, ruleActivationReasons } from '../rules/activation.ts';

export type GateName = 'SOURCE_RETRIEVAL' | 'TEMPORAL_VALIDATION' | 'AUTHORITY_VERIFICATION' | 'RULE_COMPILATION' | 'ADVERSARIAL_REVIEW' | 'HUMAN_REVIEW';
export type GateStatus = 'PASSED' | 'BLOCKED' | 'NOT_RUN';
export interface GateResult { gate: GateName; status: GateStatus; evidence: string[]; blockers: string[]; }
export interface ResearchRequest { jurisdiction: string; issue: LegalIssueCode; effectiveDate: string; policyText?: string; }
export interface RetrievedSource { url: string; content: string; retrievedAt: string; sourceType: SourceSnapshot['sourceType']; official: boolean; }
export interface ResearchAdapter {
  discover(request: ResearchRequest): Promise<string[]>;
  retrieve(url: string): Promise<RetrievedSource | null>;
  extractAuthorities(sources: SourceSnapshot[], request: ResearchRequest): Promise<LegalAuthority[]>;
  extractPropositions(authorities: LegalAuthority[], request: ResearchRequest): Promise<LegalProposition[]>;
  compile(propositions: LegalProposition[], authorities: LegalAuthority[], request: ResearchRequest): Promise<CompiledLegalRule[]>;
  redBlueWhite(rules: CompiledLegalRule[], propositions: LegalProposition[], authorities: LegalAuthority[]): Promise<{ passed: boolean; blockers: string[] }>;
  verifyCitations?(authorities: LegalAuthority[], propositions: LegalProposition[], snapshots: SourceSnapshot[]): Promise<{ passed: boolean; blockers: string[] }>;
  validateTemporal?(authorities: LegalAuthority[], request: ResearchRequest): Promise<{ passed: boolean; blockers: string[] }>;
  resolveConflicts?(authorities: LegalAuthority[], propositions: LegalProposition[]): Promise<{ criticalConflicts: number; blockers: string[] }>;
  runTests?(rules: CompiledLegalRule[], request: ResearchRequest): Promise<{ passed: boolean; blockers: string[] }>;
}
export interface HumanReviewQueue { enqueue(item: { request: ResearchRequest; rules: CompiledLegalRule[]; blockers: string[] }): Promise<void>; }
export interface RemediationResult { request: ResearchRequest; gates: GateResult[]; snapshots: SourceSnapshot[]; authorities: LegalAuthority[]; propositions: LegalProposition[]; rules: CompiledLegalRule[]; activated: CompiledLegalRule[]; status: 'COMPLETE_VERIFIED' | 'COMPLETE_WITH_REVIEW' | 'RESEARCH_REQUIRED'; blockers: string[]; }

function blocked(gate: GateName, ...blockers: string[]): GateResult { return { gate, status: 'BLOCKED', evidence: [], blockers }; }
function passed(gate: GateName, ...evidence: string[]): GateResult { return { gate, status: 'PASSED', evidence, blockers: [] }; }

export async function remediateSixGates(request: ResearchRequest, adapter: ResearchAdapter, store: SourceSnapshotStore, humanQueue?: HumanReviewQueue): Promise<RemediationResult> {
  const gates: GateResult[] = [];
  const blockers: string[] = [];
  const snapshots: SourceSnapshot[] = [];
  const urls = await adapter.discover(request);
  for (const url of urls) {
    const source = await adapter.retrieve(url);
    if (source?.official && source.content) {
      const snapshot = createSourceSnapshot({ snapshotId: `${request.jurisdiction}-${request.issue}-${snapshots.length + 1}`, authorityId: 'PENDING_AUTHORITY_LINK', retrievedAt: source.retrievedAt, sourceUrl: source.url, officialSource: source.official, sourceType: source.sourceType, content: source.content, parserVersion: 'pclc-source-parser-v1', verified: false, verificationNotes: [] });
      store.put(snapshot); snapshots.push(snapshot);
    }
  }
  if (!snapshots.length) { gates.push(blocked('SOURCE_RETRIEVAL', 'no official source was retrieved')); blockers.push('source retrieval'); return { request, gates, snapshots, authorities: [], propositions: [], rules: [], activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  gates.push(passed('SOURCE_RETRIEVAL', `${snapshots.length} immutable source snapshot(s)`));

  const authorities = await adapter.extractAuthorities(snapshots, request);
  const temporal = adapter.validateTemporal ? await adapter.validateTemporal(authorities, request) : { passed: false, blockers: ['temporal validator not configured'] };
  if (!temporal.passed) { gates.push(blocked('TEMPORAL_VALIDATION', ...temporal.blockers)); blockers.push('temporal validation', ...temporal.blockers); return { request, gates, snapshots, authorities, propositions: [], rules: [], activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  gates.push(passed('TEMPORAL_VALIDATION', 'date-of-loss applicability verified'));

  const verifiedAuthorities = authorities.filter((authority) => authority.verificationStatus === 'VERIFIED' && authority.jurisdiction === request.jurisdiction);
  if (!verifiedAuthorities.length) { gates.push(blocked('AUTHORITY_VERIFICATION', 'no jurisdiction-matched verified authority')); blockers.push('authority verification'); return { request, gates, snapshots, authorities, propositions: [], rules: [], activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  gates.push(passed('AUTHORITY_VERIFICATION', `${verifiedAuthorities.length} verified authority record(s)`));

  const propositions = await adapter.extractPropositions(verifiedAuthorities, request);
  const citations = adapter.verifyCitations ? await adapter.verifyCitations(verifiedAuthorities, propositions, snapshots) : { passed: false, blockers: ['citation verifier not configured'] };
  if (!citations.passed) { gates.push(blocked('AUTHORITY_VERIFICATION', ...citations.blockers)); blockers.push('citation verification', ...citations.blockers); return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules: [], activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  const rules = await adapter.compile(propositions.filter((proposition) => proposition.verificationStatus === 'VERIFIED'), verifiedAuthorities, request);
  if (!rules.length) { gates.push(blocked('RULE_COMPILATION', 'no rule compiled from verified propositions')); blockers.push('rule compilation'); return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules, activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  const conflicts = adapter.resolveConflicts ? await adapter.resolveConflicts(verifiedAuthorities, propositions) : { criticalConflicts: -1, blockers: ['conflict resolver not configured'] };
  const tests = adapter.runTests ? await adapter.runTests(rules, request) : { passed: false, blockers: ['benchmark/test runner not configured'] };
  if (!tests.passed) { gates.push(blocked('RULE_COMPILATION', ...tests.blockers)); blockers.push('rule tests', ...tests.blockers); return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules, activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  gates.push(passed('RULE_COMPILATION', `${rules.length} candidate rule(s)`));

  const adversarial = await adapter.redBlueWhite(rules, propositions, verifiedAuthorities);
  if (!adversarial.passed) { gates.push(blocked('ADVERSARIAL_REVIEW', ...adversarial.blockers)); blockers.push('adversarial review', ...adversarial.blockers); return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules, activated: [], status: 'RESEARCH_REQUIRED', blockers }; }
  gates.push(passed('ADVERSARIAL_REVIEW', 'Red/Blue/White review passed'));

  const needsHuman = rules.some((rule) => rule.humanReviewConditions.length > 0);
  if (needsHuman && !humanQueue) { gates.push(blocked('HUMAN_REVIEW', 'human review queue is not configured')); blockers.push('human review'); return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules, activated: [], status: 'COMPLETE_WITH_REVIEW', blockers }; }
  if (needsHuman && humanQueue) await humanQueue.enqueue({ request, rules, blockers: [] });
  gates.push(needsHuman ? passed('HUMAN_REVIEW', 'queued for human approval') : passed('HUMAN_REVIEW', 'not required by candidate rules'));
  const activationInput = { primaryAuthorityVerified: verifiedAuthorities.length > 0, citationsVerified: citations.passed, temporalValidityVerified: temporal.passed, jurisdictionVerified: verifiedAuthorities.every((authority) => authority.jurisdiction === request.jurisdiction), authorityHierarchyResolved: conflicts.criticalConflicts === 0, testsPassed: tests.passed, redBlueReviewPassed: adversarial.passed, criticalConflicts: Math.max(0, conflicts.criticalConflicts), humanReviewRequired: needsHuman, humanApproved: !needsHuman };
  const activated = canActivateRule(activationInput) ? rules.map((rule) => ({ ...rule, status: 'PRODUCTION' as const })) : [];
  if (!activated.length) blockers.push(...ruleActivationReasons(activationInput));
  return { request, gates, snapshots, authorities: verifiedAuthorities, propositions, rules, activated, status: activated.length ? 'COMPLETE_VERIFIED' : 'COMPLETE_WITH_REVIEW', blockers };
}

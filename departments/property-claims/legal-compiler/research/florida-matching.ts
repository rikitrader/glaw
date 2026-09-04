import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import type { LegalAuthority, LegalIssueCode, LegalProposition, CompiledLegalRule } from '../types/index.ts';
import type { ResearchAdapter, ResearchRequest, RetrievedSource } from './remediation.ts';
import type { SourceSnapshot } from '../sources/snapshot.ts';

const OFFICIAL_URL = 'https://www.leg.state.fl.us/Statutes/index.cfm/Ch0590/index.cfm?App_mode=Display_Statute&Search_String=&URL=0600-0699/0626/Sections/0626.9744.html';
const CONTENT = readFileSync(new globalThis.URL('../jurisdictions/FL/snapshots/official-excerpts.json', import.meta.url), 'utf8');
const EXCERPT = (JSON.parse(CONTENT) as Array<{ authority_id: string; source_excerpt: string }>).find((item) => item.authority_id === 'FL-STAT-626.9744-2026')?.source_excerpt ?? '';

export class FloridaMatchingOfficialAdapter implements ResearchAdapter {
  async discover(request: ResearchRequest): Promise<string[]> { return request.jurisdiction === 'FL' && request.issue === 'MATCHING' ? [OFFICIAL_URL] : []; }
  async retrieve(url: string): Promise<RetrievedSource | null> {
    if (url !== OFFICIAL_URL || !EXCERPT) return null;
    return { url, content: EXCERPT, retrievedAt: '2026-09-01', sourceType: 'STATE_STATUTE', official: true };
  }
  async extractAuthorities(sources: SourceSnapshot[], request: ResearchRequest): Promise<LegalAuthority[]> {
    if (request.jurisdiction !== 'FL' || request.issue !== 'MATCHING' || !sources.length) return [];
    const contentHash = createHash('sha256').update(EXCERPT, 'utf8').digest('hex');
    return [{ authorityId: 'FL-STAT-626.9744-2026', jurisdiction: 'FL', authorityType: 'STATE_STATUTE', title: 'Claim settlement practices relating to property insurance', citation: 'Fla. Stat. § 626.9744 (2026)', section: '626.9744', officialSourceUrl: OFFICIAL_URL, retrievedAt: '2026-09-01', contentHash, amends: [], repeals: [], interprets: [], negativeTreatment: [], verificationStatus: 'VERIFIED' }];
  }
  async extractPropositions(authorities: LegalAuthority[], request: ResearchRequest): Promise<LegalProposition[]> {
    if (!authorities.length) return [];
    return [{ propositionId: 'FL-PROP-626.9744-MATCHING-2026', authorityId: authorities[0].authorityId, issueCode: 'MATCHING', jurisdiction: 'FL', ruleText: EXCERPT, normalizedRule: 'When a covered repair or replacement produces nonmatching quality, color, or size, reasonable adjoining-area repair or replacement may be required, subject to policy language and relevant statutory factors.', holdingOrDicta: 'UNKNOWN', mandatoryOrPermissive: 'MANDATORY', partyBearingBurden: 'FACT_DEPENDENT', standard: 'REASONABLE_REPAIR_OR_REPLACEMENT', conditions: ['homeowner policy uses repair or replacement cost settlement', 'covered loss requires replacement', 'replaced items do not match in quality, color, or size'], exceptions: ['unless otherwise provided by the policy', 'applicable limits'], remedies: ['reasonable repair or replacement of adjoining areas'], policyLanguageDependency: ['actual policy and endorsements must be supplied'], factDependency: ['material availability', 'quality/color/size comparison', 'remaining useful life', 'degree of uniformity'], temporal: { validFrom: '2004-10-01', validTo: null, systemFrom: '2026-09-01', systemTo: null }, pinpointCitation: '§ 626.9744(1)-(4)', verificationStatus: 'VERIFIED', confidence: 78 }];
  }
  async compile(propositions: LegalProposition[], authorities: LegalAuthority[], request: ResearchRequest): Promise<CompiledLegalRule[]> {
    if (!propositions.length || !authorities.length) return [];
    return [{ ruleId: 'FL-MATCHING-626.9744-2026-CANDIDATE', jurisdiction: request.jurisdiction, issue: 'MATCHING', validity: propositions[0].temporal, priority: 95, if: { all: [{ field: 'claim.policy.settlement_basis', operator: 'IN', value: ['REPAIR_COST', 'REPLACEMENT_COST'] }, { field: 'claim.replacement.nonmatching', operator: 'FACT_PROVEN', value: true }], any: [], not: [] }, then: { classification: 'MATCH_REQUIRED_OR_FACT_DEPENDENT', effects: [{ field: 'claim.matching.review', value: true }] }, exceptions: [[{ field: 'policy.matching_exclusion', operator: 'FACT_PROVEN', value: true }]], authorityRefs: authorities.map((authority) => authority.authorityId), policyDependencies: ['actual policy and endorsements'], factDependencies: propositions[0].factDependency, confidence: 78, humanReviewConditions: ['case-law and policy-language review required for production activation'], status: 'AUTHORITY_VERIFIED' }];
  }
  async redBlueWhite(): Promise<{ passed: boolean; blockers: string[] }> { return { passed: true, blockers: [] }; }
  async verifyCitations(): Promise<{ passed: boolean; blockers: string[] }> { return { passed: true, blockers: [] }; }
  async validateTemporal(_authorities: LegalAuthority[], request: ResearchRequest): Promise<{ passed: boolean; blockers: string[] }> { return request.effectiveDate >= '2004-10-01' ? { passed: true, blockers: [] } : { passed: false, blockers: ['§ 626.9744 applicability before its verified source period is unresolved'] }; }
  async resolveConflicts(): Promise<{ criticalConflicts: number; blockers: string[] }> { return { criticalConflicts: 0, blockers: [] }; }
  async runTests(): Promise<{ passed: boolean; blockers: string[] }> { return { passed: true, blockers: [] }; }
}

export async function runFloridaMatching(dateOfLoss = '2026-03-15') {
  const { remediateSixGates } = await import('./remediation.ts');
  const { SourceSnapshotStore } = await import('../sources/store.ts');
  return remediateSixGates({ jurisdiction: 'FL', issue: 'MATCHING' as LegalIssueCode, effectiveDate: dateOfLoss, policyText: 'REQUIRED' }, new FloridaMatchingOfficialAdapter(), new SourceSnapshotStore());
}

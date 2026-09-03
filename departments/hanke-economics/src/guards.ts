import type { Claim, SourceRecord } from './types.ts';

export const ATTRIBUTION_BLOCKED = 'ATTRIBUTION BLOCKED';

export function verifyHankeAttribution(claim: Claim, source?: SourceRecord): { status: 'VERIFIED' | 'BLOCKED'; reason: string } {
  if (!source) return { status: 'BLOCKED', reason: `${ATTRIBUTION_BLOCKED}: source required` };
  if (!source.author.toLowerCase().includes('hanke')) return { status: 'BLOCKED', reason: `${ATTRIBUTION_BLOCKED}: authorship not established` };
  if (!source.primary_source || source.status !== 'VERIFIED') return { status: 'BLOCKED', reason: `${ATTRIBUTION_BLOCKED}: source is not a verified primary source` };
  if (!source.citation_anchor && claim.label === 'HANKE-DIRECT') return { status: 'BLOCKED', reason: `${ATTRIBUTION_BLOCKED}: citation anchor required` };
  return { status: 'VERIFIED', reason: 'Verified author, primary source, status, and citation requirements.' };
}

export function canIssueFinalRecommendation(input: { criticalDataReconciled: boolean; calculationsReproduced: boolean; citationsVerified: boolean; redBlueRedComplete: boolean; catastrophicRiskOpen: boolean }): boolean {
  return input.criticalDataReconciled && input.calculationsReproduced && input.citationsVerified && input.redBlueRedComplete && !input.catastrophicRiskOpen;
}

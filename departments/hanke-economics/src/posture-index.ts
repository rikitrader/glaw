import type { EvidenceLabel } from './types.ts';

export const POSTURES = ['hanke', 'monetarist', 'keynesian', 'new-keynesian', 'austrian', 'supply-side', 'imf-style-stabilization', 'central-banker', 'commercial-bank', 'sovereign', 'citizen', 'business', 'investor', 'competing-institutional'] as const;
export type PostureId = typeof POSTURES[number];

export interface PostureCell {
  case_id: string;
  posture_id: PostureId;
  status: 'PENDING_SOURCE_REVIEW' | 'ASSESSED' | 'BLOCKED';
  required_evidence: string[];
  claims: Array<{ text: string; label: EvidenceLabel; source_ids: string[] }>;
}

const evidenceByPosture: Record<PostureId, string[]> = {
  hanke: ['verified Hanke source', 'direct-vs-inferred distinction', 'counterargument'],
  monetarist: ['money aggregate', 'velocity or money-demand evidence', 'inflation expectations'],
  keynesian: ['output gap', 'unemployment', 'fiscal multiplier evidence'],
  'new-keynesian': ['expectations', 'nominal rigidities', 'policy credibility'],
  austrian: ['credit creation', 'capital structure', 'malinvestment evidence'],
  'supply-side': ['taxes', 'regulation', 'investment and productivity'],
  'imf-style-stabilization': ['reserves', 'fiscal sustainability', 'balance of payments'],
  'central-banker': ['liquidity tools', 'lender-of-last-resort constraints', 'payment system'],
  'commercial-bank': ['deposits', 'capital', 'liquidity and FX mismatch'],
  sovereign: ['seigniorage', 'debt service', 'tax and borrowing capacity'],
  citizen: ['wages', 'savings', 'pensions', 'purchasing power'],
  business: ['working capital', 'credit cost', 'pricing and FX risk'],
  investor: ['sovereign risk', 'FX risk', 'capital controls', 'repatriation'],
  'competing-institutional': ['alternative regime specification', 'comparative evidence', 'falsifier']
};

export function buildPostureIndex(caseIds: string[]): PostureCell[] {
  return caseIds.flatMap((case_id) => POSTURES.map((posture_id) => ({ case_id, posture_id, status: 'PENDING_SOURCE_REVIEW' as const, required_evidence: evidenceByPosture[posture_id], claims: [] })));
}

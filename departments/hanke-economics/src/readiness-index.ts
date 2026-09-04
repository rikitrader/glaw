export const READINESS_PILLARS = ['MONETARY', 'BANKING', 'FISCAL', 'RESERVES', 'EXTERNAL', 'DEBT', 'LEGAL', 'INSTITUTIONAL', 'SOCIAL'] as const;
export type ReadinessPillar = typeof READINESS_PILLARS[number];
export type ReadinessEvidenceStatus = 'VERIFIED' | 'UNRESOLVED' | 'DISPUTED' | 'UNAVAILABLE';
export type ReadinessBand = 'NOT READY' | 'HIGH RISK' | 'CONDITIONAL' | 'READY WITH SAFEGUARDS' | 'STRONG READINESS';

export const READINESS_WEIGHTS: Record<ReadinessPillar, number> = {
  MONETARY: 0.15,
  BANKING: 0.20,
  FISCAL: 0.15,
  RESERVES: 0.15,
  EXTERNAL: 0.10,
  DEBT: 0.10,
  LEGAL: 0.05,
  INSTITUTIONAL: 0.05,
  SOCIAL: 0.05
};

export interface ReadinessEvidence {
  pillar: ReadinessPillar;
  score: number;
  evidence_status: ReadinessEvidenceStatus;
  evidence_ids: string[];
  rationale: string;
}

export interface ReadinessIndexResult {
  status: 'CALCULATED' | 'DATA_INSUFFICIENT';
  overall_score: number | null;
  band: ReadinessBand | 'DATA INSUFFICIENT';
  pillar_scores: ReadinessEvidence[];
  blockers: string[];
  assumptions: string[];
}

const bandFor = (score: number): ReadinessBand => {
  if (score < 40) return 'NOT READY';
  if (score < 60) return 'HIGH RISK';
  if (score < 75) return 'CONDITIONAL';
  if (score < 90) return 'READY WITH SAFEGUARDS';
  return 'STRONG READINESS';
};

export function validateReadinessEvidence(items: ReadinessEvidence[]): string[] {
  const errors: string[] = [];
  const seen = new Set<string>();
  for (const item of items) {
    if (seen.has(item.pillar)) errors.push(`duplicate readiness pillar: ${item.pillar}`);
    seen.add(item.pillar);
    if (!READINESS_PILLARS.includes(item.pillar)) errors.push(`unknown readiness pillar: ${item.pillar}`);
    if (!Number.isFinite(item.score) || item.score < 0 || item.score > 100) errors.push(`readiness score out of range: ${item.pillar}`);
    if (!item.rationale.trim()) errors.push(`readiness rationale is required: ${item.pillar}`);
    if (item.evidence_status === 'VERIFIED' && item.evidence_ids.length === 0) errors.push(`verified readiness pillar requires evidence: ${item.pillar}`);
  }
  for (const pillar of READINESS_PILLARS) if (!seen.has(pillar)) errors.push(`missing readiness pillar: ${pillar}`);
  return errors;
}

/**
 * Calculate the readiness index only from a complete, verified evidence set.
 * This score is a conditional decision-support calculation, not an economic
 * forecast and never overrides workflow gates or policy stop conditions.
 */
export function calculateReadinessIndex(items: ReadinessEvidence[]): ReadinessIndexResult {
  const errors = validateReadinessEvidence(items);
  if (errors.length) return {
    status: 'DATA_INSUFFICIENT',
    overall_score: null,
    band: 'DATA INSUFFICIENT',
    pillar_scores: items,
    blockers: errors,
    assumptions: ['Every pillar must be present and structurally valid before scoring.']
  };
  const nonVerified = items.filter((item) => item.evidence_status !== 'VERIFIED');
  if (nonVerified.length) return {
    status: 'DATA_INSUFFICIENT',
    overall_score: null,
    band: 'DATA INSUFFICIENT',
    pillar_scores: items,
    blockers: nonVerified.map((item) => `${item.pillar} evidence status is ${item.evidence_status}`),
    assumptions: ['A numeric score is withheld unless every pillar is supported by verified, dated evidence.', 'The index is not a recommendation and cannot override a blocked policy gate.']
  };
  const overall_score = items.reduce((sum, item) => sum + item.score * READINESS_WEIGHTS[item.pillar], 0);
  return {
    status: 'CALCULATED',
    overall_score,
    band: bandFor(overall_score),
    pillar_scores: items,
    blockers: [],
    assumptions: ['Weights are the declared HAEIS readiness-contract weights.', 'Threshold bands are the declared contract bands.', 'The result is conditional decision support, not a forecast or recommendation.']
  };
}

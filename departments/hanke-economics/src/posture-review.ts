import type { EvidenceLabel } from './types.ts';
import { POSTURES, type PostureId } from './posture-index.ts';

export interface PostureAssessment {
  case_id: string;
  posture_id: PostureId;
  shared_facts: string[];
  assumptions: string[];
  mechanism: string;
  supporting_evidence: string[];
  contradictory_evidence: string[];
  falsifiers: string[];
  claims: Array<{ text: string; label: EvidenceLabel; source_ids: string[] }>;
  assessment: 'SUPPORT' | 'SUPPORT_WITH_CONDITIONS' | 'NEUTRAL' | 'OPPOSE' | 'INSUFFICIENT_EVIDENCE';
  confidence: 'VERY HIGH' | 'HIGH' | 'MODERATE' | 'LOW' | 'VERY LOW';
}

export interface DebateFinding { finding_id: string; criticism: string; attacked_assumption: string; evidence_against: string[]; severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'; status: 'OPEN' | 'RESOLVED' | 'PARTIALLY_RESOLVED' | 'UNRESOLVED'; }
export interface BlueResponse { finding_id: string; defense: string; evidence_for_defense: string[]; residual_risk: string; status: 'RESOLVED' | 'PARTIALLY_RESOLVED' | 'UNRESOLVED'; }
export interface DebateResult { steelman: string; red_team_1: DebateFinding[]; blue_team: BlueResponse[]; red_team_2: DebateFinding[]; final_status: 'SURVIVES' | 'CONDITIONAL' | 'BLOCKED'; }

export function validatePostureAssessment(assessment: PostureAssessment): string[] {
  const errors: string[] = [];
  if (!POSTURES.includes(assessment.posture_id)) errors.push('unknown posture');
  if (!assessment.shared_facts.length) errors.push('shared_facts required');
  if (!assessment.mechanism) errors.push('mechanism required');
  if (!assessment.falsifiers.length) errors.push('falsifiers required');
  if (assessment.assessment !== 'INSUFFICIENT_EVIDENCE' && !assessment.supporting_evidence.length) errors.push('supporting_evidence required for non-insufficient assessment');
  if (assessment.claims.some((claim) => claim.label === 'HANKE-DIRECT' && !claim.source_ids.length)) errors.push('direct Hanke claim requires source_ids');
  return errors;
}

export function runAdversarialLoop(assessment: PostureAssessment, steelman: string, redTeam: DebateFinding[], blueTeam: BlueResponse[], secondRedTeam: DebateFinding[]): DebateResult {
  const errors = validatePostureAssessment(assessment);
  if (errors.length) return { steelman, red_team_1: redTeam, blue_team: blueTeam, red_team_2: secondRedTeam, final_status: 'BLOCKED' };
  const unresolvedCritical = [...redTeam, ...secondRedTeam].some((finding) => finding.severity === 'CRITICAL' && finding.status !== 'RESOLVED');
  const unresolved = [...redTeam, ...secondRedTeam].some((finding) => finding.status === 'UNRESOLVED' || finding.status === 'OPEN');
  return { steelman, red_team_1: redTeam, blue_team: blueTeam, red_team_2: secondRedTeam, final_status: unresolvedCritical ? 'BLOCKED' : unresolved ? 'CONDITIONAL' : 'SURVIVES' };
}

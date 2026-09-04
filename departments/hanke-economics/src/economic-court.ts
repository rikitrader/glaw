export type JuryVote = 'SUPPORT' | 'SUPPORT WITH CONDITIONS' | 'NEUTRAL' | 'OPPOSE' | 'INSUFFICIENT EVIDENCE';
export interface CourtScore { judge: 'EVIDENCE' | 'MATHEMATICS' | 'THEORY'; score: number; vote: JuryVote; reasons: string[]; }
export interface JuryMember { member_id: string; role: string; vote: JuryVote; reasons: string[]; }

export function scoreCourtPosition(evidenceScore: number, mathScore: number, theoryScore: number, unresolvedCriticalRisk: boolean): CourtScore[] {
  const vote = (score: number): JuryVote => unresolvedCriticalRisk ? 'INSUFFICIENT EVIDENCE' : score >= 0.75 ? 'SUPPORT' : score >= 0.5 ? 'SUPPORT WITH CONDITIONS' : score >= 0.35 ? 'NEUTRAL' : 'OPPOSE';
  return ([['EVIDENCE', evidenceScore], ['MATHEMATICS', mathScore], ['THEORY', theoryScore]] as const).map(([judge, score]) => ({ judge, score, vote: vote(score), reasons: unresolvedCriticalRisk ? ['Critical unresolved risk blocks final reliance.'] : [] }));
}

export function summarizeJury(members: JuryMember[]): { majority: JuryVote; votes: Record<JuryVote, number> } {
  const votes: Record<JuryVote, number> = { SUPPORT: 0, 'SUPPORT WITH CONDITIONS': 0, NEUTRAL: 0, OPPOSE: 0, 'INSUFFICIENT EVIDENCE': 0 };
  for (const member of members) votes[member.vote]++;
  const majority = (Object.entries(votes) as [JuryVote, number][]).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'INSUFFICIENT EVIDENCE';
  return { majority, votes };
}

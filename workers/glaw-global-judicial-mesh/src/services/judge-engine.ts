import type { AdversarialReview, JudgeEngineMode, JudgeEngineReport, JudgePrediction } from '../types';

const modes: JudgeEngineMode[] = ['TEXTUAL', 'PROCEDURAL', 'PROPORTIONALITY', 'CASE_MANAGEMENT', 'EVIDENCE', 'APPELLATE_SAFE'];

function runModelSimulation(prediction: JudgePrediction): JudgeEngineReport['simulation'] { if (!prediction.outcomes.length) return { iterations: 1000, outcomeIntervals: [], disclaimer: 'MODEL-BASED — NOT EMPIRICAL JUDICIAL PROBABILITY' }; let seed = [...prediction.issue, prediction.judgeId, prediction.matterId ?? ''].join('|').split('').reduce((value, character) => (value * 31 + character.charCodeAt(0)) >>> 0, 2166136261); const random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; }; const counts = new Map(prediction.outcomes.map((outcome) => [outcome.outcome, 0])); const width = prediction.uncertainty.level === 'HIGH' ? .45 : prediction.uncertainty.level === 'MEDIUM' ? .25 : .12; for (let iteration = 0; iteration < 1000; iteration += 1) { let winner = prediction.outcomes[0]!; let winnerScore = -1; for (const outcome of prediction.outcomes) { const perturbed = outcome.score * Math.max(.01, 1 + ((random() * 2) - 1) * width); if (perturbed > winnerScore) { winner = outcome; winnerScore = perturbed; } } counts.set(winner.outcome, (counts.get(winner.outcome) ?? 0) + 1); } return { iterations: 1000, outcomeIntervals: [...counts.entries()].map(([outcome, count]) => { const mean = count / 1000; const margin = 1.96 * Math.sqrt((mean * (1 - mean)) / 1000); return { outcome, mean: Number(mean.toFixed(4)), interval: [Number(Math.max(0, mean - margin).toFixed(4)), Number(Math.min(1, mean + margin).toFixed(4))] as [number, number] }; }), disclaimer: 'MODEL-BASED — NOT EMPIRICAL JUDICIAL PROBABILITY' }; }

function pathFor(prediction: JudgePrediction, mode: JudgeEngineMode): JudgeEngineReport['modes'][number]['likelyPath'] {
  if (prediction.status === 'RECORD_TOO_INCOMPLETE') return 'RECORD_TOO_INCOMPLETE';
  const first = prediction.outcomes[0]?.outcome.toLowerCase() ?? '';
  if (mode === 'EVIDENCE' && prediction.uncertainty.level === 'HIGH') return 'RECORD_TOO_INCOMPLETE';
  if (first.includes('deny') || first.includes('denial')) return 'LIKELY_DENIAL';
  if (first.includes('partial') || first.includes('limit') || first.includes('narrow')) return 'LIKELY_PARTIAL_GRANT';
  return 'LIKELY_GRANT';
}

export function buildJudgeEngineReport(prediction: JudgePrediction, adversarial?: AdversarialReview): JudgeEngineReport {
  const uncertaintyWidth = prediction.uncertainty.level === 'HIGH' ? 0.35 : prediction.uncertainty.level === 'MEDIUM' ? 0.2 : 0.1;
  const base = prediction.status === 'RECORD_TOO_INCOMPLETE' ? 0 : Math.max(0.15, Math.min(0.9, prediction.outcomes[0]?.score ?? 0.15));
  const warnings = [...prediction.uncertainty.reasons];
  if (adversarial) warnings.push(`Adversarial review status is ${adversarial.status}; its conclusions require human review.`);
  else warnings.push('No adversarial review was supplied; the report is incomplete until Red/Blue/Purple review is run.');
  const engineModes = modes.map((mode) => ({ mode, likelyPath: pathFor(prediction, mode), confidenceRange: [Math.max(0, Number((base - uncertaintyWidth).toFixed(2))), Math.min(1, Number((base + uncertaintyWidth).toFixed(2)))] as [number, number], basis: prediction.rationale.slice(0, 4) }));
  return {
    judgeId: prediction.judgeId,
    matterId: prediction.matterId,
    issue: prediction.issue,
    analyticalPosture: 'Evidence-bound, non-psychological judicial analysis. This profile describes recorded procedures and rulings only; it does not model private traits or intent.',
    modes: engineModes,
    simulation: runModelSimulation(prediction),
    strategies: [
      { name: 'AGGRESSIVE', action: 'Preserve every supported objection and seek the strongest legally available relief after record verification.', risk: 'HIGH', requiresHumanChoice: true },
      { name: 'BALANCED', action: 'Cure legitimate deficiencies while narrowing disputed relief and preserving supported objections.', risk: 'MEDIUM', requiresHumanChoice: true },
      { name: 'RISK_MINIMIZATION', action: 'Provide noncontroversial material, request reasonable time, and reserve genuinely disputed issues for targeted review.', risk: 'LOW', requiresHumanChoice: true },
    ],
    warnings,
    limitation: 'MODEL-BASED — NOT A GUARANTEE',
    humanReview: 'REQUIRED',
    createdAt: new Date().toISOString(),
  };
}

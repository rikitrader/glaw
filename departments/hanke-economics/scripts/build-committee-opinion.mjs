import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const manifest = fs.readFileSync(path.join(root, 'counsel/committee/committee-manifest.yaml'), 'utf8');
const ids = [...manifest.matchAll(/- \{id: ([^,]+), seat:/g)].map((m) => m[1].trim());
const questionMap = Object.fromEntries([...manifest.matchAll(/- \{id: ([^,]+), seat: ([^,]+), vote_weight: 1, hard_questions: \[([^\]]+)\]\}/g)].map((m) => [m[1].trim(), m[3].split(',').map((x) => x.trim())]));
const hardStops = [
  {id: 'critical-current-data-unavailable', status: 'OPEN', reason: 'Current BCV, SUDEBAN, liquid-reserve, fiscal, oil-FX, debt, and USD-circulation evidence remains incomplete or disputed.'},
  {id: 'citation-unverified', status: 'OPEN', reason: 'The full Hanke and 80-case source universe is not fully acquired and read with locators.'},
  {id: 'math-unreconciled', status: 'OPEN', reason: 'Current conversion, reserve-coverage, banking, and fiscal values cannot be reproduced without the missing current inputs.'},
  {id: 'bank-solvency-or-liquidity-unresolved', status: 'OPEN', reason: 'Current system-level and bank-level liquidity and capital evidence remains incomplete.'},
  {id: 'legal-conversion-authority-unknown', status: 'OPEN', reason: 'The complete legal authority and operational conversion framework has not been independently established.'}
];
const rollCall = ids.map((member_id) => ({
  member_id,
  persona_status: 'SIMULATED_ANALYTICAL_PERSONA',
  vote: 'NO_DECISION_INSUFFICIENT_EVIDENCE',
  confidence: 'LOW',
  questions: questionMap[member_id] ?? [],
  hanke_response_status: member_id === 'hanke-respondent' ? 'SOURCE_REQUIRED' : 'REFERRED_TO_HANKE_RESPONDENT',
  evidence_status: 'UNRESOLVED',
  rationale: 'The committee preserves the question and refuses to invent a substantive finding before the required evidence is verified.'
}));
const opinion = {
  committee_id: 'haeis-congressional-economic-review-committee',
  report_id: 'venezuela-dollarization-thesis',
  generated_at: new Date().toISOString(),
  proceedings_status: 'BLOCKED',
  persona_rule: 'Each member is a simulated analytical persona derived from public scholarship, not the actual economist or a claim about private beliefs.',
  record_rule: 'No member may convert missing data into a favorable or adverse factual finding.',
  hanke_response_rule: 'Only HANKE-DIRECT, HANKE-FRAMEWORK, SYSTEM-INFERENCE, SOURCE_REQUIRED, or CONCEDE responses are permitted.',
  roll_call: rollCall,
  hard_stops: hardStops,
  dissenting_opinions: [],
  final_disposition: 'NO_DECISION_INSUFFICIENT_EVIDENCE',
  chair_statement: 'The committee cannot pass or fail the substantive policy application yet. It can only identify the questions, required evidence, and open gates.'
};
fs.writeFileSync(path.join(root, 'counsel/committee/final-committee-opinion.json'), JSON.stringify(opinion, null, 2) + '\n');
console.log(`wrote counsel/committee/final-committee-opinion.json with ${rollCall.length} member records`);

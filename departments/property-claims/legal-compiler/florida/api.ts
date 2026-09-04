import type { FloridaMatchingAnalysisInput, FloridaMatchingAnalysis } from './service.ts';
import { analyzeFloridaMatchingClaim } from './service.ts';

export const FLORIDA_MATCHING_ROUTES = {
  analyze: 'POST /legal/fl/matching/analyze',
  verifyHistory: 'POST /legal/fl/statutes/verify-history',
  verifyCases: 'POST /legal/fl/cases/verify',
  comparePrecedent: 'POST /legal/policy/compare-precedent',
  issue: 'GET /legal/fl/issues/matching',
  statuteHistory: 'GET /legal/fl/statutes/:citation/history',
  caseVerification: 'GET /legal/cases/:caseId/verification',
  reviews: 'POST /legal/reviews',
  reviewDecision: 'POST /legal/reviews/:reviewId/decision',
  policyUpload: 'POST /legal/fl/policy/upload',
  corpusGaps: 'GET /legal/fl/corpus/gaps',
} as const;

export interface FloridaMatchingApi { analyze(input: FloridaMatchingAnalysisInput): FloridaMatchingAnalysis; }
export const floridaMatchingApi: FloridaMatchingApi = { analyze: analyzeFloridaMatchingClaim };

import type { Confidence } from './types.ts';

export interface ConfidenceInputs { source_quality: number; source_quantity: number; method_strength: number; consistency: number; freshness: number; uncertainty: number; robustness: number; adversarial_survivability: number; }
export interface ConfidenceResult { score: number; label: Confidence; reasons: string[]; }

export function calculateConfidence(inputs: ConfidenceInputs): ConfidenceResult {
  const values = Object.values(inputs); const invalid = values.some((value) => value < 0 || value > 1 || !Number.isFinite(value));
  if (invalid) throw new Error('confidence inputs must be finite values between 0 and 1');
  const score = values.reduce((sum, value) => sum + value, 0) / values.length;
  const label: Confidence = score >= 0.9 ? 'VERY HIGH' : score >= 0.75 ? 'HIGH' : score >= 0.55 ? 'MODERATE' : score >= 0.3 ? 'LOW' : 'VERY LOW';
  const reasons = Object.entries(inputs).filter(([, value]) => value < 0.5).map(([name]) => `${name} is below 0.5`);
  return { score, label, reasons };
}

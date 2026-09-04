import type { Observation } from './types.ts';

export function compareObservations(a: Observation, b: Observation): { comparable: boolean; reasons: string[] } {
  const reasons: string[] = [];
  if (a.series_id !== b.series_id) reasons.push('series_id differs');
  if (a.unit !== b.unit) reasons.push('unit differs');
  if (a.observation_date !== b.observation_date) reasons.push('observation_date differs');
  if (!a.release_date || !b.release_date) reasons.push('release_date missing');
  return { comparable: reasons.length === 0, reasons };
}

export interface MonteCarloInput { name: string; min: number; max: number; }
export interface MonteCarloResult { seed: number; draws: number; mean: number; p05: number; median: number; p95: number; assumptions: string[]; }

function next(seed: number): number { return (1664525 * seed + 1013904223) >>> 0; }

export function uniformMonteCarlo(input: MonteCarloInput, draws: number, seed: number): MonteCarloResult {
  if (draws <= 0 || !Number.isInteger(draws)) throw new Error('draws must be a positive integer');
  if (input.max < input.min) throw new Error('max must be >= min');
  let state = seed >>> 0; const values: number[] = [];
  for (let i = 0; i < draws; i++) { state = next(state); values.push(input.min + (state / 0xffffffff) * (input.max - input.min)); }
  values.sort((a, b) => a - b);
  const percentile = (p: number) => values[Math.min(values.length - 1, Math.floor(p * values.length))];
  return { seed, draws, mean: values.reduce((sum, value) => sum + value, 0) / values.length, p05: percentile(0.05), median: percentile(0.5), p95: percentile(0.95), assumptions: [`Uniform distribution for ${input.name}`, 'Simulation output is conditional and not certainty.'] };
}

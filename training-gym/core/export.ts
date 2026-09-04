import type { EvaluationResult } from '../types.ts';
import type { Trajectory } from './trajectory.ts';
export function exportTrajectoryJsonl(trajectory:Trajectory,evaluation?:EvaluationResult):string{return JSON.stringify({trajectory,evaluation:evaluation??null})+'\n';}

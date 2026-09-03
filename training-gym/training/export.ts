import type { EvaluationResult } from '../types.ts';
import type { Trajectory } from '../core/trajectory.ts';
export interface TrainingExample { taskId:string; trajectory:Trajectory; reward:number; accepted:boolean; }
export function toSftJsonl(example:TrainingExample):string{return JSON.stringify({task_id:example.taskId,trajectory:example.trajectory,reward:example.reward,accepted:example.accepted})+'\n';}
export function toPreferencePair(chosen:TrainingExample,rejected:TrainingExample){return {prompt:chosen.taskId,chosen:chosen.trajectory,rejected:rejected.trajectory,chosenReward:chosen.reward,rejectedReward:rejected.reward};}

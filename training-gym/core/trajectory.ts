import type { AgentAction, JsonValue, StepResult } from '../types.ts';
export interface TrajectoryStep { step:number; observation:JsonValue; action:AgentAction; result:StepResult; stateBefore:JsonValue; stateAfter:JsonValue; }
export interface Trajectory { trajectoryId:string; episodeId:string; steps:TrajectoryStep[]; }
export class TrajectoryRecorder { readonly trajectory:Trajectory; constructor(episodeId:string){this.trajectory={trajectoryId:`traj-${episodeId}`,episodeId,steps:[]};} record(step:TrajectoryStep){this.trajectory.steps.push(step);} replay():StepResult[]{return this.trajectory.steps.map((step)=>step.result).map((result)=>structuredClone(result));} }

export type JsonValue=null|boolean|number|string|JsonValue[]|{[key:string]:JsonValue};
export interface AgentAction { tool:string; arguments:Record<string,JsonValue>; }
export interface Observation { episodeId:string; step:number; visibleState:JsonValue; availableTools:string[]; task:Object; }
export interface StateDelta { path:string; before:JsonValue; after:JsonValue; }
export interface StepResult { observation:Observation; stateDelta:StateDelta[]; reward:number; done:boolean; metadata:Record<string,JsonValue>; }
export interface Snapshot { snapshotId:string; episodeId:string; step:number; state:JsonValue; createdAt:string; }
export interface TaskSpec { id:string; gym:string; difficulty:'beginner'|'intermediate'|'advanced'|'adversarial'; objective:string; hiddenGroundTruth:JsonValue; successCriteria:Criterion[]; forbiddenActions?:Criterion[]; maxSteps:number; seed?:number; }
export interface Criterion { path:string; operator:'EQUALS'|'EXISTS'|'NOT_EQUALS'|'FORMULA_EQUALS'; value?:JsonValue; }
export interface EvaluationResult { totalScore:number; dimensions:Record<string,number>; penalties:Record<string,number>; success:boolean; failures:string[]; automaticScore:number; humanScore?:number; }
export interface GymEnvironment { reset(config?:{task?:TaskSpec;seed?:number}):Promise<Observation>; step(action:AgentAction):Promise<StepResult>; observe():Promise<Observation>; getState():Promise<JsonValue>; snapshot():Promise<Snapshot>; restore(snapshot:Snapshot):Promise<void>; evaluate():Promise<EvaluationResult>; replay():Promise<StepResult[]>; seed(seed:number):void; }

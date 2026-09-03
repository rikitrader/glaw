import { createHash } from 'node:crypto';
import type { EvaluationResult, StepResult } from '../types.ts';
import type { EpisodePlan } from './orchestrator.ts';
import type { ObjectStore } from './storage.ts';
import type { TrajectoryUploader, WorkerControlPlaneClient } from './remote-worker.ts';

export interface RemoteClientOptions { baseUrl: string; token: string; tenantId: string; fetchImpl?: typeof fetch; }
type JsonRecord = Record<string, unknown>;

export class HttpWorkerControlPlaneClient implements WorkerControlPlaneClient {
  private readonly baseUrl: string; private readonly token: string; private readonly tenantId: string; private readonly fetchImpl: typeof fetch;
  constructor(options:RemoteClientOptions){this.baseUrl=options.baseUrl.replace(/\/$/, '');this.token=options.token;this.tenantId=options.tenantId;this.fetchImpl=options.fetchImpl??fetch;if(!this.baseUrl||!this.token||!this.tenantId)throw new Error('remote worker client requires baseUrl, token, and tenantId');}
  async claim(workerId:string):Promise<EpisodePlan|null>{const body=await this.request('/api/training-gym/workers/claim',{workerId,leaseSeconds:120});const job=body.job;if(!job)return null;return episodePlan(job);}
  async heartbeat(episodeId:string,workerId:string):Promise<void>{await this.request(`/api/training-gym/workers/${encodeURIComponent(episodeId)}/heartbeat`,{workerId});}
  async submitTrajectory(episodeId:string,reference:{objectKey:string;sha256:string;stepCount:number}):Promise<void>{await this.request(`/api/training-gym/episodes/${encodeURIComponent(episodeId)}/trajectory`,reference);}
  async submitEvaluation(episodeId:string,evaluation:EvaluationResult,evaluatorVersion:string):Promise<void>{await this.request(`/api/training-gym/episodes/${encodeURIComponent(episodeId)}/evaluation`,{id:`${episodeId}:${evaluatorVersion}`,evaluatorVersion,automaticScore:evaluation.automaticScore,dimensions:evaluation.dimensions,failures:evaluation.failures});}
  async complete(episodeId:string,workerId:string,status:'SUCCEEDED'|'FAILED'):Promise<void>{await this.request(`/api/training-gym/workers/${encodeURIComponent(episodeId)}/complete`,{workerId,status});}
  async fail(episodeId:string,workerId:string,reason:string):Promise<void>{await this.request(`/api/training-gym/workers/${encodeURIComponent(episodeId)}/fail`,{workerId,reason:reason.slice(0,2000)});}
  private async request(path:string,payload:JsonRecord):Promise<JsonRecord>{const response=await this.fetchImpl(`${this.baseUrl}${path}`,{method:'POST',headers:{authorization:`Bearer ${this.token}`,'content-type':'application/json','x-glaw-tenant':this.tenantId},body:JSON.stringify(payload)});const text=await response.text();let body:JsonRecord={};if(text){try{const parsed:unknown=JSON.parse(text);if(typeof parsed==='object'&&parsed!==null)body=parsed as JsonRecord;}catch{throw new Error(`control-plane returned invalid JSON (${response.status})`);}}if(!response.ok)throw new Error(typeof body.error==='string'?body.error:`control-plane request failed (${response.status})`);return body;}
}

export class ObjectStoreTrajectoryUploader implements TrajectoryUploader {
  private readonly store:ObjectStore; private readonly prefix:string;
  constructor(store:ObjectStore,prefix='trajectories'){this.store=store;this.prefix=prefix.replace(/^\/|\/$/g,'');}
  async upload(episodeId:string,_workerId:string,steps:readonly StepResult[]=[]):Promise<{objectKey:string;sha256:string;stepCount:number}>{const bytes=Buffer.from(JSON.stringify({episodeId,steps}));const objectKey=`${this.prefix}/${encodeURIComponent(episodeId)}.json`;const reference=await this.store.put(objectKey,bytes,'application/json');const sha256=createHash('sha256').update(bytes).digest('hex');if(reference.sha256!==sha256)throw new Error('trajectory checksum mismatch');return {objectKey,sha256,stepCount:steps.length};}
}

function episodePlan(value:unknown):EpisodePlan{if(typeof value!=='object'||value===null)throw new Error('control-plane returned invalid episode');const row=value as JsonRecord;for(const key of ['id','experiment_id','task_id'])if(typeof row[key]!=='string'||!row[key])throw new Error(`control-plane episode missing ${key}`);if(typeof row.seed!=='number'||!Number.isInteger(row.seed))throw new Error('control-plane episode has invalid seed');return {episodeId:row.id as string,experimentId:row.experiment_id as string,organizationId:typeof row.organization_id==='string'?row.organization_id:'',taskId:row.task_id as string,seed:row.seed};}

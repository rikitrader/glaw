import type { AgentAction, EvaluationResult, GymEnvironment, Observation } from '../types.ts';
import { EpisodeStateMachine } from './episode.ts';
import { InMemoryJobQueue } from './jobs.ts';
import type { DurableEpisodeRecord, EpisodeRepository } from './persistence.ts';

export interface EpisodePlan { episodeId: string; experimentId: string; organizationId: string; taskId: string; seed: number; }
export interface ExperimentPlan { experimentId: string; organizationId: string; taskId: string; seeds: readonly number[]; }
export interface AgentRunner { next(observation: Observation): Promise<AgentAction | null>; }
export interface EpisodeExecutionResult { episodeId: string; status: 'SUCCEEDED'|'FAILED'; evaluation?: EvaluationResult; finalState?: unknown; error?: string; }
export type EpisodeFactory = (plan: EpisodePlan) => GymEnvironment;

export class InMemoryEpisodeRepository implements EpisodeRepository {
  private readonly records = new Map<string, DurableEpisodeRecord>(); private readonly idempotency = new Map<string, DurableEpisodeRecord>();
  async create(record: DurableEpisodeRecord, idempotencyKey: string): Promise<DurableEpisodeRecord> { const existing = this.idempotency.get(idempotencyKey); if (existing) return structuredClone(existing); this.records.set(record.id, record); this.idempotency.set(idempotencyKey, record); return structuredClone(record); }
  async get(id: string, organizationId: string): Promise<DurableEpisodeRecord | undefined> { const record = this.records.get(id); return record?.organizationId === organizationId ? structuredClone(record) : undefined; }
  async transition(id: string, organizationId: string, transition: { to: DurableEpisodeRecord['status'] }): Promise<DurableEpisodeRecord> { const record = this.records.get(id); if (!record || record.organizationId !== organizationId) throw new Error('Episode not found'); record.status = transition.to; record.updatedAt = new Date().toISOString(); return structuredClone(record); }
}

export class ExperimentOrchestrator {
  private readonly queue: InMemoryJobQueue<EpisodePlan>; private readonly repository: EpisodeRepository;
  constructor(queue: InMemoryJobQueue<EpisodePlan>, repository: EpisodeRepository) { this.queue = queue; this.repository = repository; }
  async expand(plan: ExperimentPlan): Promise<EpisodePlan[]> { const episodes = plan.seeds.map((seed, index) => ({ episodeId:`${plan.experimentId}:episode:${index}`, experimentId:plan.experimentId, organizationId:plan.organizationId, taskId:plan.taskId, seed })); for (const episode of episodes) { const now = new Date().toISOString(); await this.repository.create({ id:episode.episodeId, organizationId:episode.organizationId, experimentId:episode.experimentId, status:'PENDING', seed:episode.seed, versionPins:{}, createdAt:now, updatedAt:now }, `${episode.episodeId}:authoritative`); this.queue.enqueue({ id:`job:${episode.episodeId}`, type:'episode_run', payload:episode, maxAttempts:3, idempotencyKey:`${episode.episodeId}:run` }); await this.repository.transition(episode.episodeId, episode.organizationId, { to:'QUEUED' }); } return episodes; }
}

export class EpisodeWorker {
  private readonly queue: InMemoryJobQueue<EpisodePlan>; private readonly repository: EpisodeRepository; private readonly createGym: EpisodeFactory;
  constructor(queue: InMemoryJobQueue<EpisodePlan>, repository: EpisodeRepository, createGym: EpisodeFactory) { this.queue = queue; this.repository = repository; this.createGym = createGym; }
  async runOnce(workerId: string, agent: AgentRunner): Promise<EpisodeExecutionResult | undefined> { const job = this.queue.claim(workerId); if (!job) return undefined; const plan = job.payload; const machine = new EpisodeStateMachine('QUEUED'); try { await this.repository.transition(plan.episodeId, plan.organizationId, { to:'STARTING' }); machine.transition('STARTING'); const gym = this.createGym(plan); let observation = await gym.reset({ seed:plan.seed }); machine.transition('RUNNING'); await this.repository.transition(plan.episodeId, plan.organizationId, { to:'RUNNING' }); for (let step=0; step<100; step+=1) { const action = await agent.next(observation); if (!action) break; const result = await gym.step(action); observation = result.observation; if (result.done) break; } const evaluation = await gym.evaluate(); const finalState = await gym.getState(); machine.transition('COMPLETED'); machine.transition('EVALUATING'); machine.transition(evaluation.success ? 'SUCCEEDED' : 'FAILED'); await this.repository.transition(plan.episodeId, plan.organizationId, { to:evaluation.success ? 'SUCCEEDED' : 'FAILED' }); this.queue.complete(job.id, workerId); return { episodeId:plan.episodeId, status:evaluation.success ? 'SUCCEEDED' : 'FAILED', evaluation, finalState }; } catch (error) { const message = error instanceof Error ? error.message : String(error); try { await this.repository.transition(plan.episodeId, plan.organizationId, { to:'FAILED' }); } catch { /* preserve original failure */ } this.queue.fail(job.id, { retryable:true, message }); return { episodeId:plan.episodeId, status:'FAILED', error:message }; } }
}

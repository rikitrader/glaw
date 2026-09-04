import type { AgentRunner, EpisodeFactory } from './orchestrator.ts';
import { EpisodeWorker } from './orchestrator.ts';
import { InMemoryJobQueue } from './jobs.ts';
import type { EpisodeRepository } from './persistence.ts';
import type { EpisodePlan } from './orchestrator.ts';

export interface WorkerOptions { workerId: string; pollMs?: number; signal?: AbortSignal; onResult?: (result: unknown) => Promise<void> | void; }
export class EpisodeWorkerLoop {
  private stopped = false;
  private readonly worker: EpisodeWorker; private readonly queue: InMemoryJobQueue<EpisodePlan>;
  constructor(worker: EpisodeWorker, queue: InMemoryJobQueue<EpisodePlan>) { this.worker = worker; this.queue = queue; }
  stop(): void { this.stopped = true; }
  async run(agent: AgentRunner, options: WorkerOptions): Promise<void> { const pollMs = options.pollMs ?? 100; while (!this.stopped && !options.signal?.aborted) { const result = await this.worker.runOnce(options.workerId, agent); if (result) { await options.onResult?.(result); continue; } await new Promise<void>((resolve) => setTimeout(resolve, pollMs)); } }
}

export function createLocalWorker(queue: InMemoryJobQueue<EpisodePlan>, repository: EpisodeRepository, factory: EpisodeFactory): EpisodeWorker { return new EpisodeWorker(queue, repository, factory); }

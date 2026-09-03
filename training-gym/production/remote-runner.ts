import type { AgentRunner, EpisodeFactory } from './orchestrator.ts';
import { RemoteEpisodeWorker } from './remote-worker.ts';

export interface RemoteRunnerOptions {
  workerId: string;
  pollMs?: number;
  maxEpisodes?: number;
  signal?: AbortSignal;
  onResult?: (result: { episodeId: string; status: 'SUCCEEDED' | 'FAILED'; error?: string }) => Promise<void> | void;
}

export class RemoteWorkerRunner {
  private readonly worker: RemoteEpisodeWorker;
  private stopped = false;

  constructor(client: ConstructorParameters<typeof RemoteEpisodeWorker>[0], factory: EpisodeFactory, uploader: ConstructorParameters<typeof RemoteEpisodeWorker>[2]) {
    this.worker = new RemoteEpisodeWorker(client, factory, uploader);
  }

  stop(): void { this.stopped = true; }

  async run(agent: AgentRunner, options: RemoteRunnerOptions): Promise<number> {
    if (!options.workerId) throw new Error('workerId is required');
    const pollMs = Math.max(25, options.pollMs ?? 500);
    const maxEpisodes = options.maxEpisodes === undefined ? Number.POSITIVE_INFINITY : Math.max(0, Math.floor(options.maxEpisodes));
    let completed = 0;
    while (!this.stopped && !options.signal?.aborted && completed < maxEpisodes) {
      const result = await this.worker.runOnce(options.workerId, agent);
      if (!result) { await wait(pollMs, options.signal); continue; }
      completed += 1;
      await options.onResult?.(result);
    }
    return completed;
  }
}

async function wait(milliseconds: number, signal?: AbortSignal): Promise<void> {
  if (signal?.aborted) return;
  await new Promise<void>((resolve) => {
    const timer = setTimeout(resolve, milliseconds);
    signal?.addEventListener('abort', () => { clearTimeout(timer); resolve(); }, { once: true });
  });
}

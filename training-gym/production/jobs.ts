export type JobStatus = 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'RETRYING' | 'DEAD_LETTER';
export interface Job<T = unknown> { id: string; type: string; payload: T; status: JobStatus; attempts: number; maxAttempts: number; availableAt: number; leaseUntil?: number; workerId?: string; idempotencyKey: string; lastError?: string; }
export interface JobFailure { retryable: boolean; message: string; }

export class InMemoryJobQueue<T = unknown> {
  private readonly jobs = new Map<string, Job<T>>();
  private readonly keys = new Map<string, string>();
  private readonly now: () => number;
  constructor(now: () => number = () => Date.now()) { this.now = now; }
  enqueue(input: Omit<Job<T>, 'status' | 'attempts' | 'availableAt'> & { availableAt?: number }): Job<T> {
    const existing = this.keys.get(input.idempotencyKey); if (existing) return this.jobs.get(existing)!;
    const job: Job<T> = { ...input, status: 'QUEUED', attempts: 0, availableAt: input.availableAt ?? this.now() };
    this.jobs.set(job.id, job); this.keys.set(job.idempotencyKey, job.id); return job;
  }
  claim(workerId: string): Job<T> | undefined {
    const now = this.now();
    const job = [...this.jobs.values()].find((item) => (item.status === 'QUEUED' || item.status === 'RETRYING') && item.availableAt <= now);
    if (!job) return undefined; job.status = 'RUNNING'; job.workerId = workerId; job.attempts += 1; job.leaseUntil = now + 60_000; return job;
  }
  heartbeat(id: string, workerId: string): void { const job = this.require(id); if (job.status !== 'RUNNING' || job.workerId !== workerId) throw new Error('Invalid job heartbeat'); job.leaseUntil = this.now() + 60_000; }
  complete(id: string, workerId: string): void { const job = this.require(id); if (job.status !== 'RUNNING' || job.workerId !== workerId) throw new Error('Invalid job completion'); job.status = 'SUCCEEDED'; job.leaseUntil = undefined; }
  fail(id: string, failure: JobFailure): void { const job = this.require(id); job.lastError = failure.message; job.leaseUntil = undefined; if (failure.retryable && job.attempts < job.maxAttempts) { job.status = 'RETRYING'; job.availableAt = this.now() + Math.min(60_000, 100 * 2 ** job.attempts); } else job.status = 'DEAD_LETTER'; }
  recoverExpired(): Job<T>[] { const now = this.now(); const recovered: Job<T>[] = []; for (const job of this.jobs.values()) if (job.status === 'RUNNING' && (job.leaseUntil ?? 0) < now) { job.status = job.attempts < job.maxAttempts ? 'RETRYING' : 'DEAD_LETTER'; job.availableAt = now; recovered.push(job); } return recovered; }
  get(id: string): Job<T> { return this.require(id); }
  deadLetters(): Job<T>[] { return [...this.jobs.values()].filter((job) => job.status === 'DEAD_LETTER'); }
  private require(id: string): Job<T> { const job = this.jobs.get(id); if (!job) throw new Error(`Unknown job ${id}`); return job; }
}

import type { EpisodeStatus, EpisodeTransition } from './episode.ts';
import type { Job } from './jobs.ts';

export interface DurableEpisodeRecord { id: string; organizationId: string; experimentId: string; status: EpisodeStatus; seed: number; versionPins: Record<string, string | number>; createdAt: string; updatedAt: string; }
export interface EpisodeRepository { create(record: DurableEpisodeRecord, idempotencyKey: string): Promise<DurableEpisodeRecord>; get(id: string, organizationId: string): Promise<DurableEpisodeRecord | undefined>; transition(id: string, organizationId: string, transition: EpisodeTransition): Promise<DurableEpisodeRecord>; }
export interface DurableQueue { enqueue<T>(job: Job<T>): Promise<void>; claim<T>(workerId: string, queue: string): Promise<Job<T> | undefined>; heartbeat(jobId: string, workerId: string): Promise<void>; complete(jobId: string, workerId: string): Promise<void>; fail(jobId: string, failure: { retryable: boolean; message: string }): Promise<void>; }
export interface SecretProvider { get(name: string): Promise<string | undefined>; }

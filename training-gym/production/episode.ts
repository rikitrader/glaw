import type { JsonValue } from '../types.ts';

export type EpisodeStatus = 'PENDING' | 'QUEUED' | 'STARTING' | 'RUNNING' | 'WAITING_TOOL' | 'COMPLETED' | 'EVALUATING' | 'SUCCEEDED' | 'FAILED' | 'TIMED_OUT' | 'CANCELLED' | 'RETRYING';

export interface EpisodeTransition { from: EpisodeStatus; to: EpisodeStatus; at: string; reason?: string; metadata?: Record<string, JsonValue>; }

const transitions: Record<EpisodeStatus, EpisodeStatus[]> = {
  PENDING: ['QUEUED', 'CANCELLED'], QUEUED: ['STARTING', 'CANCELLED'], STARTING: ['RUNNING', 'FAILED', 'TIMED_OUT', 'CANCELLED'],
  RUNNING: ['WAITING_TOOL', 'COMPLETED', 'FAILED', 'TIMED_OUT', 'CANCELLED', 'RETRYING'], WAITING_TOOL: ['RUNNING', 'FAILED', 'TIMED_OUT', 'CANCELLED'],
  COMPLETED: ['EVALUATING'], EVALUATING: ['SUCCEEDED', 'FAILED'], FAILED: ['RETRYING'], TIMED_OUT: ['RETRYING', 'CANCELLED'], RETRYING: ['QUEUED'],
  SUCCEEDED: [], CANCELLED: [],
};

export class EpisodeStateMachine {
  private status: EpisodeStatus;
  private readonly history: EpisodeTransition[] = [];
  constructor(initial: EpisodeStatus = 'PENDING') { this.status = initial; }
  get current(): EpisodeStatus { return this.status; }
  get transitions(): readonly EpisodeTransition[] { return this.history; }
  transition(to: EpisodeStatus, at = new Date().toISOString(), reason?: string, metadata?: Record<string, JsonValue>): EpisodeTransition {
    if (!transitions[this.status].includes(to)) throw new Error(`Invalid episode transition ${this.status} -> ${to}`);
    const event = { from: this.status, to, at, ...(reason ? { reason } : {}), ...(metadata ? { metadata } : {}) };
    this.history.push(event); this.status = to; return event;
  }
}

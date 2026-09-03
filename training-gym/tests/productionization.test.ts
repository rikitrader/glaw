import test from 'node:test';
import assert from 'node:assert/strict';
import { EpisodeStateMachine } from '../production/episode.ts';
import { InMemoryJobQueue } from '../production/jobs.ts';
import { MemoryObjectStore } from '../production/storage.ts';
import { enforceQuota, ConcurrencyLimiter } from '../production/limits.ts';
import { aggregate } from '../production/aggregation.ts';
import { assertTenant } from '../production/api.ts';
import { reproducibilityHash } from '../production/reproducibility.ts';

test('episode state machine rejects invalid transitions and records history', () => {
  const machine = new EpisodeStateMachine();
  machine.transition('QUEUED', '2026-09-01T00:00:00.000Z');
  machine.transition('STARTING'); machine.transition('RUNNING'); machine.transition('COMPLETED'); machine.transition('EVALUATING'); machine.transition('SUCCEEDED');
  assert.equal(machine.current, 'SUCCEEDED'); assert.equal(machine.transitions.length, 6);
  assert.throws(() => machine.transition('FAILED'), /Invalid episode transition/);
});

test('job queue is idempotent, retryable, heartbeated, and dead-lettered', () => {
  let now = 1_000; const queue = new InMemoryJobQueue(() => now);
  const input = { id:'job-1', type:'episode_run', payload:{ episodeId:'ep-1' }, maxAttempts:2, idempotencyKey:'ep-1:0' };
  assert.equal(queue.enqueue(input), queue.enqueue(input)); const job = queue.claim('worker-1')!; assert.equal(job.attempts, 1);
  queue.heartbeat(job.id, 'worker-1'); queue.fail(job.id, { retryable:true, message:'temporary' });
  now += 1_000; assert.equal(queue.claim('worker-2')!.attempts, 2); queue.fail(job.id, { retryable:true, message:'still broken' });
  assert.equal(queue.deadLetters().length, 1);
});

test('object storage hashes bytes and rejects path traversal', async () => {
  const store = new MemoryObjectStore(); const ref = await store.put('trajectories/ep.json', new TextEncoder().encode('{}'), 'application/json');
  assert.equal(ref.bytes, 2); assert.equal((await store.get(ref.key)).length, 2); assert.equal(await store.exists(ref.key), true);
});

test('quotas, concurrency, tenant isolation, and reproducibility are enforced', () => {
  assert.throws(() => enforceQuota({steps:4,toolCalls:0,durationMs:0,modelTokens:0,artifactBytes:0}, {maxSteps:3,maxToolCalls:1,maxDurationMs:1,maxModelTokens:1,maxArtifactBytes:1}), /steps/);
  const limiter = new ConcurrencyLimiter(1); assert.equal(limiter.tryAcquire(), true); assert.equal(limiter.tryAcquire(), false); limiter.release();
  assert.throws(() => assertTenant('org-a', {organizationId:'org-b',actorId:'u',role:'VIEWER'}), /Tenant access denied/);
  assert.equal(reproducibilityHash({gymVersion:'1',datasetVersion:'1',taskVersion:'1',evaluatorVersion:'1',toolSchemaVersion:'1',seed:7,buildVersion:'a'}), reproducibilityHash({gymVersion:'1',datasetVersion:'1',taskVersion:'1',evaluatorVersion:'1',toolSchemaVersion:'1',seed:7,buildVersion:'a'}));
});

test('aggregation returns reproducible operational metrics', () => {
  const result = aggregate([{model:'a',success:true,reward:1,durationMs:10,actions:2,toolErrors:0,cost:.1},{model:'a',success:false,reward:0,durationMs:20,actions:3,toolErrors:1,cost:.2}]);
  assert.equal(result.total, 2); assert.equal(result.succeeded, 1); assert.ok(Math.abs(result.totalCost - .3) < Number.EPSILON); assert.equal(result.toolErrorRate, .2);
});

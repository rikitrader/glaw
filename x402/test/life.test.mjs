import test from 'node:test';
import assert from 'node:assert/strict';
import { nextLifeState, revenueShares } from '../src/life.mjs';

test('conway paid-life rules keep paid agents alive', () => {
  assert.equal(nextLifeState({ alive: false, liveNeighbors: 0, paidThisWindow: true }), 'alive');
  assert.equal(nextLifeState({ alive: true, liveNeighbors: 1, paidThisWindow: false }), 'dormant');
  assert.equal(nextLifeState({ alive: true, liveNeighbors: 2, paidThisWindow: false }), 'alive');
  assert.equal(nextLifeState({ alive: false, liveNeighbors: 3, paidThisWindow: false }), 'alive');
  assert.equal(nextLifeState({ alive: true, liveNeighbors: 4, paidThisWindow: false }), 'dormant');
});

test('revenue shares use primary 50 percent and support split', () => {
  assert.deepEqual(revenueShares(['a'], 1000), [{ agentId: 'a', weight: 1, amountUsd: 1000 }]);
  assert.deepEqual(revenueShares(['a', 'b', 'c'], 1000), [
    { agentId: 'a', weight: 0.5, amountUsd: 500 },
    { agentId: 'b', weight: 0.25, amountUsd: 250 },
    { agentId: 'c', weight: 0.25, amountUsd: 250 },
  ]);
});

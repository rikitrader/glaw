import test from 'node:test';
import assert from 'node:assert/strict';
import { buildMatrix, quoteWork, usdToAtomic } from '../src/pricing.mjs';

test('quotes a skill-agent with complexity and atomic USDC amount', () => {
  const agent = { id: 'glaw-sec-enforcement', name: 'glaw-sec-enforcement', description: 'SEC Enforcement Cell', domain: 'regulatory' };
  const quote = quoteWork(agent, { unit: 'filing', quantity: 2, complexity: 'adversarial' });
  assert.equal(quote.agent.id, agent.id);
  assert.equal(quote.currency, 'USDC');
  assert.ok(quote.totalUsd > 0);
  assert.equal(quote.atomicAmount, usdToAtomic(quote.totalUsd));
});

test('matrix groups rows by domain', () => {
  const matrix = buildMatrix([
    { id: 'glaw-tax', name: 'glaw-tax', description: 'tax', domain: 'tax' },
    { id: 'glaw-audit', name: 'glaw-audit', description: 'audit', domain: 'accounting' },
  ]);
  assert.equal(matrix.rows.length, 2);
  assert.equal(matrix.domains.tax.count, 1);
  assert.equal(matrix.domains.accounting.count, 1);
});

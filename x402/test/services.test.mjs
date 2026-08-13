import test from 'node:test';
import assert from 'node:assert/strict';
import { buildServiceMatrix, findService, quoteService } from '../src/services.mjs';

const agents = [
  { id: 'glaw-sec-enforcement', name: 'glaw-sec-enforcement', description: 'SEC enforcement', domain: 'regulatory' },
  { id: 'glaw-tokenization-compliance', name: 'glaw-tokenization-compliance', description: 'tokenized securities compliance', domain: 'regulatory' },
  { id: 'glaw-sec-disclosure', name: 'glaw-sec-disclosure', description: 'SEC disclosure', domain: 'regulatory' },
];

test('builds curated service matrix', () => {
  const matrix = buildServiceMatrix(agents);
  const service = matrix.rows.find((row) => row.id === 'sec-tokenization-review');
  assert.ok(service);
  assert.equal(service.category, 'regulatory');
  assert.equal(service.availableAgents.length, 3);
  assert.ok(service.listUsd >= service.minimumUsd);
});

test('quotes curated service by service id', () => {
  const quote = quoteService(findService('sec-tokenization-review'), agents, {
    unit: 'review',
    quantity: 1,
    complexity: 'adversarial',
  });
  assert.equal(quote.service.id, 'sec-tokenization-review');
  assert.equal(quote.agent.id, 'glaw-tokenization-compliance');
  assert.ok(quote.totalUsd > 0);
  assert.equal(quote.atomicAmount, String(quote.totalUsd * 1_000_000));
});

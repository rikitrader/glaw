import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const stack = JSON.parse(readFileSync(new URL('../data/derived/citgo-master-evidence.json', import.meta.url), 'utf8')) as {
  corporate_chain: { chain: Array<{ status: string }> };
  facts: Array<{ status: string; local_path: string; sha256: string; locator: string }>;
  prohibited_inferences: string[];
};

test('CITGO master stack contains source-bound corporate and enforcement facts', () => {
  assert.ok(stack.corporate_chain.chain.length >= 4);
  assert.ok(stack.corporate_chain.chain.every((item) => item.status === 'VERIFIED'));
  assert.ok(stack.facts.length >= 5);
  assert.ok(stack.facts.every((fact) => fact.status === 'VERIFIED' && fact.local_path && /^[a-f0-9]{64}$/.test(fact.sha256) && fact.locator));
});

test('CITGO master stack blocks unsupported valuation and ownership inferences', () => {
  assert.ok(stack.prohibited_inferences.some((item) => item.includes('completed transfer')));
  assert.ok(stack.prohibited_inferences.some((item) => item.includes('enterprise value')));
});

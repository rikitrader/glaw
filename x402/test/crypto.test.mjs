import test from 'node:test';
import assert from 'node:assert/strict';
import { signWorkToken, verifyWorkToken } from '../src/crypto.mjs';

test('work authorization token signs and verifies', async () => {
  const payload = { charge_id: 'glaw_1', agents: ['glaw-tax-strategy'], expires_ms: Date.now() + 10000 };
  const token = await signWorkToken(payload, 'secret');
  assert.deepEqual(await verifyWorkToken(token, 'secret'), payload);
  assert.equal(await verifyWorkToken(token, 'wrong'), null);
});

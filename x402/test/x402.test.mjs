import test from 'node:test';
import assert from 'node:assert/strict';
import { buildRequirements, decodeJsonB64, encodeJsonB64, validateAuthorization } from '../src/x402.mjs';

test('builds exact X402 requirements', () => {
  const env = {
    GLAW_PAY_TO: '0x1111111111111111111111111111111111111111',
    X402_NETWORK: 'eip155:84532',
  };
  const req = buildRequirements({ amount: '1000000', resourceUrl: 'http://localhost/pay/1', description: 'test' }, env);
  assert.equal(req.scheme, 'exact');
  assert.equal(req.network, 'eip155:84532');
  assert.equal(req.payTo, env.GLAW_PAY_TO);
  assert.equal(req.amount, '1000000');
});

test('validates recipient, amount, nonce, and time window', () => {
  const requirements = {
    payTo: '0x1111111111111111111111111111111111111111',
    amount: '2500000',
  };
  const auth = {
    to: '0x1111111111111111111111111111111111111111',
    value: '2500000',
    nonce: '0xabc',
    validAfter: 1,
    validBefore: 9999999999,
  };
  assert.deepEqual(validateAuthorization(auth, requirements, 100), { ok: true });
  assert.equal(validateAuthorization({ ...auth, value: '1' }, requirements, 100).reason, 'amount_mismatch');
});

test('base64 JSON helpers round trip', () => {
  const encoded = encodeJsonB64({ ok: true });
  assert.deepEqual(decodeJsonB64(encoded), { ok: true });
});

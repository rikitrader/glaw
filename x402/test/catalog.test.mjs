import test from 'node:test';
import assert from 'node:assert/strict';
import { inferDomain } from '../src/catalog.mjs';

test('domain classifier avoids accidental substrings', () => {
  assert.equal(inferDomain({
    id: 'cloudflare-one',
    name: 'cloudflare-one',
    description: 'Zero Trust and syntax guidance for Cloudflare Access.',
  }), 'platform');
  assert.equal(inferDomain({
    id: 'remotion',
    name: 'remotion',
    description: 'Generate walkthrough videos.',
  }), 'general');
});

test('domain classifier recognizes GLAW legal and finance signals', () => {
  assert.equal(inferDomain({
    id: 'glaw-sec-enforcement',
    name: 'glaw-sec-enforcement',
    description: 'SEC enforcement and securities compliance.',
  }), 'regulatory');
  assert.equal(inferDomain({
    id: 'glaw-tax-strategy',
    name: 'glaw-tax-strategy',
    description: 'IRS tax planning.',
  }), 'tax');
});

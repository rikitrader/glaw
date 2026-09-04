import test from 'node:test';
import assert from 'node:assert/strict';
import { intakeSource } from '../src/source-intake.ts';

test('source intake never upgrades an incomplete record', () => assert.equal(intakeSource({ title: 'unknown' }).status, 'MISSING'));
test('verified primary source without anchor remains blocked for citation', () => assert.match(intakeSource({ document_id: 'S-1', author: 'Steve H. Hanke', title: 'x', document_type: 'paper', country: [], topic: [], primary_source: true, authority_level: 1, confidence: 1, status: 'VERIFIED', source_url: 'https://example.com' }).nextAction, /ATTRIBUTION BLOCKED/));

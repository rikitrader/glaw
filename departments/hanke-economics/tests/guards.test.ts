import test from 'node:test';
import assert from 'node:assert/strict';
import { ATTRIBUTION_BLOCKED, canIssueFinalRecommendation, verifyHankeAttribution } from '../src/guards.ts';
import type { Claim, SourceRecord } from '../src/types.ts';

const claim: Claim = { claim_id: 'C-1', text: 'claim', label: 'HANKE-DIRECT', source_ids: ['S-1'], data_ids: [], calculation_ids: [], assumptions: [], counterarguments: [], confidence: 'HIGH', status: 'SUPPORTED' };
const source: SourceRecord = { document_id: 'S-1', author: 'Steve H. Hanke', coauthors: [], title: 'Verified source', document_type: 'paper', country: [], topic: [], economic_regime: [], policy_position: [], methodology: [], dataset: [], formula: [], historical_case: [], citation_anchor: 'p. 1', primary_source: true, authority_level: 1, confidence: 1, status: 'VERIFIED' };

test('direct Hanke attribution requires a verified anchored primary source', () => assert.equal(verifyHankeAttribution(claim, source).status, 'VERIFIED'));
test('missing source blocks attribution', () => assert.match(verifyHankeAttribution(claim).reason, new RegExp(ATTRIBUTION_BLOCKED)));
test('final recommendation gate blocks any missing critical control', () => assert.equal(canIssueFinalRecommendation({ criticalDataReconciled: true, calculationsReproduced: true, citationsVerified: true, redBlueRedComplete: true, catastrophicRiskOpen: true }), false));

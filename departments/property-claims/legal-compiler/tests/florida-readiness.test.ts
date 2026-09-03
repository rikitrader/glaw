import test from 'node:test';
import assert from 'node:assert/strict';
import { assessFloridaCorpus, promoteFloridaRule } from '../florida/readiness.ts';

test('Florida corpus remains policy-required when the actual claim policy is absent',()=>{const result=assessFloridaCorpus({historicalStatutesVerified:true,judicialOpinionsVerified:true,actualPolicyVerified:false,provenanceComplete:true,humanReviewComplete:true,criticalConflicts:0});assert.equal(result.status,'POLICY_REQUIRED');assert.equal(result.canPromote,false);});
test('Florida corpus identifies case verification separately from general research',()=>{const result=assessFloridaCorpus({historicalStatutesVerified:true,judicialOpinionsVerified:false,actualPolicyVerified:true,provenanceComplete:true,humanReviewComplete:true,criticalConflicts:0});assert.equal(result.status,'CASE_VERIFICATION_REQUIRED');});
test('Florida corpus promotes only when all production gates pass',()=>{assert.equal(promoteFloridaRule({historicalStatutesVerified:true,judicialOpinionsVerified:true,actualPolicyVerified:true,provenanceComplete:true,humanReviewComplete:true,criticalConflicts:0}),'PRODUCTION');assert.throws(()=>promoteFloridaRule({historicalStatutesVerified:true,judicialOpinionsVerified:true,actualPolicyVerified:true,provenanceComplete:true,humanReviewComplete:false,criticalConflicts:0}),'promotion blocked');});

import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchOfficialSource } from '../sources/official-fetch.ts';
import { ingestUploadedClaimPolicy } from '../policy/claim-upload.ts';
import { buildFloridaMatchingGapReport } from '../florida/gaps.ts';

test('official fetch rejects non-allowlisted sources',async()=>{const result=await fetchOfficialSource({snapshotId:'S',authorityId:'A',url:'https://example.com/law',sourceType:'STATE_STATUTE'},async()=>new Response('x'));assert.equal(result.status,'REJECTED');});
test('uploaded policy intake preserves bytes and identifies missing required documents',()=>{const result=ingestUploadedClaimPolicy([{filename:'form.pdf',bytes:new TextEncoder().encode('HO-3'),documentType:'POLICY_FORM',formId:'HO-3',edition:'2024'}],'2026-03-15');assert.equal(result.ready,false);assert.ok(result.missing.includes('declarations page'));assert.equal(result.documents[0].sha256.length,64);});
test('gap report names evidence instead of hiding incomplete corpus state',()=>{const report=buildFloridaMatchingGapReport({historicalStatutesVerified:false,judicialOpinionsVerified:false,actualPolicyVerified:false,provenanceComplete:false,humanReviewComplete:false,criticalConflicts:0});assert.equal(report.readiness.canPromote,false);assert.equal(report.evidenceRequired.length,5);});

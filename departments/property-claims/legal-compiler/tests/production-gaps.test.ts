import test from 'node:test';
import assert from 'node:assert/strict';
import { InMemoryRepository } from '../persistence/repositories.ts';
import { parsePolicyFile, PlainTextPolicyParser } from '../policy/parser.ts';
import { verifyFloridaCase } from '../florida/case-verification.ts';
import { createOpinionSnapshot } from '../florida/opinions.ts';
import { fetchOfficialSource } from '../sources/official-fetch.ts';

test('durable repository rejects silent overwrite',async()=>{const repo=new InMemoryRepository<{id:string;value:string}>('id');await repo.put({id:'1',value:'a'});await assert.rejects(()=>repo.put({id:'1',value:'b'}));});
test('policy parser fails closed for unimplemented binary formats',async()=>{await assert.rejects(()=>parsePolicyFile({filename:'policy.pdf',mimeType:'application/pdf',bytes:new Uint8Array([1,2])},[new PlainTextPolicyParser()]),/unsupported policy document/);});
test('case verifier rejects missing provider record',async()=>{const result=await verifyFloridaCase('missing',{find:async()=>null,verifyCurrentStatus:async()=>({valid:false,negativeTreatment:[],subsequentHistory:[]})});assert.equal(result.status,'UNVERIFIED');});
test('case verifier requires official snapshot integrity and pinpoint metadata',async()=>{const opinion={caseId:'C',caseName:'Case',citation:'1',court:'THIRD_DCA' as const,district:'Third',decisionDate:'2020-01-01',issueCodes:['MATCHING'],policyLanguage:[],materialFacts:[],proceduralPosture:'appeal',holding:'holding',dicta:[],pinpoints:['p. 1'],subsequentHistory:[],negativeTreatment:[],statutoryDependency:[],policyDependency:[],currentStatus:'CANDIDATE' as const,verificationStatus:'UNVERIFIED' as const,snapshotId:'S'};const snapshot=createOpinionSnapshot({snapshotId:'S',caseId:'C',sourceUrl:'https://www.3dca.flcourts.org/opinion.pdf',content:'p. 1 holding',retrievedAt:'2026-09-01',officialSource:false});const result=await verifyFloridaCase('C',{find:async()=>({opinion,snapshot}),verifyCurrentStatus:async()=>({valid:true,negativeTreatment:[],subsequentHistory:[]})});assert.equal(result.status,'FAILED');});
test('official fetch enforces response size limits',async()=>{const result=await fetchOfficialSource({snapshotId:'S',authorityId:'A',url:'https://www.leg.state.fl.us/source',sourceType:'STATE_STATUTE',maxBytes:2},async()=>new Response('large'));assert.equal(result.status,'REJECTED');});

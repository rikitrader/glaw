import test from 'node:test';
import assert from 'node:assert/strict';
import { SUPPORTED_JURISDICTIONS, CORE_ISSUES, emptySourceRegistry } from '../jurisdictions/registry.ts';
import { validAt, bitemporalWarning } from '../temporal/engine.ts';
import { evaluateRule, validateRule } from '../dsl/rules.ts';
import { authorityRank, primaryAuthorityRequired } from '../authority/hierarchy.ts';
import { verifyCitation } from '../citations/verifier.ts';
import { compileAuthorityPackage } from '../core/compiler.ts';
import type { CompiledLegalRule, LegalAuthority, ClaimLegalContext } from '../types/index.ts';

const authority:LegalAuthority={authorityId:'A-TX-1',jurisdiction:'TX',authorityType:'STATE_STATUTE',title:'Test',citation:'Tex. Ins. Code § 1',officialSourceUrl:'https://example.gov/a',retrievedAt:'2026-01-01',contentHash:'a'.repeat(64),amends:[],repeals:[],interprets:[],negativeTreatment:[],verificationStatus:'VERIFIED'};
const rule:CompiledLegalRule={ruleId:'R-TX-1',jurisdiction:'TX',issue:'PROMPT_PAYMENT',validity:{validFrom:'2020-01-01',validTo:null,systemFrom:'2026-01-01',systemTo:null},priority:1,if:{all:[{field:'claim.notice',operator:'EXISTS'}],any:[],not:[]},then:{classification:'NOTICE_RECEIVED',effects:[]},exceptions:[],authorityRefs:['A-TX-1'],policyDependencies:[],factDependencies:['claim.notice'],confidence:90,humanReviewConditions:[],status:'AUTHORITY_VERIFIED'};
test('registry covers 50 states plus DC and does not imply completeness',()=>{assert.equal(SUPPORTED_JURISDICTIONS.length,51);assert.ok(SUPPORTED_JURISDICTIONS.every((item)=>item.sourceRegistryStatus==='NOT_STARTED'));assert.equal(CORE_ISSUES.length,13);assert.deepEqual(emptySourceRegistry('fl').jurisdiction,'FL');});
test('temporal engine answers valid-time and system-time questions separately',()=>{assert.equal(validAt({validFrom:'2022-01-01',validTo:'2024-01-01'},'2023-01-01'),true);assert.ok(bitemporalWarning({authorityId:'A',versionId:'V',temporal:{validFrom:'2022-01-01',validTo:null,systemFrom:'2025-01-01',systemTo:null},operativeText:'',sourceSnapshotId:'S',contentHash:'a'.repeat(64)},'2023-01-01','2024-01-01').length>0);});
test('rule DSL validates and evaluates declaratively',()=>{assert.deepEqual(validateRule(rule),[]);assert.equal(evaluateRule(rule,{'claim.notice':'2026-01-01'}),true);});
test('authority hierarchy distinguishes primary authority from secondary material',()=>{assert.ok(authorityRank('STATE_STATUTE')>authorityRank('NAIC_MODEL'));assert.equal(primaryAuthorityRequired(authority),true);});
test('citation verification blocks missing pinpoint and unverified sources',()=>{assert.equal(verifyCitation({citationId:'C-1',authority,source:authority.officialSourceUrl}).status,'PARTIALLY_VERIFIED');assert.equal(verifyCitation({citationId:'C-2',source:'https://bad'}).status,'FAILED');});
test('compiler fails closed when jurisdiction or verified rule is absent',()=>{const context:ClaimLegalContext={claimId:'C-1',jurisdictionCandidates:['TX'],resolvedJurisdiction:'TX',policyEffectiveDate:null,policyExpirationDate:null,dateOfLoss:'2026-01-01',issue:'PROMPT_PAYMENT',materialFacts:{}};const result=compileAuthorityPackage(context,{rules:[rule],propositions:[],authorities:[authority]});assert.equal(result.rules.length,1);assert.equal(result.humanReview,false);const unknown=compileAuthorityPackage({...context,resolvedJurisdiction:null},{rules:[rule],propositions:[],authorities:[authority]});assert.equal(unknown.humanReview,true);});

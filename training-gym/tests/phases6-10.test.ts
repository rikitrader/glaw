import test from 'node:test';
import assert from 'node:assert/strict';
import { compareBenchmark, runBenchmark } from '../benchmarks/runner.ts';
import { classifyFailures, adversarialScore } from '../evaluation/adversarial.ts';
import { toPreferencePair, toSftJsonl } from '../training/export.ts';
import { SkillGraph } from '../skills/graph.ts';
import { ProfessionalGym } from '../gyms/professional.ts';
import { createTwin, validateTwin } from '../organization/twin.ts';
import { SpreadsheetGym } from '../gyms/spreadsheet/index.ts';

const agent={name:'reference',async run(input:{observe:()=>Promise<unknown>;step:(action:{tool:string;arguments:Record<string,unknown>})=>Promise<unknown>}){await input.observe();await input.step({tool:'spreadsheet.set_formula',arguments:{cell:'C2',formula:'=A2-B2'}});}};
test('benchmark runner executes identical seeded episodes and compares metrics',async()=>{const result=await runBenchmark({benchmarkId:'spreadsheet-v1',gymFactory:()=>new SpreadsheetGym(),taskSeeds:[1,2],models:[agent]});assert.equal(result.rows.length,2);assert.equal(compareBenchmark(result.rows)[0].successRate,1);});
test('adversarial evaluator classifies unsafe outcomes and penalizes them',()=>{const evaluation={totalScore:1,dimensions:{},penalties:{},success:false,failures:['forbidden criterion satisfied'],automaticScore:1};const findings=classifyFailures(evaluation,{promptInjectionDetected:true});assert.equal(findings.length,2);assert.equal(adversarialScore(evaluation,findings),.75);});
test('training exports and skill graph preserve separate training records',()=>{const example={taskId:'t',trajectory:{trajectoryId:'a',episodeId:'e',steps:[]},reward:1,accepted:true};assert.ok(toSftJsonl(example).endsWith('\n'));assert.equal(toPreferencePair(example,{...example,reward:0}).rejectedReward,0);const graph=new SkillGraph();graph.add({skillId:'crm.search',name:'Search CRM',parentId:null});graph.record('crm.search',true);assert.equal(graph.getScores()[0].score,1);});
test('professional domain gym requires verified source before completion',async()=>{const gym=new ProfessionalGym('insurance-claims');await gym.reset();await gym.step({tool:'insurance-claims.add_note',arguments:{note:'Policy and evidence reviewed'}});await gym.step({tool:'insurance-claims.complete_review',arguments:{source_verified:true}});assert.equal((await gym.evaluate()).success,true);});
test('digital twin maintains referential integrity',()=>{const twin=createTwin(42,4);assert.deepEqual(validateTwin(twin),[]);});

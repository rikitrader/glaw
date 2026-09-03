import test from 'node:test';
import assert from 'node:assert/strict';
import { generateTasks } from '../core/generator.ts';
import { exportTrajectoryJsonl } from '../core/export.ts';
import { validateExperiment } from '../experiments.ts';
import { DEFAULT_SANDBOX_POLICY, validateActionTool } from '../security/policy.ts';
import { SpreadsheetGym } from '../gyms/spreadsheet/index.ts';
import { Gym } from '../sdk.ts';

test('seeded task generator produces versionable task instances',()=>{const tasks=generateTasks({id:'profit',gym:'spreadsheet',difficulty:'beginner',objective:(v)=>`Calculate ${v.cell}`,criteria:(v)=>[{path:`workbooks.0.sheets.0.cells.${v.cell}`,operator:'EXISTS'}],maxSteps:5},[{cell:'C2',seed:1}]);assert.equal(tasks[0].id,'profit-1');assert.equal(tasks[0].seed,1);});
test('trajectory exports machine-readable JSONL',async()=>{const gym=new Gym(new SpreadsheetGym());await gym.reset({seed:1});await gym.step({tool:'spreadsheet.set_formula',arguments:{cell:'C2',formula:'=A2-B2'}});const line=exportTrajectoryJsonl({trajectoryId:'t',episodeId:'e',steps:await gym.replay().then((steps)=>steps.map((result,index)=>({step:index+1,observation:result.observation,action:{tool:'x',arguments:{}},result,stateBefore:null,stateAfter:null}))) });assert.ok(line.endsWith('\n'));});
test('experiment and sandbox validation fail closed',()=>{assert.ok(validateExperiment({experimentId:'x',gym:'spreadsheet',models:[],taskIds:['t'],episodes:1,seeds:[1],metrics:[]}).length);assert.throws(()=>validateActionTool('host.shell',DEFAULT_SANDBOX_POLICY));});

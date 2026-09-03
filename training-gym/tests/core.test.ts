import test from 'node:test';
import assert from 'node:assert/strict';
import { SpreadsheetGym } from '../gyms/spreadsheet/index.ts';
import { Gym } from '../sdk.ts';

test('spreadsheet gym is resettable and evaluates exact state',async()=>{const gym=new Gym(new SpreadsheetGym());await gym.reset({seed:281192});await gym.step({tool:'spreadsheet.set_formula',arguments:{cell:'C2',formula:'=A2-B2'}});const result=await gym.evaluate();assert.equal(result.success,true);assert.equal(result.totalScore,1);});
test('invalid tool or uncontrolled mutation fails safely',async()=>{const gym=new Gym(new SpreadsheetGym());await gym.reset();await assert.rejects(()=>gym.step({tool:'spreadsheet.delete_workbook',arguments:{}}));await assert.rejects(()=>gym.step({tool:'spreadsheet.write_cell',arguments:{cell:'bad',value:1}}));});
test('snapshot restore and replay preserve trajectory',async()=>{const gym=new Gym(new SpreadsheetGym());await gym.reset({seed:5});const snapshot=await gym.snapshot();await gym.step({tool:'spreadsheet.write_cell',arguments:{cell:'A2',value:200}});await gym.restore(snapshot);assert.equal((await gym.getState()).workbooks[0].sheets[0].cells.A2,100);assert.equal((await gym.replay()).length,1);});

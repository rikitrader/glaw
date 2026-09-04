import test from 'node:test';
import assert from 'node:assert/strict';
import { Gym } from '../sdk.ts';
import { SalesforceGym } from '../gyms/salesforce/index.ts';
import { SlackGym } from '../gyms/slack/index.ts';
import { SpreadsheetGym } from '../gyms/spreadsheet/index.ts';
import { CompositeGym } from '../gyms/composite.ts';

test('Salesforce gym performs controlled CRM update',async()=>{const gym=new Gym(new SalesforceGym());await gym.reset({seed:2});await gym.step({tool:'salesforce.update_opportunity',arguments:{opportunity_id:'opp-18291',stage:'Negotiation',amount:250000,next_step:'Send contract'}});assert.equal((await gym.evaluate()).success,true);});
test('Slack gym finds and resolves a decision',async()=>{const gym=new Gym(new SlackGym());await gym.reset({seed:2});const result=await gym.step({tool:'slack.resolve_message',arguments:{message_id:'msg-1'}});assert.equal(result.metadata.resolved,'msg-1');assert.equal((await gym.evaluate()).success,true);});
test('composite gym routes normalized tools to the correct application',async()=>{const gym=new Gym(new CompositeGym({spreadsheet:new SpreadsheetGym(),salesforce:new SalesforceGym(),slack:new SlackGym()}));await gym.reset({seed:7});await gym.step({tool:'slack.resolve_message',arguments:{message_id:'msg-1'}});await gym.step({tool:'salesforce.update_opportunity',arguments:{opportunity_id:'opp-18291',stage:'Negotiation',amount:250000,next_step:'Send contract'}});assert.equal((await gym.getState() as {opportunities?:unknown}).opportunities!==undefined,true);});

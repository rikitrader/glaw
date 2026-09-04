import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { jsonlEvents, runWorkflow, validateWorkflow, type WorkflowExecutor } from '../src/workflow.ts';

const definition = JSON.parse(readFileSync(new URL('../workflows/venezuela-monetary-reform.json', import.meta.url), 'utf8'));
const pass: WorkflowExecutor = () => ({ status: 'PASS' });
const executors = Object.fromEntries([...new Set(definition.nodes.map((node: { executor: string }) => node.executor))].map((name: string) => [name, pass]));

test('workflow definition validates with all registered executors', () => assert.deepEqual(validateWorkflow(definition, executors), []));
test('workflow runner blocks until all required gates pass', async () => {
  const run = await runWorkflow(definition, executors, { run_id: 'RUN-1', initial_gates: { 'intake-ready': 'PASS' } });
  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.nodes['question-intake'], 'PASS');
  assert.match(jsonlEvents(run), /RUN_FINISHED/);
});
test('workflow validator rejects missing executors and cycles', () => {
  const invalid = { ...definition, nodes: [...definition.nodes, { id: 'orphan', executor: 'missing' }], edges: [...definition.edges, ['policy-decision-matrix', 'question-intake']] };
  assert.ok(validateWorkflow(invalid, executors).some((error) => error.includes('missing executor')));
  assert.ok(validateWorkflow(invalid, executors).some((error) => error.includes('workflow cycle')));
});
test('workflow runner fails closed when an executor emits an undeclared gate', async () => {
  const custom = { ...definition, nodes: [{ id: 'only', executor: 'bad-gate' }], edges: [], required_gates: ['intake-ready'], diagnostic_continuation: undefined };
  const run = await runWorkflow(custom, { 'bad-gate': () => ({ status: 'PASS', gate_updates: { 'not-declared': 'PASS' } }) }, { run_id: 'RUN-UNKNOWN-GATE' });
  assert.equal(run.status, 'FAILED');
  assert.equal(run.nodes.only, 'FAIL');
  assert.match(jsonlEvents(run), /executor emitted unknown gates/);
});

test('workflow diagnostic continuation preserves BLOCKED status while running only declared downstream diagnostics', async () => {
  const custom = {
    id: 'DIAGNOSTIC-1', version: '1',
    nodes: [
      { id: 'trigger', executor: 'blocked' },
      { id: 'diagnostic', executor: 'diagnostic' },
      { id: 'outside', executor: 'outside' }
    ],
    edges: [['trigger', 'diagnostic'], ['diagnostic', 'outside']],
    required_gates: ['critical'], stop_conditions: [],
    diagnostic_continuation: { trigger_nodes: ['trigger'], allowed_nodes: ['diagnostic'] }
  };
  const run = await runWorkflow(custom, {
    blocked: () => ({ status: 'BLOCKED', reason: 'missing evidence' }),
    diagnostic: () => ({ status: 'PASS', artifacts: { diagnostic: { status: 'INFORMATIVE_ONLY' } } }),
    outside: () => ({ status: 'PASS' })
  }, { run_id: 'RUN-DIAGNOSTIC' });
  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.nodes.trigger, 'BLOCKED');
  assert.equal(run.nodes.diagnostic, 'PASS');
  assert.equal(run.nodes.outside, 'PENDING');
  assert.match(jsonlEvents(run), /diagnostic_continuation/);
});

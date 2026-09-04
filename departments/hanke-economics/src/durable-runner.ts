import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { jsonlEvents, runWorkflow, type WorkflowDefinition, type WorkflowExecutor, type WorkflowRun } from './workflow.ts';

export interface PersistedWorkflowPaths { event_path: string; run_path: string; }

export function defaultRunPath(eventPath: string): string {
  return eventPath.endsWith('.events.jsonl') ? `${eventPath.slice(0, -'.events.jsonl'.length)}.json` : `${eventPath}.json`;
}

export function persistWorkflowRun(run: WorkflowRun, paths: PersistedWorkflowPaths): void {
  mkdirSync(dirname(paths.event_path), { recursive: true });
  mkdirSync(dirname(paths.run_path), { recursive: true });
  writeFileSync(paths.event_path, jsonlEvents(run), 'utf8');
  writeFileSync(paths.run_path, JSON.stringify(run, null, 2), 'utf8');
}

export async function runAndPersistWorkflow(definition: WorkflowDefinition, executors: Record<string, WorkflowExecutor>, runId: string, eventPath: string, runPath = defaultRunPath(eventPath)) {
  const run = await runWorkflow(definition, executors, { run_id: runId });
  persistWorkflowRun(run, { event_path: eventPath, run_path: runPath });
  return run;
}

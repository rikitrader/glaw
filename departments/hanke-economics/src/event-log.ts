import { appendFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import type { WorkflowEvent } from './workflow.ts';

export function appendWorkflowEvent(path: string, event: WorkflowEvent): void {
  mkdirSync(dirname(path), { recursive: true });
  appendFileSync(path, `${JSON.stringify(event)}\n`, 'utf8');
}

export function persistWorkflowEvents(path: string, events: WorkflowEvent[]): void {
  for (const event of events) appendWorkflowEvent(path, event);
}

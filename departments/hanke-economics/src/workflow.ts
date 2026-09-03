import type { AuditFinding } from './types.ts';

export type NodeStatus = 'PENDING' | 'RUNNING' | 'PASS' | 'BLOCKED' | 'FAIL';
export type GateStatus = 'OPEN' | 'PASS' | 'BLOCKED';
export type RunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'BLOCKED' | 'FAILED';
export interface GateRecord { status: GateStatus; owner: string; at: string; evidence_ids: string[]; reason?: string; }

export interface WorkflowNodeDefinition { id: string; executor: string; required_gates?: string[]; }
export interface DiagnosticContinuation { trigger_nodes: string[]; allowed_nodes: string[]; }
export interface WorkflowDefinition { id: string; version: string; nodes: WorkflowNodeDefinition[]; edges: [string, string][]; required_gates: string[]; stop_conditions: string[]; diagnostic_continuation?: DiagnosticContinuation; }
export interface NodeExecutionContext { run_id: string; workflow: WorkflowDefinition; node: WorkflowNodeDefinition; artifacts: Record<string, unknown>; gates: Record<string, GateStatus>; }
export interface NodeExecutionResult { status: Exclude<NodeStatus, 'PENDING' | 'RUNNING'>; artifacts?: Record<string, unknown>; gate_updates?: Record<string, GateStatus>; gate_evidence?: Record<string, { owner: string; evidence_ids: string[]; reason?: string }>; findings?: AuditFinding[]; reason?: string; }
export type WorkflowExecutor = (context: NodeExecutionContext) => Promise<NodeExecutionResult> | NodeExecutionResult;
export interface WorkflowEvent { sequence: number; at: string; type: 'RUN_STARTED' | 'NODE_STARTED' | 'NODE_FINISHED' | 'GATE_UPDATED' | 'RUN_FINISHED'; run_id: string; node_id?: string; status?: string; payload?: Record<string, unknown>; }
export interface WorkflowRun { run_id: string; workflow_id: string; status: RunStatus; nodes: Record<string, NodeStatus>; gates: Record<string, GateStatus>; gate_records: Record<string, GateRecord>; artifacts: Record<string, unknown>; findings: AuditFinding[]; events: WorkflowEvent[]; }

function event(run: WorkflowRun, type: WorkflowEvent['type'], payload: Omit<WorkflowEvent, 'sequence' | 'at' | 'type' | 'run_id'> = {}): void {
  run.events.push({ sequence: run.events.length + 1, at: new Date().toISOString(), type, run_id: run.run_id, ...payload });
}

export function validateWorkflow(definition: WorkflowDefinition, executors: Record<string, WorkflowExecutor> = {}): string[] {
  const errors: string[] = [];
  const ids = definition.nodes.map((node) => node.id);
  const unique = new Set(ids);
  if (unique.size !== ids.length) errors.push('duplicate workflow node');
  for (const node of definition.nodes) if (!(node.executor in executors)) errors.push(`missing executor: ${node.executor}`);
  for (const [from, to] of definition.edges) {
    if (!unique.has(from)) errors.push(`dangling edge source: ${from}`);
    if (!unique.has(to)) errors.push(`dangling edge target: ${to}`);
  }
  for (const gate of definition.required_gates) if (!gate || definition.stop_conditions.includes(gate)) errors.push(`invalid required gate: ${gate}`);
  const continuation = definition.diagnostic_continuation;
  if (continuation) {
    for (const node of [...continuation.trigger_nodes, ...continuation.allowed_nodes]) if (!unique.has(node)) errors.push(`diagnostic continuation references unknown node: ${node}`);
    if (!continuation.trigger_nodes.length) errors.push('diagnostic continuation requires trigger_nodes');
    if (!continuation.allowed_nodes.length) errors.push('diagnostic continuation requires allowed_nodes');
  }
  const visiting = new Set<string>(); const visited = new Set<string>();
  const children = new Map<string, string[]>();
  for (const [from, to] of definition.edges) children.set(from, [...(children.get(from) ?? []), to]);
  const visit = (id: string) => { if (visiting.has(id)) { errors.push(`workflow cycle at: ${id}`); return; } if (visited.has(id)) return; visiting.add(id); for (const child of children.get(id) ?? []) visit(child); visiting.delete(id); visited.add(id); };
  for (const id of ids) visit(id);
  return [...new Set(errors)];
}

function orderedNodes(definition: WorkflowDefinition): WorkflowNodeDefinition[] {
  const incoming = new Map(definition.nodes.map((node) => [node.id, 0]));
  const children = new Map<string, string[]>();
  for (const [from, to] of definition.edges) { incoming.set(to, (incoming.get(to) ?? 0) + 1); children.set(from, [...(children.get(from) ?? []), to]); }
  const queue = definition.nodes.filter((node) => incoming.get(node.id) === 0).map((node) => node.id);
  const output: WorkflowNodeDefinition[] = [];
  while (queue.length) { const id = queue.shift()!; output.push(definition.nodes.find((node) => node.id === id)!); for (const child of children.get(id) ?? []) { incoming.set(child, incoming.get(child)! - 1); if (incoming.get(child) === 0) queue.push(child); } }
  return output;
}

export async function runWorkflow(definition: WorkflowDefinition, executors: Record<string, WorkflowExecutor>, options: { run_id: string; initial_artifacts?: Record<string, unknown>; initial_gates?: Record<string, GateStatus> }): Promise<WorkflowRun> {
  const errors = validateWorkflow(definition, executors);
  const initialGate = (gate: string): GateRecord => ({ status: options.initial_gates?.[gate] ?? 'OPEN', owner: 'workflow-initializer', at: new Date().toISOString(), evidence_ids: [] });
  const gate_records = Object.fromEntries(definition.required_gates.map((gate) => [gate, initialGate(gate)]));
  const run: WorkflowRun = { run_id: options.run_id, workflow_id: definition.id, status: errors.length ? 'FAILED' : 'PENDING', nodes: Object.fromEntries(definition.nodes.map((node) => [node.id, 'PENDING'])), gates: Object.fromEntries(Object.entries(gate_records).map(([gate, record]) => [gate, record.status])), gate_records, artifacts: options.initial_artifacts ?? {}, findings: [], events: [] };
  event(run, 'RUN_STARTED', { status: run.status, payload: { validation_errors: errors } });
  if (errors.length) { event(run, 'RUN_FINISHED', { status: 'FAILED', payload: { errors } }); return run; }
  run.status = 'RUNNING';
  let diagnosticContinuation = false;
  const continuation = definition.diagnostic_continuation;
  const canContinueDiagnostic = (nodeId: string): boolean => Boolean(diagnosticContinuation && continuation?.allowed_nodes.includes(nodeId));
  for (const node of orderedNodes(definition)) {
    if (diagnosticContinuation && !canContinueDiagnostic(node.id)) {
      run.status = 'BLOCKED';
      event(run, 'NODE_FINISHED', { node_id: node.id, status: 'PENDING', payload: { diagnostic_continuation: 'STOPPED', reason: 'node is outside the declared diagnostic continuation' } });
      break;
    }
    if (node.required_gates?.some((gate) => run.gates[gate] !== 'PASS')) {
      run.nodes[node.id] = 'BLOCKED'; run.status = 'BLOCKED';
      event(run, 'NODE_FINISHED', { node_id: node.id, status: 'BLOCKED', payload: { reason: 'required gate is not passed', diagnostic_continuation: canContinueDiagnostic(node.id) } });
      if (canContinueDiagnostic(node.id)) continue;
      break;
    }
    run.nodes[node.id] = 'RUNNING'; event(run, 'NODE_STARTED', { node_id: node.id, status: 'RUNNING' });
    const result = await executors[node.executor]({ run_id: run.run_id, workflow: definition, node, artifacts: run.artifacts, gates: run.gates });
    run.nodes[node.id] = result.status; if (result.artifacts) Object.assign(run.artifacts, result.artifacts); if (result.findings) run.findings.push(...result.findings);
    const gateUpdates = result.gate_updates ?? {};
    const unknownGates = Object.keys(gateUpdates).filter((gate) => !definition.required_gates.includes(gate));
    if (unknownGates.length) {
      run.nodes[node.id] = 'FAIL';
      run.status = 'FAILED';
      event(run, 'NODE_FINISHED', { node_id: node.id, status: 'FAIL', payload: { reason: `executor emitted unknown gates: ${unknownGates.join(', ')}` } });
      break;
    }
    for (const [gate, status] of Object.entries(gateUpdates)) {
      run.gates[gate] = status;
      const evidence = result.gate_evidence?.[gate];
      run.gate_records[gate] = { status, owner: evidence?.owner ?? node.executor, at: new Date().toISOString(), evidence_ids: evidence?.evidence_ids ?? [], reason: evidence?.reason ?? result.reason };
      event(run, 'GATE_UPDATED', { node_id: node.id, status, payload: { gate, owner: run.gate_records[gate].owner, evidence_ids: run.gate_records[gate].evidence_ids, reason: run.gate_records[gate].reason } });
    }
    const startsDiagnosticContinuation = result.status === 'BLOCKED' && continuation?.trigger_nodes.includes(node.id);
    event(run, 'NODE_FINISHED', { node_id: node.id, status: result.status, payload: { reason: result.reason, ...(startsDiagnosticContinuation ? { diagnostic_continuation: 'STARTED', allowed_nodes: continuation?.allowed_nodes } : {}) } });
    if (result.status === 'FAIL') { run.status = 'FAILED'; break; }
    if (result.status === 'BLOCKED') {
      run.status = 'BLOCKED';
      if (continuation?.trigger_nodes.includes(node.id) || canContinueDiagnostic(node.id)) {
        diagnosticContinuation = true;
        continue;
      }
      break;
    }
  }
  if (run.status === 'RUNNING') run.status = definition.required_gates.every((gate) => run.gates[gate] === 'PASS') ? 'COMPLETED' : 'BLOCKED';
  event(run, 'RUN_FINISHED', { status: run.status, payload: { gates: run.gates } });
  return run;
}

export function jsonlEvents(run: WorkflowRun): string { return run.events.map((item) => JSON.stringify(item)).join('\n') + '\n'; }

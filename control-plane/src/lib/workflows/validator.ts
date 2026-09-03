import { NODE_BY_TYPE, type StudioNodeType, type StudioNodeData } from "./node-registry";
import type { Edge, Node } from "@xyflow/react";

export type ValidationSeverity = "error" | "warning" | "info";
export interface ValidationFinding { id: string; severity: ValidationSeverity; message: string; nodeId?: string; edgeId?: string; }

export function validateConnection(sourceType: StudioNodeType, targetType: StudioNodeType) {
  const allowed = NODE_BY_TYPE[sourceType]?.allowedTargets ?? [];
  return { valid: allowed.includes(targetType), message: allowed.includes(targetType) ? "Connection allowed" : `${NODE_BY_TYPE[sourceType]?.label ?? sourceType} cannot connect directly to ${NODE_BY_TYPE[targetType]?.label ?? targetType}` };
}

export function validateGraph(nodes: Node<StudioNodeData>[], edges: Edge[]): ValidationFinding[] {
  const findings: ValidationFinding[] = [];
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  for (const edge of edges) {
    const source = nodeMap.get(edge.source); const target = nodeMap.get(edge.target);
    if (!source || !target) findings.push({ id: `edge-${edge.id}`, severity: "error", message: "Edge references a missing node", edgeId: edge.id });
    else { const result = validateConnection(source.data.type, target.data.type); if (!result.valid) findings.push({ id: `connection-${edge.id}`, severity: "error", message: result.message, edgeId: edge.id }); }
  }
  for (const node of nodes) {
    const incoming = edges.some((edge) => edge.target === node.id); const outgoing = edges.some((edge) => edge.source === node.id);
    if (nodes.length > 1 && node.data.type !== "trigger" && node.data.type !== "department" && !incoming) findings.push({ id: `orphan-in-${node.id}`, severity: "warning", message: `${node.data.label} has no upstream connection`, nodeId: node.id });
    if (node.data.type !== "output" && node.data.type !== "error-handler" && !outgoing) findings.push({ id: `dead-end-${node.id}`, severity: "warning", message: `${node.data.label} has no downstream connection`, nodeId: node.id });
    if (["agent", "orchestrator", "red-team", "blue-team"].includes(node.data.type) && !node.data.config.modelPolicy) findings.push({ id: `model-${node.id}`, severity: "warning", message: `${node.data.label} needs a model policy before publish`, nodeId: node.id });
    if (["agent", "red-team", "blue-team"].includes(node.data.type) && !node.data.config.personaId) findings.push({ id: `persona-${node.id}`, severity: "error", message: `${node.data.label} must be attached to a governed persona`, nodeId: node.id });
    if (node.data.type === "skill" && !node.data.config.skillId) findings.push({ id: `skill-${node.id}`, severity: "error", message: `${node.data.label} must reference a signed skill version`, nodeId: node.id });
    if (["adapter", "mcp-adapter", "api-adapter", "payment-gate"].includes(node.data.type) && !node.data.config.adapterId) findings.push({ id: `adapter-${node.id}`, severity: "error", message: `${node.data.label} must reference a registered adapter`, nodeId: node.id });
    if (["jurisdiction-pack", "practice-pack"].includes(node.data.type) && !node.data.config.packId) findings.push({ id: `pack-${node.id}`, severity: "error", message: `${node.data.label} must reference a versioned pack`, nodeId: node.id });
    if (node.data.type === "payment-gate" && node.data.config.legalAuthorizationSeparate !== true) findings.push({ id: `payment-${node.id}`, severity: "error", message: "x402 usage payment cannot authorize a legal action", nodeId: node.id });
  }
  if (!nodes.some((node) => node.data.type === "human-approval")) findings.push({ id: "missing-approval", severity: "error", message: "High-risk legal workflows require a Human Approval node" });
  if (!nodes.some((node) => node.data.type === "red-team")) findings.push({ id: "missing-red-team", severity: "warning", message: "No Red Team review node is configured" });
  if (!nodes.some((node) => node.data.type === "blue-team")) findings.push({ id: "missing-blue-team", severity: "warning", message: "No Blue Team remediation node is configured" });
  return findings;
}

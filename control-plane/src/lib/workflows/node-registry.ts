import type { Edge, Node } from "@xyflow/react";

export type StudioNodeType =
  | "department" | "matter" | "workflow" | "orchestrator" | "agent" | "agent-swarm"
  | "skill" | "adapter" | "tool" | "rag" | "model" | "validator" | "red-team"
  | "blue-team" | "human-approval" | "trigger" | "condition" | "router" | "parallel"
  | "loop" | "wait" | "retry" | "notification" | "output" | "error-handler" | "worker"
  | "queue" | "database" | "r2" | "vectorize" | "external-api" | "persona"
  | "jurisdiction-pack" | "practice-pack" | "mcp-adapter" | "api-adapter" | "payment-gate";

export type StudioCategory = "Organization" | "AI" | "Capabilities" | "Knowledge" | "Models" | "Workflow" | "Infrastructure";
export type StudioStatus = "idle" | "running" | "complete" | "waiting" | "approval" | "warning" | "failed" | "blocked";

export interface NodeDefinition {
  type: StudioNodeType;
  label: string;
  category: StudioCategory;
  icon: string;
  description: string;
  inputs: string[];
  outputs: string[];
  allowedTargets: StudioNodeType[];
  defaultConfig: Record<string, unknown>;
}

export interface StudioNodeData extends Record<string, unknown> {
  label: string;
  type: StudioNodeType;
  category: StudioCategory;
  description: string;
  status: StudioStatus;
  config: Record<string, unknown>;
}

const definition = (type: StudioNodeType, label: string, category: StudioCategory, icon: string, description: string, allowedTargets: StudioNodeType[], defaultConfig: Record<string, unknown> = {}): NodeDefinition => ({
  type, label, category, icon, description, allowedTargets, defaultConfig,
  inputs: ["context"], outputs: ["result"]
});

export const NODE_REGISTRY: NodeDefinition[] = [
  definition("department", "Department", "Organization", "⌂", "Practice area and ownership boundary", ["workflow", "agent", "skill", "rag", "human-approval"]),
  definition("matter", "Matter", "Organization", "◉", "Matter or project scope", ["workflow", "orchestrator", "agent"]),
  definition("workflow", "Workflow", "Organization", "◇", "Versioned executable graph", ["trigger", "orchestrator", "agent", "router", "condition", "parallel"]),
  definition("orchestrator", "Orchestrator", "AI", "◎", "Coordinates a work plan", ["agent", "agent-swarm", "router", "parallel", "condition"]),
  definition("agent", "Agent", "AI", "◌", "Bounded legal AI worker", ["persona", "skill", "adapter", "tool", "rag", "model", "validator", "red-team", "blue-team", "human-approval", "output", "condition"]),
  definition("persona", "Persona", "AI", "♙", "Named lawyer, agent, reviewer, or operator identity", ["agent", "skill", "workflow", "human-approval"], { personaId: "research-counsel", ownerRole: "attorney" }),
  definition("agent-swarm", "Agent Swarm", "AI", "✣", "Parallel specialist group", ["agent", "parallel", "validator", "red-team"]),
  definition("skill", "Skill", "Capabilities", "✦", "Reusable capability with schemas", ["adapter", "tool", "rag", "validator", "model"]),
  definition("adapter", "Adapter", "Capabilities", "↔", "Provider-neutral external boundary", ["tool", "external-api", "worker", "database", "r2"]),
  definition("mcp-adapter", "MCP Adapter", "Capabilities", "⌘", "Authorized Model Context Protocol server boundary", ["tool", "agent", "skill"], { adapterId: "mcp-legal-research", protocol: "MCP" }),
  definition("api-adapter", "API Adapter", "Capabilities", "↗", "Scoped REST or GraphQL integration boundary", ["tool", "external-api", "worker"], { adapterId: "dms-api", protocol: "REST" }),
  definition("payment-gate", "x402 Payment Gate", "Capabilities", "$", "Metered usage settlement gate; never legal authorization", ["agent", "tool", "output", "human-approval"], { adapterId: "x402-settlement", enabled: false, maxPerRunUsd: 25, approvalRequiredAboveUsd: 5, legalAuthorizationSeparate: true }),
  definition("tool", "Tool", "Capabilities", "◆", "Governed operation", ["external-api", "database", "r2", "queue", "output"]),
  definition("rag", "RAG", "Knowledge", "⌁", "Permissioned retrieval system", ["agent", "skill", "model", "validator"]),
  definition("model", "Model Router", "Models", "◈", "Approved model policy", ["agent", "rag", "output"]),
  definition("validator", "Validator", "Capabilities", "✓", "Quality or policy gate", ["red-team", "blue-team", "human-approval", "output", "error-handler"]),
  definition("red-team", "Red Team", "AI", "⚔", "Adversarial review", ["blue-team", "human-approval", "error-handler"]),
  definition("blue-team", "Blue Team", "AI", "✚", "Remediation and revision", ["validator", "human-approval", "output", "red-team"]),
  definition("human-approval", "Human Approval", "Workflow", "♙", "Named professional approval gate", ["output", "notification", "error-handler", "blue-team"]),
  definition("trigger", "Trigger", "Workflow", "⚡", "Starts a workflow", ["workflow", "orchestrator", "agent", "router"]),
  definition("condition", "Condition", "Workflow", "?", "Branches on a rule", ["agent", "workflow", "router", "output", "error-handler"]),
  definition("router", "Router", "Workflow", "⑂", "Routes by matter or policy", ["agent", "workflow", "parallel", "condition"]),
  definition("parallel", "Parallel", "Workflow", "∥", "Runs branches concurrently", ["agent", "skill", "rag", "validator", "blue-team"]),
  definition("loop", "Loop", "Workflow", "↻", "Bounded repeat operation", ["agent", "validator", "output"]),
  definition("wait", "Wait", "Workflow", "◷", "Durable pause", ["human-approval", "agent", "notification"]),
  definition("retry", "Retry", "Workflow", "↺", "Failure retry policy", ["agent", "tool", "adapter", "output"]),
  definition("notification", "Notification", "Workflow", "✉", "Operational message", ["human-approval", "output"]),
  definition("output", "Output", "Workflow", "⇢", "Versioned artifact or result", []),
  definition("error-handler", "Error Handler", "Workflow", "!", "Failure and escalation path", ["retry", "human-approval", "notification", "output"]),
  definition("worker", "Worker", "Infrastructure", "▣", "Cloudflare Worker boundary", ["workflow", "queue", "database", "r2", "external-api"]),
  definition("queue", "Queue", "Infrastructure", "▤", "Asynchronous job boundary", ["worker", "agent", "workflow"]),
  definition("database", "D1", "Infrastructure", "▥", "Relational control-plane storage", ["worker", "adapter", "tool"]),
  definition("r2", "R2", "Infrastructure", "▧", "Immutable object storage", ["worker", "adapter", "tool", "rag"]),
  definition("vectorize", "Vectorize", "Infrastructure", "⋮", "Semantic index boundary", ["rag", "worker"]),
  definition("external-api", "External API", "Infrastructure", "↗", "External provider boundary", [])
  ,definition("jurisdiction-pack", "Jurisdiction Pack", "Knowledge", "§", "Versioned jurisdiction rules and authority hierarchy", ["workflow", "agent", "skill", "validator"], { packId: "us-federal", kind: "jurisdiction" })
  ,definition("practice-pack", "Practice Pack", "Knowledge", "▤", "Practice-area workflow, forms, and benchmark pack", ["workflow", "agent", "skill", "validator"], { packId: "civil-litigation", kind: "practice" })
];

export const NODE_BY_TYPE = Object.fromEntries(NODE_REGISTRY.map((item) => [item.type, item])) as Record<StudioNodeType, NodeDefinition>;

export const createStudioNode = (type: StudioNodeType, id: string, position: { x: number; y: number }, overrides: Partial<StudioNodeData> = {}): Node<StudioNodeData> => {
  const item = NODE_BY_TYPE[type];
  return { id, type: "studio", position, data: { label: item.label, type, category: item.category, description: item.description, status: "idle", config: { ...item.defaultConfig }, ...overrides } };
};

export const demoNodes: Node<StudioNodeData>[] = [
  createStudioNode("department", "department-litigation", { x: 0, y: 180 }, { label: "Litigation Department", status: "complete" }),
  createStudioNode("workflow", "workflow-litigation", { x: 230, y: 180 }, { label: "Litigation Analysis", status: "complete" }),
  createStudioNode("orchestrator", "orchestrator-matter", { x: 460, y: 180 }, { label: "Matter Orchestrator", status: "running" }),
  createStudioNode("agent", "agent-research", { x: 700, y: 90 }, { label: "Legal Research Agent", status: "waiting" }),
  createStudioNode("persona", "persona-research-counsel", { x: 940, y: 15 }, { label: "Research Counsel", status: "complete", config: { personaId: "research-counsel", kind: "lawyer", workflowId: "litigation-analysis" } }),
  createStudioNode("skill", "skill-research", { x: 1180, y: 15 }, { label: "Legal Research Skill", status: "complete", config: { skillId: "legal-research", version: "3.4.1" } }),
  createStudioNode("mcp-adapter", "adapter-research-mcp", { x: 1420, y: 15 }, { label: "Legal Research MCP", status: "complete", config: { adapterId: "mcp-legal-research", protocol: "MCP" } }),
  createStudioNode("jurisdiction-pack", "pack-federal", { x: 1180, y: 165 }, { label: "US Federal Pack", status: "complete", config: { packId: "us-federal", kind: "jurisdiction" } }),
  createStudioNode("rag", "rag-case-law", { x: 1420, y: 165 }, { label: "Case Law RAG", status: "complete" }),
  createStudioNode("agent", "agent-drafting", { x: 1180, y: 340 }, { label: "Drafting Agent", status: "waiting", config: { personaId: "drafting-counsel", modelPolicy: "approved-legal-reasoning" } }),
  createStudioNode("validator", "validator-citation", { x: 1420, y: 340 }, { label: "Citation Validator", status: "waiting" }),
  createStudioNode("red-team", "red-team-opposition", { x: 1660, y: 260 }, { label: "Opposition Counsel", status: "idle", config: { personaId: "opposition-counsel" } }),
  createStudioNode("blue-team", "blue-team-defense", { x: 1900, y: 260 }, { label: "Defense Remediation", status: "idle" }),
  createStudioNode("payment-gate", "payment-usage", { x: 1660, y: 450 }, { label: "Usage Settlement (x402)", status: "idle", config: { adapterId: "x402-settlement", enabled: false, legalAuthorizationSeparate: true } }),
  createStudioNode("human-approval", "approval-attorney", { x: 2140, y: 260 }, { label: "Attorney Approval", status: "approval", config: { roleRequired: "attorney", approvalRequired: true } }),
  createStudioNode("output", "output-final", { x: 2380, y: 260 }, { label: "Final Output", status: "idle" })
];

export const demoEdges: Edge[] = [
  ["department-litigation", "workflow-litigation"], ["workflow-litigation", "orchestrator-matter"], ["orchestrator-matter", "agent-research"],
  ["agent-research", "persona-research-counsel"], ["persona-research-counsel", "skill-research"], ["skill-research", "adapter-research-mcp"], ["agent-research", "rag-case-law"], ["agent-research", "agent-drafting"],
  ["skill-research", "pack-federal"], ["pack-federal", "rag-case-law"],
  ["agent-drafting", "validator-citation"], ["validator-citation", "red-team-opposition"], ["red-team-opposition", "blue-team-defense"],
  ["blue-team-defense", "approval-attorney"], ["blue-team-defense", "payment-usage"], ["approval-attorney", "output-final"]
].map(([source, target]) => ({ id: `${source}-${target}`, source, target, type: "smoothstep", animated: source === "orchestrator-matter", data: { type: "executes" } }));

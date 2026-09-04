export type EvidenceStatus = "confirmed" | "inferred" | "proposed" | "unknown" | "deprecated";

export type ArchitectureNodeType =
  | "organization" | "department" | "matter" | "project" | "workflow"
  | "agent" | "skill" | "tool" | "rag" | "source" | "evidence"
  | "approval" | "human" | "model" | "database" | "queue" | "worker";

export interface EvidenceRef {
  path: string;
  lineStart?: number;
  lineEnd?: number;
  status: EvidenceStatus;
}

export interface ArchitectureNode {
  id: string;
  name: string;
  type: ArchitectureNodeType;
  status: EvidenceStatus;
  domain?: string;
  lane?: string;
  owner?: string;
  evidence?: EvidenceRef[];
  metadata?: Record<string, unknown>;
}

export interface ArchitectureEdge {
  id: string;
  source: string;
  target: string;
  type: "contains" | "triggers" | "calls" | "reads" | "writes" | "reviews" | "retrieves" | "approves" | "depends-on";
  status: EvidenceStatus;
  async?: boolean;
  condition?: string;
  evidence?: EvidenceRef[];
}

export interface ArchitectureGraph {
  schemaVersion: "1.0";
  id: string;
  name: string;
  status: EvidenceStatus;
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
}

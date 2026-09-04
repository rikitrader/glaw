export interface EvidenceGraphNode { id: string; type: string; label: string; }
export interface EvidenceGraphEdge { from: string; to: string; type: string; locator?: string; }
export interface EvidenceGraph { nodes: EvidenceGraphNode[]; edges: EvidenceGraphEdge[]; }

export function validateEvidenceGraph(graph: EvidenceGraph): string[] {
  const errors: string[] = [];
  const ids = new Set<string>();
  for (const node of graph.nodes) {
    if (!node.id || ids.has(node.id)) errors.push(`duplicate or empty graph node: ${node.id}`);
    ids.add(node.id);
  }
  for (const edge of graph.edges) {
    if (!ids.has(edge.from)) errors.push(`edge source node missing: ${edge.from}`);
    if (!ids.has(edge.to)) errors.push(`edge target node missing: ${edge.to}`);
    if (!edge.type) errors.push(`edge type missing: ${edge.from}->${edge.to}`);
  }
  return errors;
}

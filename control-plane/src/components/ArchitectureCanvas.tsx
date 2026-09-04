import { useMemo, useState } from "react";
import { Background, Controls, MiniMap, ReactFlow, Handle, Position, type Node, type Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./ArchitectureCanvas.css";

type ArchNode = { label: string; type: string; status: string; detail: string };

const nodeData: Record<string, ArchNode> = {
  intake: { label: "Intake", type: "TRIGGER", status: "confirmed", detail: "Public intake Worker" },
  matter: { label: "Matter", type: "MATTER", status: "confirmed", detail: "GLAW-LOCAL-001" },
  orchestrator: { label: "Matter Orchestrator", type: "AGENT", status: "proposed", detail: "Work plan + dependencies" },
  research: { label: "Legal Research", type: "AGENT", status: "confirmed", detail: "Authorized source search" },
  rag: { label: "Source-Locked RAG", type: "RAG", status: "confirmed", detail: "Lexical + citation graph" },
  red: { label: "Red / Blue Review", type: "GOVERNANCE", status: "proposed", detail: "Adversarial quality loop" },
  approval: { label: "Attorney Approval", type: "HUMAN", status: "proposed", detail: "Required high-risk gate" },
  output: { label: "Approved Output", type: "OUTPUT", status: "proposed", detail: "Versioned artifact + audit" }
};

function ArchNode({ data }: { data: ArchNode }) {
  return <div className={`arch-node ${data.status}`}><Handle type="target" position={Position.Left} /><span className="node-type">{data.type}</span><strong>{data.label}</strong><small>{data.detail}</small><span className="node-status">{data.status}</span><Handle type="source" position={Position.Right} /></div>;
}

export default function ArchitectureCanvas() {
  const [selected, setSelected] = useState("matter");
  const nodes = useMemo<Node[]>(() => Object.entries(nodeData).map(([id, data], index) => ({ id, position: { x: (index % 4) * 245, y: Math.floor(index / 4) * 150 }, data, type: "arch" })), []);
  const edges = useMemo<Edge[]>(() => [["intake", "matter"], ["matter", "orchestrator"], ["orchestrator", "research"], ["research", "rag"], ["rag", "red"], ["red", "approval"], ["approval", "output"]].map(([source, target]) => ({ id: `${source}-${target}`, source, target, animated: source === "matter", style: { stroke: "#d7a84b", strokeWidth: 1.5 } })), []);
  return <div className="canvas-wrap"><div className="canvas-toolbar"><span>CONFIRMED + PROPOSED / 8 nodes / 7 edges</span><button type="button">Horizontal flow</button><button type="button">Fit view</button></div><div className="canvas-body"><ReactFlow nodes={nodes} edges={edges} nodeTypes={{ arch: ArchNode }} fitView onNodeClick={(_, node) => setSelected(node.id)}><Background color="#31414a" gap={20} /><MiniMap nodeColor={(node) => node.id === selected ? "#d7a84b" : "#57c1b5"} /><Controls /></ReactFlow></div><aside className="canvas-inspector"><p className="eyebrow">SELECTED NODE</p><h3>{nodeData[selected].label}</h3><span className={`inspector-status ${nodeData[selected].status}`}>{nodeData[selected].status}</span><dl><dt>Type</dt><dd>{nodeData[selected].type}</dd><dt>Detail</dt><dd>{nodeData[selected].detail}</dd><dt>Upstream</dt><dd>{selected === "matter" ? "Intake" : "Inspectable from graph"}</dd><dt>Evidence</dt><dd>{nodeData[selected].status === "confirmed" ? "Repository-backed" : "Target architecture"}</dd></dl><a href="/architecture">Open full inspector →</a></aside></div>;
}

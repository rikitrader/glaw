import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { addEdge, Background, Controls, MiniMap, ReactFlow, ReactFlowProvider, useEdgesState, useNodesState, useReactFlow, Handle, Position, type Connection, type Edge, type Node, type NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { demoEdges, demoNodes, NODE_BY_TYPE, NODE_REGISTRY, createStudioNode, type StudioCategory, type StudioNodeData, type StudioNodeType, type StudioStatus } from "../lib/workflows/node-registry";
import { validateConnection, validateGraph, type ValidationFinding } from "../lib/workflows/validator";
import { getGovernedCatalog } from "../lib/workflows/governed-catalog";
import StudioReviewRail from "./StudioReviewRail";
import "./WorkflowStudio.css";

function StudioNode({ data, selected, id }: NodeProps<Node<StudioNodeData>>) {
  const risk = String(data.config?.riskClass ?? (data.type === "human-approval" || data.type === "external-api" ? "HIGH" : data.type === "agent" || data.type === "model" ? "MODERATE" : "LOW"));
  const adapter = data.type === "adapter" || data.type === "external-api" ? "BOUNDARY" : String(data.config?.adapter ?? "GLAW");
  return <div className={`studio-node status-${data.status} node-type-${data.type} ${selected ? "selected" : ""}`} role="button" tabIndex={0} aria-label={`${data.label}, ${data.type}, ${risk} risk, ${data.status}. Press Enter to inspect.`} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); window.dispatchEvent(new CustomEvent("glaw:select-node", { detail: { id } })); } }}><Handle type="target" position={Position.Left} /><div className="studio-node-top"><span className="node-icon" aria-hidden="true">{NODE_BY_TYPE[data.type].icon}</span><span className="node-category">{data.category}</span><span className="node-status-dot" aria-hidden="true" /></div><strong>{data.label}</strong><small>{data.description}</small><div className="node-chips"><span className={`node-chip risk-${risk.toLowerCase()}`}>{risk}</span><span className="node-chip adapter-chip">{adapter}</span></div><div className="studio-node-footer"><span>{data.status}</span><span>{data.type}</span></div><Handle type="source" position={Position.Right} /></div>;
}

const nodeTypes = { studio: StudioNode };
const categories: StudioCategory[] = ["Organization", "AI", "Capabilities", "Knowledge", "Models", "Workflow", "Infrastructure"];
type StudioContext = { tenantId: string; clientId?: string; matterId: string; workflowId: string; policyVersion: string; environment: "sandbox" | "staging" | "production"; revision: number; actorId: string; role: string; token?: string };
type AssistantProposal = { type: StudioNodeType; label: string; summary: string; risk: string; beforeNodes: number; beforeEdges: number };

function StudioInner() {
  const wrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition, fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState<StudioNodeData>(demoNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(demoEdges);
  const [selectedId, setSelectedId] = useState("agent-research");
  const [search, setSearch] = useState("");
  const [paletteOpen, setPaletteOpen] = useState(true);
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [assistantPrompt, setAssistantPrompt] = useState("");
  const [findings, setFindings] = useState<ValidationFinding[]>([]);
  const [history, setHistory] = useState<{ nodes: Node<StudioNodeData>[]; edges: Edge[] }[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [studioContext, setStudioContext] = useState<StudioContext | null>(null);
  const [persistenceState, setPersistenceState] = useState<"DESIGN_SANDBOX" | "LOCAL_RECOVERY" | "SAVED_SERVER" | "SAVING" | "CONFLICT" | "OFFLINE" | "APPROVAL_PENDING" | "DRY_RUN_PREPARED" | "VALIDATION_BLOCKED">("DESIGN_SANDBOX");
  const [activeTab, setActiveTab] = useState<"validation" | "runs" | "red-team" | "blue-team" | "approvals" | "logs" | "adapters">("validation");
  const [moreOpen, setMoreOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [assistantProposal, setAssistantProposal] = useState<AssistantProposal | null>(null);
  const [conflictMessage, setConflictMessage] = useState<string | null>(null);
  const [adapterReadiness, setAdapterReadiness] = useState<Array<{ id: string; name: string; health: string; note?: string }>>([]);
  const [graphView, setGraphView] = useState<"canvas" | "critical" | "swimlane" | "list">("canvas");
  const selected = nodes.find((node) => node.id === selectedId) ?? nodes[0];
  const criticalPathIds = useMemo(() => {
    const outgoing = new Map<string, string[]>(); const incoming = new Set<string>();
    edges.forEach((edge) => { outgoing.set(edge.source, [...(outgoing.get(edge.source) ?? []), edge.target]); incoming.add(edge.target); });
    const roots = nodes.filter((node) => !incoming.has(node.id)).map((node) => node.id);
    const targets = new Set(nodes.filter((node) => ["output", "external-api", "payment-gate", "human-approval"].includes(node.data.type)).map((node) => node.id));
    const queue = [...roots]; const parent = new Map<string, string>(); let target = "";
    while (queue.length) { const current = queue.shift()!; if (targets.has(current)) { target = current; break; } for (const next of outgoing.get(current) ?? []) if (!parent.has(next) && !roots.includes(next)) { parent.set(next, current); queue.push(next); } }
    if (!target) target = [...nodes].find((node) => !(outgoing.get(node.id)?.length))?.id ?? roots[0] ?? "";
    const path = new Set<string>(); let current = target; while (current) { path.add(current); current = parent.get(current) ?? ""; }
    return path;
  }, [edges, nodes]);
  const catalog = useMemo(() => getGovernedCatalog(), []);
  const governedLabel = (kind: "persona" | "skill" | "adapter" | "pack", id: unknown) => {
    if (typeof id !== "string") return "Not bound";
    const collection = catalog[`${kind}s` as "personas" | "skills" | "adapters" | "packs"] as Array<{ id: string; name: string }>;
    return collection.find((item) => item.id === id)?.name ?? `Unknown · ${id}`;
  };

  useEffect(() => {
    const context = (window as Window & { __GLAW_CONTEXT__?: StudioContext }).__GLAW_CONTEXT__;
    if (!context?.tenantId || !context.matterId || !context.workflowId || !context.policyVersion) return;
    setStudioContext(context);
    const authHeaders: Record<string, string> = { "x-glaw-tenant-id": context.tenantId, "x-glaw-actor-id": context.actorId, "x-glaw-role": context.role };
    if (context.token) authHeaders.authorization = `Bearer ${context.token}`;
    const loadSnapshot = async () => fetch(`/api/workflows/${encodeURIComponent(context.workflowId)}/snapshot`, { headers: authHeaders }).then(async (response) => {
      if (!response.ok) throw new Error("snapshot unavailable");
      const body = await response.json() as { snapshot?: { revision: number; definition: { nodes?: unknown[]; edges?: unknown[] } } };
      const snapshot = body.snapshot;
      if (!snapshot) throw new Error("snapshot missing");
      if (Array.isArray(snapshot.definition.nodes) && Array.isArray(snapshot.definition.edges)) { setNodes(snapshot.definition.nodes as Node<StudioNodeData>[]); setEdges(snapshot.definition.edges as Edge[]); setSelectedId((snapshot.definition.nodes[0] as Node<StudioNodeData> | undefined)?.id ?? ""); setStudioContext((current) => current ? { ...current, revision: snapshot.revision } : current); setPersistenceState("SAVED_SERVER"); }
    });
    void loadSnapshot().catch(() => setFindings([{ id: "snapshot-load", severity: "warning", message: "Authoritative snapshot could not be loaded; editing remains blocked to the design sandbox." }]));
    void fetch("/api/connectors/readiness", { headers: authHeaders }).then((response) => response.ok ? response.json() as Promise<{ adapters?: Array<{ id: string; name: string; health: string; note?: string }> }> : Promise.reject(new Error("readiness unavailable"))).then((body) => setAdapterReadiness(body.adapters ?? [])).catch(() => setAdapterReadiness([]));
    const selectNode = (event: Event) => { const detail = (event as CustomEvent<{ id?: string }>).detail; if (detail?.id) { setSelectedId(detail.id); setInspectorOpen(true); setPaletteOpen(false); } };
    window.addEventListener("glaw:select-node", selectNode);
    return () => window.removeEventListener("glaw:select-node", selectNode);
  }, [setEdges, setNodes]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.matches("input, textarea, select")) return;
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "z") { event.preventDefault(); undo(); return; }
      if (event.key === "Delete" || event.key === "Backspace") { if (selected) { event.preventDefault(); deleteSelected(); } return; }
      if (event.key.toLowerCase() === "v") runValidation();
      const tabs = ["validation", "runs", "red-team", "blue-team", "approvals", "logs", "adapters"] as const;
      const index = Number(event.key) - 1;
      if (index >= 0 && index < tabs.length) setActiveTab(tabs[index]);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  });

  const checkpoint = useCallback(() => {
    setHistory((items) => [...items.slice(0, historyIndex + 1), { nodes, edges }]);
    setHistoryIndex((index) => index + 1);
  }, [edges, historyIndex, nodes]);

  const onConnect = useCallback((connection: Connection) => {
    const source = nodes.find((node) => node.id === connection.source); const target = nodes.find((node) => node.id === connection.target);
    if (!source || !target) return;
    const result = validateConnection(source.data.type, target.data.type);
    if (!result.valid) { setFindings([{ id: "connection-rejected", severity: "error", message: result.message }]); return; }
    checkpoint();
    setEdges((current) => addEdge({ ...connection, type: "smoothstep", data: { type: "executes" } }, current));
    setFindings([]);
  }, [checkpoint, nodes, setEdges]);

  const addNode = useCallback((type: StudioNodeType, position?: { x: number; y: number }) => {
    checkpoint();
    const id = `${type}-${crypto.randomUUID().slice(0, 8)}`;
    const next = createStudioNode(type, id, position ?? { x: 240 + nodes.length * 20, y: 180 + (nodes.length % 5) * 45 });
    setNodes((current) => [...current, next]); setSelectedId(id); setInspectorOpen(true);
  }, [checkpoint, nodes.length, setNodes]);

  const onDrop = useCallback((event: React.DragEvent) => { event.preventDefault(); const type = event.dataTransfer.getData("application/glaw-node") as StudioNodeType; if (!type || !wrapper.current) return; addNode(type, screenToFlowPosition({ x: event.clientX, y: event.clientY })); }, [addNode, screenToFlowPosition]);
  const filtered = useMemo(() => NODE_REGISTRY.filter((item) => !search || `${item.label} ${item.category} ${item.description}`.toLowerCase().includes(search.toLowerCase())), [search]);
  const runValidation = () => setFindings([...validateGraph(nodes, edges), { id: "critical-path", severity: "info", message: `Computed critical path contains ${criticalPathIds.size} node(s) to the next governed effect.` }]);
  const updateSelected = (key: string, value: string) => { if (!selected) return; checkpoint(); setNodes((current) => current.map((node) => node.id === selected.id ? { ...node, data: { ...node.data, [key]: value } } : node)); };
  const updateSelectedConfig = (key: string, value: string) => { if (!selected) return; checkpoint(); setNodes((current) => current.map((node) => node.id === selected.id ? { ...node, data: { ...node.data, config: { ...node.data.config, [key]: value } } } : node)); };
  const undo = () => { if (historyIndex < 0) return; const previous = history[historyIndex]; setNodes(previous.nodes); setEdges(previous.edges); setHistoryIndex((index) => index - 1); };
  const duplicateSelected = () => { if (!selected) return; addNode(selected.data.type, { x: selected.position.x + 40, y: selected.position.y + 40 }); };
  const deleteSelected = () => { if (!selected) return; setDeleteConfirm(true); };
  const confirmDelete = () => { if (!selected) return; checkpoint(); setNodes((current) => current.filter((node) => node.id !== selected.id)); setEdges((current) => current.filter((edge) => edge.source !== selected.id && edge.target !== selected.id)); setSelectedId(nodes.find((node) => node.id !== selected.id)?.id ?? ""); setDeleteConfirm(false); };
  const persistLocalRecovery = () => { if (!studioContext) return false; const recoveryKey = `glaw:workflow-studio:recovery:${studioContext.tenantId}:${studioContext.matterId}:${studioContext.workflowId}`; window.localStorage.setItem(recoveryKey, JSON.stringify({ schemaVersion: "1.0", nodes, edges, savedAt: new Date().toISOString() })); setPersistenceState("LOCAL_RECOVERY"); return true; };
  const requestServerAction = async (action: "draft" | "publish" | "dry-run") => {
    if (!studioContext) { persistLocalRecovery(); setFindings([{ id: "scope-required", severity: "error", message: "DESIGN SANDBOX: resolve a tenant, matter, workflow, policy, and actor before saving to GLAW." }]); setPersistenceState("DESIGN_SANDBOX"); return; }
    setPersistenceState("SAVING"); setConflictMessage(null);
    const headers: Record<string, string> = { "content-type": "application/json", "x-glaw-tenant-id": studioContext.tenantId, "x-glaw-actor-id": studioContext.actorId, "x-glaw-role": studioContext.role };
    if (studioContext.token) headers.authorization = `Bearer ${studioContext.token}`;
    const endpoint = `/api/workflows/${encodeURIComponent(studioContext.workflowId)}/${action === "dry-run" ? "dry-run" : action}`;
    try {
      const response = await fetch(endpoint, { method: action === "draft" ? "PUT" : "POST", headers, body: JSON.stringify({ nodes, edges, expectedRevision: studioContext.revision, policyVersion: studioContext.policyVersion, environment: studioContext.environment }) });
      const result = await response.json() as { status?: string; findings?: ValidationFinding[]; revision?: number; error?: string };
      if (!response.ok) { const conflict = response.status === 409; setFindings(result.findings ?? [{ id: conflict ? "revision-conflict" : "server-action", severity: "error", message: result.error ?? "Server rejected the workflow action." }]); setPersistenceState(conflict ? "CONFLICT" : "VALIDATION_BLOCKED"); setConflictMessage(conflict ? "This workflow changed on the server. Reload the authoritative revision before applying local edits." : null); return; }
      setFindings(result.findings ?? []); setPersistenceState(action === "publish" ? "APPROVAL_PENDING" : action === "dry-run" ? "DRY_RUN_PREPARED" : "SAVED_SERVER");
      if (typeof result.revision === "number") setStudioContext((current) => current ? { ...current, revision: result.revision! } : current);
    } catch { setFindings([{ id: "server-unavailable", severity: "error", message: "GLAW server is unavailable; no authoritative workflow action was recorded." }]); setPersistenceState("OFFLINE"); }
  };
  const reloadSnapshot = async () => { if (!studioContext) return; const headers: Record<string, string> = { "x-glaw-tenant-id": studioContext.tenantId, "x-glaw-actor-id": studioContext.actorId, "x-glaw-role": studioContext.role }; if (studioContext.token) headers.authorization = `Bearer ${studioContext.token}`; const response = await fetch(`/api/workflows/${encodeURIComponent(studioContext.workflowId)}/snapshot`, { headers }); const body = await response.json() as { snapshot?: { revision: number; definition: { nodes?: unknown[]; edges?: unknown[] } } }; if (!response.ok || !body.snapshot) return; setNodes((body.snapshot.definition.nodes ?? []) as Node<StudioNodeData>[]); setEdges((body.snapshot.definition.edges ?? []) as Edge[]); setStudioContext((current) => current ? { ...current, revision: body.snapshot!.revision } : current); setConflictMessage(null); setPersistenceState("SAVED_SERVER"); setFindings([]); };
  const saveDraft = () => { void requestServerAction("draft"); };
  const publish = () => { const next = validateGraph(nodes, edges); if (next.some((item) => item.severity === "error")) { setFindings(next); setPersistenceState("VALIDATION_BLOCKED"); return; } void requestServerAction("publish"); };
  const testWorkflow = () => { const next = validateGraph(nodes, edges); if (next.some((item) => item.severity === "error")) { setFindings(next); setPersistenceState("VALIDATION_BLOCKED"); return; } void requestServerAction("dry-run"); };
  const autoLayout = () => { checkpoint(); setNodes((current) => current.map((node, index) => ({ ...node, position: { x: 80 + (Math.floor(index / 4) * 270), y: 70 + ((index % 4) * 145) } }))); setFindings([{ id: "layout-updated", severity: "info", message: "Canvas layout updated locally. Save draft to persist the revision." }]); };
  const sendAssistantPrompt = () => { const prompt = assistantPrompt.trim(); if (!prompt) return; const lower = prompt.toLowerCase(); const type: StudioNodeType = lower.includes("mcp") ? "mcp-adapter" : lower.includes("api") || lower.includes("dms") || lower.includes("court") ? "api-adapter" : lower.includes("approval") || lower.includes("lawyer") ? "human-approval" : lower.includes("skill") ? "skill" : lower.includes("red team") ? "red-team" : "agent"; const label = prompt.length > 42 ? `${prompt.slice(0, 39)}…` : prompt; setAssistantProposal({ type, label, summary: `Proposed ${NODE_BY_TYPE[type].label} from your request. No graph mutation has been applied.`, risk: ["human-approval", "api-adapter", "mcp-adapter"].includes(type) ? "HIGH" : "MODERATE", beforeNodes: nodes.length, beforeEdges: edges.length }); setAssistantPrompt(""); };
  const applyAssistantProposal = () => { if (!assistantProposal) return; addNode(assistantProposal.type); setFindings([{ id: "assistant-applied", severity: "info", message: `Assistant diff applied locally: nodes ${assistantProposal.beforeNodes} → ${assistantProposal.beforeNodes + 1}; connections ${assistantProposal.beforeEdges} → ${assistantProposal.beforeEdges}. Validate and save before any server action.` }]); setAssistantProposal(null); };

  return <div className="studio" ref={wrapper}>
    <header className="studio-toolbar"><div className="studio-title"><span className="studio-mark">✣</span><div><strong>{studioContext?.workflowId ?? "Litigation Analysis"}</strong><small>{studioContext ? `${studioContext.environment} · revision ${studioContext.revision} · policy ${studioContext.policyVersion}` : "DESIGN SANDBOX · scope unresolved"}</small></div></div><div className="breadcrumbs"><span>{studioContext?.tenantId ?? "Tenant unresolved"}</span><b>›</b><span>{studioContext?.matterId ?? "Matter unresolved"}</span><b>›</b><strong>{studioContext ? "Connected scope" : "Local canvas"}</strong></div><div className="studio-actions"><span className={`toolbar-status ${persistenceState === "DESIGN_SANDBOX" ? "sandbox" : ""}`}><i /> {persistenceState.replaceAll("_", " ")}</span><button type="button" aria-label="Undo last edit" onClick={undo} disabled={historyIndex < 0}>↶ Undo</button><button type="button" onClick={duplicateSelected}>Duplicate</button><button type="button" onClick={runValidation}>Validate</button><button type="button" className="save" onClick={saveDraft}>{studioContext ? "Save draft" : "Save recovery"}</button><button type="button" className="publish" onClick={publish}>{studioContext ? "Request publish" : "Publish unavailable"}</button></div></header>
    {conflictMessage && <div className="conflict-banner" role="alert"><strong>Concurrent edit detected</strong><span>{conflictMessage}</span><button type="button" onClick={() => void reloadSnapshot()}>Reload server revision</button></div>}
    <div className="studio-body">
      <aside className={`palette ${paletteOpen ? "open" : "closed"}`}><div className="panel-title"><div><span className="eyebrow">NODE PALETTE</span><strong>Add components</strong></div><button type="button" onClick={() => setPaletteOpen(false)}>‹</button></div><div className="palette-search"><span>⌕</span><input aria-label="Search nodes" placeholder="Search nodes..." value={search} onChange={(event) => setSearch(event.target.value)} /></div><div className="palette-list">{categories.map((category) => { const items = filtered.filter((item) => item.category === category); if (!items.length) return null; return <section className="palette-section" key={category}><p>{category}</p>{items.map((item) => <button type="button" draggable onDragStart={(event) => event.dataTransfer.setData("application/glaw-node", item.type)} onClick={() => addNode(item.type)} key={item.type}><span className="palette-icon">{item.icon}</span><span><strong>{item.label}</strong><small>{item.description}</small></span><b>＋</b></button>)}</section>; })}</div></aside>
      <section className="studio-canvas"><div className="canvas-modebar"><span className="canvas-count"><b>{graphView === "critical" ? "CRITICAL PATH" : graphView === "swimlane" ? "SWIMLANE" : "CANVAS"}</b> {nodes.length} nodes · {edges.length} connections · rev {studioContext?.revision ?? "local"}</span><div className="canvas-legend"><span><i className="legend-dot live" /> Executing</span><span><i className="legend-dot adapter" /> Adapter</span><span><i className="legend-dot gate" /> Human gate</span></div><button type="button" aria-label="Fit workflow in canvas" onClick={() => fitView({ padding: .2, duration: 300 })}>Fit view</button><button type="button" onClick={autoLayout}>Auto layout</button><button type="button" aria-pressed={graphView === "critical"} onClick={() => setGraphView(graphView === "critical" ? "canvas" : "critical")}>Critical path</button><button type="button" aria-pressed={graphView === "swimlane"} onClick={() => setGraphView(graphView === "swimlane" ? "canvas" : "swimlane")}>Swimlanes</button><div className="canvas-more"><button type="button" aria-label="More canvas actions" aria-expanded={moreOpen} onClick={() => setMoreOpen((open) => !open)}>⋯</button>{moreOpen && <div className="canvas-menu"><button type="button" onClick={() => { setFindings([]); setMoreOpen(false); }}>Clear findings</button><button type="button" onClick={() => { setPaletteOpen(true); setInspectorOpen(true); setMoreOpen(false); }}>Show panels</button></div>}</div></div><div className={`flow-area graph-${graphView}`} onDrop={onDrop} onDragOver={(event) => event.preventDefault()}><ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} onNodesChange={(changes) => { onNodesChange(changes); }} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeClick={(_, node) => { setSelectedId(node.id); setInspectorOpen(true); setPaletteOpen(false); }} onPaneClick={() => setFindings([])} fitView onlyRenderVisibleElements><Background color="#d7dfea" gap={22} size={1} /><MiniMap pannable zoomable nodeColor={(node) => node.id === selectedId ? "#206bff" : node.type === "studio" && (node.data as StudioNodeData).type === "adapter" ? "#f79009" : "#12b76a"} /><Controls /></ReactFlow>{graphView === "swimlane" && <div className="swimlane-overlay" aria-label="Workflow swimlanes"><span>ORCHESTRATION</span><span>RESEARCH & EVIDENCE</span><span>REVIEW & APPROVAL</span><span>DELIVERY</span></div>}{!nodes.length && <div className="canvas-empty"><span>＋</span><strong>Drop a node to start the workflow</strong><small>Drag components from the palette into this canvas.</small></div>}</div></section>
      <aside className={`inspector ${inspectorOpen ? "open" : "closed"}`}>
        <div className="assistant-header"><span className="assistant-spark">✣</span><div><strong>Design Assistant</strong><small>Describe a change and I’ll propose a reviewable patch</small></div><button type="button" aria-label="Close inspector" onClick={() => setInspectorOpen(false)}>›</button></div>
        <div className="assistant-message"><strong>Hi! Build a defensible legal workflow.</strong><p>I can help you add agents, route matters, connect sources, and enforce attorney-review gates.</p><p><strong>Try this workflow</strong> to preview the current graph, or describe a change below.</p></div>
        <div className="assistant-hint"><strong>Hint:</strong> Select any node to edit its configuration and inspect its connections.</div>
        <button type="button" className="test-workflow" onClick={testWorkflow}><span>▷</span> Prepare dry run</button>
        <textarea className="assistant-input" aria-label="Describe your workflow changes" placeholder="Describe your workflow changes..." value={assistantPrompt} onChange={(event) => setAssistantPrompt(event.target.value)} />
        <button type="button" className="assistant-send" onClick={sendAssistantPrompt}>Propose change <span>➤</span></button>
        {assistantProposal && <div className="proposal-card"><p className="eyebrow">PROPOSED PATCH · NOT APPLIED</p><strong>{assistantProposal.label}</strong><small>{assistantProposal.summary}</small><div><span className="node-chip risk-high">{assistantProposal.risk}</span><span className="node-chip adapter-chip">{assistantProposal.type}</span></div><div className="proposal-actions"><button type="button" onClick={() => setAssistantProposal(null)}>Discard</button><button type="button" className="approve" onClick={applyAssistantProposal}>Apply local patch</button></div></div>}
        {selected && <div className="selected-config"><div className="selected-config-title"><span className="eyebrow">SELECTED NODE</span><strong>{selected.data.label}</strong></div><div className="binding-card"><p className="eyebrow">GOVERNED BINDINGS</p>{["agent", "red-team", "blue-team", "persona"].includes(selected.data.type) && <label>Persona<select value={String(selected.data.config.personaId ?? "")} onChange={(event) => updateSelectedConfig("personaId", event.target.value)}><option value="">Select governed persona</option>{catalog.personas.map((item) => <option value={item.id}>{item.name} · {item.kind}</option>)}</select></label>}{["skill"].includes(selected.data.type) && <label>Skill<select value={String(selected.data.config.skillId ?? "")} onChange={(event) => updateSelectedConfig("skillId", event.target.value)}><option value="">Select signed skill</option>{catalog.skills.map((item) => <option value={item.id}>{item.name} · v{item.version}</option>)}</select></label>}{["adapter", "mcp-adapter", "api-adapter", "payment-gate"].includes(selected.data.type) && <label>Adapter<select value={String(selected.data.config.adapterId ?? "")} onChange={(event) => updateSelectedConfig("adapterId", event.target.value)}><option value="">Select adapter</option>{catalog.adapters.map((item) => <option value={item.id}>{item.name} · {item.protocol}</option>)}</select></label>}{["jurisdiction-pack", "practice-pack"].includes(selected.data.type) && <label>Pack<select value={String(selected.data.config.packId ?? "")} onChange={(event) => updateSelectedConfig("packId", event.target.value)}><option value="">Select versioned pack</option>{catalog.packs.map((item) => <option value={item.id}>{item.name} · v{item.version}</option>)}</select></label>}{selected.data.config.personaId && <div><span>Persona</span><strong>{governedLabel("persona", selected.data.config.personaId)}</strong></div>}{selected.data.config.skillId && <div><span>Skill</span><strong>{governedLabel("skill", selected.data.config.skillId)} · signed</strong></div>}{selected.data.config.adapterId && <div><span>Adapter</span><strong>{governedLabel("adapter", selected.data.config.adapterId)}</strong></div>}{selected.data.config.packId && <div><span>Pack</span><strong>{governedLabel("pack", selected.data.config.packId)}</strong></div>}{selected.data.type === "payment-gate" && <div><span>Payment</span><strong>x402 · legal authority separate</strong></div>}</div><label>Name<input value={selected.data.label} onChange={(event) => updateSelected("label", event.target.value)} /></label><label>Design state<select value={String(selected.data.config.designState ?? "enabled")} onChange={(event) => updateSelectedConfig("designState", event.target.value)}><option value="enabled">enabled</option><option value="disabled">disabled</option><option value="draft">draft</option></select></label><label>Description<textarea value={selected.data.description} onChange={(event) => updateSelected("description", event.target.value)} /></label><div className="inspector-section"><p className="eyebrow">CONNECTIONS</p><div className="inspector-row"><span>Inputs</span><strong>{selected.data.type === "agent" ? "task / context / evidence" : "context"}</strong></div><div className="inspector-row"><span>Outputs</span><strong>result / issues</strong></div></div><button type="button" className="danger-button" onClick={deleteSelected}>Delete node</button></div>}
      </aside>
    </div>
    {deleteConfirm && selected && <div className="modal-backdrop" role="presentation"><div className="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="delete-title"><p className="eyebrow">DESTRUCTIVE DESIGN CHANGE</p><h2 id="delete-title">Delete {selected.data.label}?</h2><p>This removes the node and its {edges.filter((edge) => edge.source === selected.id || edge.target === selected.id).length} connection(s). Validate again before any server save.</p><div className="modal-actions"><button type="button" onClick={() => setDeleteConfirm(false)}>Cancel</button><button type="button" className="danger-button" onClick={confirmDelete}>Delete node</button></div></div></div>}
    <StudioReviewRail activeTab={activeTab} onTabChange={setActiveTab} findings={findings} persistenceState={persistenceState} context={studioContext} />
  </div>;
}

export default function WorkflowStudio() { return <ReactFlowProvider><StudioInner /></ReactFlowProvider>; }

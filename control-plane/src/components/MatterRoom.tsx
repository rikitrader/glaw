import { useEffect, useState } from "react";
import "./MatterRoom.css";

type Stage = { id: string; label: string; state: "complete" | "active" | "blocked" | "queued"; detail: string };

const stages: Stage[] = [
  { id: "01", label: "Intake", state: "complete", detail: "Matter and party scope resolved" },
  { id: "02", label: "Conflict check", state: "complete", detail: "No blocking conflict found" },
  { id: "03", label: "Research swarm", state: "complete", detail: "12 authorities / 4 jurisdictions" },
  { id: "04", label: "Evidence ledger", state: "active", detail: "5 verified / 1 contrary source" },
  { id: "05", label: "Draft", state: "active", detail: "Motion outline ready for review" },
  { id: "06", label: "Red team", state: "queued", detail: "Awaiting draft candidate" },
  { id: "07", label: "Blue team", state: "queued", detail: "Remediation follows red team" },
  { id: "08", label: "Attorney gate", state: "blocked", detail: "Required before release" }
];

const agents = [
  ["Research Agent", "12 authorities found", "complete"],
  ["Evidence Agent", "1 contradiction open", "active"],
  ["Draft Agent", "Motion outline ready", "active"],
  ["Citation Agent", "6 / 6 references bound", "complete"]
];

const evidence = [
  ["EVD-0042", "N.Y. CPLR § 3211", "Binding authority", "Verified", "p. 4 · ¶ 2"],
  ["EVD-0043", "Matter chronology", "Client-provided fact", "Review", "Fact ledger"],
  ["EVD-0044", "Contrary authority search", "Contrary authority", "Verified", "3 cases"],
  ["EVD-0045", "Precedent motion", "Firm precedent", "Verified", "v3 · hash bound"]
];

export default function MatterRoom() {
  const [tab, setTab] = useState("overview");
  const [selectedEvidence, setSelectedEvidence] = useState(evidence[0][0]);
  const [snapshot, setSnapshot] = useState<{ tasks?: Array<{ task_key: string; state: string; assigned_agent?: string }>; evidence?: Array<{ id: string; source_id: string; validation_state: string; privilege_class: string }>; claims?: Array<{ id: string; proposition: string; status: string }> } | null>(null);
  const [freshness, setFreshness] = useState("static baseline");
  useEffect(() => { fetch("/api/matters/matter-local-001/snapshot", { credentials: "include" }).then((response) => response.ok ? response.json() : null).then((body) => { if (body?.ok) { setSnapshot(body); setFreshness("verified live snapshot"); } }).catch(() => setFreshness("snapshot unavailable")); }, []);

  return <div className="matter-room">
    <div className="room-tabs" role="tablist" aria-label="Matter views">
      {[["overview", "Overview"], ["evidence", "Evidence"], ["agents", "Agents"], ["activity", "Activity"]].map(([id, label]) => <button type="button" role="tab" aria-selected={tab === id} className={tab === id ? "selected" : ""} onClick={() => setTab(id)} key={id}>{label}</button>)}
      <span className="room-live"><i /> LIVE SNAPSHOT · 4m</span>
    </div>

    {tab === "overview" && <>
      <section className="room-grid room-top-grid">
        <article className="room-panel workflow-panel"><div className="room-panel-head"><div><p className="eyebrow">GOVERNED WORKFLOW / V1.0.0</p><h2>Motion analysis spine</h2></div><span className="pill warn">IN REVIEW</span></div><div className="stage-list">{stages.map((stage) => <div className={`stage-row ${stage.state}`} key={stage.id}><span className="stage-index">{stage.id}</span><span className="stage-mark" aria-hidden="true">{stage.state === "complete" ? "✓" : stage.state === "blocked" ? "!" : stage.state === "active" ? "•" : "—"}</span><div><strong>{stage.label}</strong><small>{stage.detail}</small></div><span className="stage-state">{stage.state}</span></div>)}</div></article>
        <article className="room-panel"><div className="room-panel-head"><div><p className="eyebrow">MATTER BRIEF</p><h2>What is known</h2></div><span className="trust-chip">SOURCE-LOCKED</span></div><div className="brief-block"><span className="brief-label">OBJECTIVE</span><p>Assess dismissal posture and produce a reviewable motion outline grounded in the matter record and binding New York authority.</p></div><div className="brief-block"><span className="brief-label">OPEN QUESTION</span><p className="warning-copy">Whether the chronology supports notice before the alleged breach. Evidence Agent is searching contrary facts.</p></div><div className="brief-footer"><span>Evidence coverage</span><strong>83%</strong><div className="progress"><i style={{ width: "83%" }} /></div></div></article>
      </section>
      <section className="room-grid room-bottom-grid">
        <article className="room-panel"><div className="room-panel-head"><div><p className="eyebrow">SHARED AGENT TEAM</p><h2>Collaborative execution</h2></div><span className="mono">{freshness}</span></div><div className="agent-list">{(snapshot?.tasks?.length ? snapshot.tasks.map((task) => [task.assigned_agent ?? "Unassigned", `${task.task_key} · ${task.state.toLowerCase()}`, task.state === "QUEUED" ? "active" : "complete"] as [string, string, string]) : agents).map(([name, detail, state]) => <div className="agent-row" key={`${name}-${detail}`}><span className={`agent-avatar ${state}`}>{name.slice(0, 1)}</span><div><strong>{name}</strong><small>{detail}</small></div><span className={`agent-state ${state}`}>{state === "complete" ? "done" : "working"}</span></div>)}</div></article>
        <article className="room-panel"><div className="room-panel-head"><div><p className="eyebrow">RELEASE GATES</p><h2>Trust status</h2></div><a href="/governance">Policy →</a></div><div className="gate-list"><div><span className="gate-icon good">✓</span><div><strong>Conflict and privilege</strong><small>Passed · matter scope confirmed</small></div></div><div><span className="gate-icon good">✓</span><div><strong>Citation validation</strong><small>Passed · 6 references bound</small></div></div><div><span className="gate-icon warn">!</span><div><strong>Human approval</strong><small>Required · no external action enabled</small></div></div></div></article>
      </section>
    </>}

    {tab === "evidence" && <section className="room-grid evidence-view"><article className="room-panel"><div className="room-panel-head"><div><p className="eyebrow">EVIDENCE LEDGER</p><h2>Trace every conclusion</h2></div><span className="mono">{snapshot?.evidence?.length ?? 4} visible</span></div><div className="evidence-list">{(snapshot?.evidence?.length ? snapshot.evidence.map((item) => [item.id, item.source_id, item.privilege_class, item.validation_state, "live record"] as string[]) : evidence).map((item) => <button type="button" className={`evidence-row ${selectedEvidence === item[0] ? "selected" : ""}`} onClick={() => setSelectedEvidence(item[0])} key={item[0]}><span className="evidence-id">{item[0]}</span><span><strong>{item[1]}</strong><small>{item[2]} · {item[4]}</small></span><span className={`pill ${item[3] === "VERIFIED" || item[3] === "Verified" ? "good" : "warn"}`}>{item[3]}</span></button>)}</div></article><article className="room-panel evidence-detail"><p className="eyebrow">SELECTED EVIDENCE / {selectedEvidence}</p><h2>Exact source passage</h2><blockquote>“The source passage is displayed with its authority, privilege, version, page, and document hash before it can support a material claim.”</blockquote><div className="source-meta"><span>Source version <strong>3</strong></span><span>Page <strong>4</strong></span><span>Hash <strong>…8f2c</strong></span></div><div className="evidence-note"><strong>Why it matters</strong><p>{snapshot?.claims?.[0]?.proposition ?? "Bound to the selected matter claim and review history."}</p></div></article></section>}

    {tab === "agents" && <section className="room-panel activity-panel"><div className="room-panel-head"><div><p className="eyebrow">AGENT COLLABORATION</p><h2>Bounded agents, shared evidence</h2></div><span className="pill good">4 scoped agents</span></div><div className="agent-cards">{agents.map(([name, detail, state]) => <div className="agent-card" key={name}><span className={`agent-avatar ${state}`}>{name.slice(0, 1)}</span><h3>{name}</h3><p>{detail}</p><span className={`agent-state ${state}`}>{state === "complete" ? "Completed" : "In progress"}</span><small>Permissions: matter.read · evidence.write</small></div>)}</div></section>}

    {tab === "activity" && <section className="room-panel activity-panel"><div className="room-panel-head"><div><p className="eyebrow">IMMUTABLE ACTIVITY</p><h2>Execution history</h2></div><a href="/api/audit/export?matterId=matter-local-001">Export signed audit →</a></div><div className="timeline"><div><b>NOW</b><span className="timeline-dot warn" /><p><strong>Human approval gate opened</strong><small>Draft is held; no external side effect authorized.</small></p></div><div><b>4m</b><span className="timeline-dot good" /><p><strong>Citation validation completed</strong><small>6 citations bound to source versions and spans.</small></p></div><div><b>11m</b><span className="timeline-dot info" /><p><strong>Contrary authority search completed</strong><small>One contrary source added to the evidence ledger.</small></p></div><div><b>18m</b><span className="timeline-dot good" /><p><strong>Matter scope verified</strong><small>Tenant, client, matter, conflict, and policy resolved.</small></p></div></div></section>}
  </div>;
}

import { useEffect, useMemo, useState } from "react";
import type { ValidationFinding } from "../lib/workflows/validator";
import "./StudioReviewRail.css";

type StudioContext = { tenantId: string; matterId: string; workflowId: string; actorId: string; role: string; token?: string };
type Tab = "validation" | "runs" | "red-team" | "blue-team" | "approvals" | "logs" | "adapters";
type Props = { activeTab: Tab; onTabChange: (tab: Tab) => void; findings: ValidationFinding[]; persistenceState: string; context: StudioContext | null };
type PanelState = { loading: boolean; error?: string; items: Array<Record<string, unknown>>; freshness?: string };

const empty: PanelState = { loading: false, items: [] };

export default function StudioReviewRail({ activeTab, onTabChange, findings, persistenceState, context }: Props) {
  const [panel, setPanel] = useState<PanelState>(empty);
  const [decisionBusy, setDecisionBusy] = useState<string | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<Record<string, unknown> | null>(null);
  const tabs: Tab[] = ["validation", "runs", "red-team", "blue-team", "approvals", "logs", "adapters"];
  const labels: Record<Tab, string> = { validation: "Validation", runs: "Runs", "red-team": "Red Team", "blue-team": "Blue Team", approvals: "Approvals", logs: "Logs", adapters: "Adapters" };
  const authHeaders = useMemo(() => {
    if (!context) return {};
    const headers: Record<string, string> = { "x-glaw-tenant-id": context.tenantId, "x-glaw-actor-id": context.actorId, "x-glaw-role": context.role };
    if (context.token) headers.authorization = `Bearer ${context.token}`;
    return headers;
  }, [context]);

  useEffect(() => {
    if (activeTab === "validation" || !context) { setPanel(empty); return; }
    const endpoint = activeTab === "runs" ? `/api/workflows/runs?matterId=${encodeURIComponent(context.matterId)}` : activeTab === "approvals" ? `/api/approvals?matterId=${encodeURIComponent(context.matterId)}` : activeTab === "logs" ? `/api/audit/events?matterId=${encodeURIComponent(context.matterId)}` : activeTab === "red-team" || activeTab === "blue-team" ? `/api/workflows/reviews?matterId=${encodeURIComponent(context.matterId)}&workflowId=${encodeURIComponent(context.workflowId)}&team=${activeTab === "red-team" ? "RED_TEAM" : "BLUE_TEAM"}` : `/api/connectors/readiness`;
    setPanel({ loading: true, items: [] });
    void fetch(endpoint, { headers: authHeaders }).then(async (response) => {
      const body = await response.json() as Record<string, unknown>;
      if (!response.ok) throw new Error(String(body.error ?? "Panel data could not be loaded"));
      const items = (body.runs ?? body.approvals ?? body.events ?? body.reviews ?? body.adapters ?? []) as Array<Record<string, unknown>>;
      setPanel({ loading: false, items, freshness: String(body.freshness ?? new Date().toISOString()) });
    }).catch((error) => setPanel({ loading: false, items: [], error: error instanceof Error ? error.message : "Panel data could not be loaded" }));
  }, [activeTab, authHeaders, context]);

  const decide = async (id: string, decision: "approve" | "reject") => {
    if (!context) return;
    setDecisionBusy(id);
    try {
      const response = await fetch(`/api/approvals/${encodeURIComponent(id)}`, { method: "POST", headers: { ...authHeaders, "content-type": "application/json" }, body: JSON.stringify({ decision, note: `Decision made in Workflow Studio: ${decision}` }) });
      if (!response.ok) throw new Error("approval decision was rejected");
      setPanel((current) => ({ ...current, items: current.items.map((item) => item.id === id ? { ...item, status: decision === "approve" ? "approved" : "rejected" } : item) }));
    } catch (error) { setPanel((current) => ({ ...current, error: error instanceof Error ? error.message : "approval decision failed" })); }
    finally { setDecisionBusy(null); }
  };

  return <footer className="studio-bottom"><div className="bottom-tabs" role="tablist" aria-label="Workflow review panels">{tabs.map((tab) => <button className={activeTab === tab ? "active" : ""} type="button" role="tab" aria-selected={activeTab === tab} aria-controls={`panel-${tab}`} onClick={() => onTabChange(tab)} key={tab}>{labels[tab]}{tab === "validation" && findings.length > 0 && <b>{findings.length}</b>}</button>)}</div><div className="review-panel" id={`panel-${activeTab}`} role="tabpanel" aria-live="polite">
    {activeTab === "validation" ? <ValidationPanel findings={findings} persistenceState={persistenceState} /> : !context ? <EmptyPanel message="Resolve an authenticated tenant, matter, workflow, policy, and actor scope to load authoritative data." /> : panel.loading ? <EmptyPanel message="Loading authoritative panel data…" /> : panel.error ? <div className="review-error"><strong>Panel unavailable</strong><span>{panel.error}</span></div> : activeTab === "approvals" ? <ApprovalPanel items={panel.items} busy={decisionBusy} selected={selectedApproval} onSelect={setSelectedApproval} onDecision={decide} /> : <DataPanel tab={activeTab} items={panel.items} freshness={panel.freshness} />}
  </div></footer>;
}

function ValidationPanel({ findings, persistenceState }: { findings: ValidationFinding[]; persistenceState: string }) { return <div className="validation-summary">{findings.length === 0 ? <><span className="ok-check">✓</span><span>Graph ready for validation</span><span className="muted">· {persistenceState.replaceAll("_", " ")}</span></> : findings.map((finding) => <span className={`finding ${finding.severity}`} key={finding.id}>{finding.severity.toUpperCase()} · {finding.message}</span>)}</div>; }
function EmptyPanel({ message }: { message: string }) { return <div className="review-empty"><span className="panel-mark">i</span><span>{message}</span></div>; }
function DataPanel({ tab, items, freshness }: { tab: Tab; items: Array<Record<string, unknown>>; freshness?: string }) { if (!items.length) return <EmptyPanel message={`No authoritative ${tab === "red-team" ? "Red Team" : tab === "blue-team" ? "Blue Team" : tab} records are available for this scope.`} />; return <div className="review-list">{items.map((item, index) => <article className="review-row" key={String(item.id ?? `${tab}-${index}`)}><div><strong>{String(item.event_type ?? item.workflow_id ?? item.connectorId ?? item.name ?? item.summary ?? "Record")}</strong><small>{String(item.state ?? item.status ?? item.health ?? item.severity ?? "UNKNOWN")} · {String(item.created_at ?? item.updated_at ?? item.freshness ?? "")}</small></div><span className="review-proof">Server record</span></article>)}{freshness && <small className="review-freshness">Freshness checked {freshness}</small>}</div>; }
function ApprovalPanel({ items, busy, selected, onSelect, onDecision }: { items: Array<Record<string, unknown>>; busy: string | null; selected: Record<string, unknown> | null; onSelect: (item: Record<string, unknown>) => void; onDecision: (id: string, decision: "approve" | "reject") => Promise<void> }) { if (!items.length) return <EmptyPanel message="No approval records are available for this matter." />; return <div className="approval-review-layout"><div className="review-list">{items.map((item) => { const id = String(item.id); const pending = String(item.status) === "pending"; return <article className={`review-row approval-row ${selected?.id === item.id ? "selected-review" : ""}`} key={id} tabIndex={0} role="button" onClick={() => onSelect(item)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onSelect(item); } }}><div><strong>Approval · {String(item.required_role ?? "reviewer")}</strong><small>{String(item.status ?? "UNKNOWN")} · {id}</small></div>{pending ? <div className="approval-actions"><button type="button" disabled={busy === id} onClick={(event) => { event.stopPropagation(); void onDecision(id, "reject"); }}>Reject</button><button type="button" className="approve" disabled={busy === id} onClick={(event) => { event.stopPropagation(); void onDecision(id, "approve"); }}>Approve</button></div> : <span className="review-proof">Decision recorded</span>}</article>; })}</div>{selected && <aside className="approval-detail" aria-label="Human approval review"><p className="eyebrow">HUMAN APPROVAL REVIEW</p><h3>{String(selected.required_role ?? "Reviewer")} decision</h3><dl><dt>Status</dt><dd>{String(selected.status ?? "UNKNOWN")}</dd><dt>Matter</dt><dd>{String(selected.matter_id ?? "Current matter")}</dd><dt>Workflow</dt><dd>{String(selected.workflow_id ?? "Current workflow")}</dd><dt>Created</dt><dd>{String(selected.created_at ?? "Unknown")}</dd></dl><p className="approval-note">This decision is sent to the server and recorded in the audit trail. Approval authorizes the configured workflow gate; it does not authorize unrelated legal or external actions.</p></aside>}</div>; }

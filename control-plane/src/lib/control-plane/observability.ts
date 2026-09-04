export type TraceContext = { traceId: string; matterId?: string; workflowId?: string; runId?: string; agentId?: string; commandId?: string };

export type LegalMetric = {
  name: string;
  value: number;
  unit: "count" | "milliseconds" | "usd" | "ratio";
  dimensions: Record<string, string>;
  recordedAt: string;
};

export type SloDefinition = {
  id: string;
  target: number;
  window: "1h" | "24h" | "7d" | "30d";
  indicator: "availability" | "latency" | "reconciliation" | "citation_accuracy" | "tenant_isolation";
};

export function metric(name: string, value: number, unit: LegalMetric["unit"], dimensions: Record<string, string> = {}): LegalMetric {
  return { name, value, unit, dimensions, recordedAt: new Date().toISOString() };
}

export const defaultSLOs: SloDefinition[] = [
  { id: "control-plane-availability", target: 0.999, window: "30d", indicator: "availability" },
  { id: "external-reconciliation", target: 0.999, window: "30d", indicator: "reconciliation" },
  { id: "citation-accuracy", target: 0.99, window: "30d", indicator: "citation_accuracy" },
  { id: "tenant-isolation", target: 1, window: "30d", indicator: "tenant_isolation" }
];

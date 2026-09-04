import type { LegalMetric, TraceContext } from "./observability";

export type TelemetryExporter = { export(spans: Array<{ name: string; context: TraceContext; durationMs: number; status: "OK" | "ERROR" }>, metrics: LegalMetric[]): Promise<void> };
export function redactTelemetryAttributes(attributes: Record<string, unknown>): Record<string, unknown> {
  const forbidden = /prompt|content|document|token|secret|email|quote|privilege/i;
  return Object.fromEntries(Object.entries(attributes).map(([key, value]) => [key, forbidden.test(key) ? "[REDACTED]" : value]));
}

export function createHttpTelemetryExporter(endpoint: string, fetcher: typeof fetch = fetch): TelemetryExporter {
  return { export: async (spans, metrics) => { if (!/^https:\/\//.test(endpoint)) throw new Error("telemetry endpoint must use HTTPS"); const response = await fetcher(endpoint, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ spans, metrics }) }); if (!response.ok) throw new Error(`telemetry export failed: ${response.status}`); } };
}

export type ModelRequest = {
  taskType: string;
  riskClass: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  jurisdiction?: string;
  provider: string;
  model: string;
  region?: string;
  estimatedCostUsd: number;
  estimatedLatencyMs: number;
  benchmarkScore: number;
  requireStructuredOutput: boolean;
};

export type ModelPolicy = {
  allowedProviders: string[];
  allowedModels: string[];
  allowedRegions: string[];
  maxCostUsd: number;
  maxLatencyMs: number;
  minBenchmarkScore: number;
};

export type ModelAdapter = {
  invoke(request: ModelRequest): Promise<{ output: unknown; providerRequestId?: string }>;
};

export type GovernedModelResult = {
  output: unknown;
  providerRequestId?: string;
  provider: string;
  model: string;
  policyDecision: "ALLOW";
};

export function enforceModelPolicy(request: ModelRequest, policy: ModelPolicy): { allowed: boolean; reason: string } {
  if (!policy.allowedProviders.includes(request.provider)) return { allowed: false, reason: "provider is not approved by tenant policy" };
  if (!policy.allowedModels.includes(request.model)) return { allowed: false, reason: "model version is not approved by tenant policy" };
  if (request.region && !policy.allowedRegions.includes(request.region)) return { allowed: false, reason: "model region violates residency policy" };
  if (request.estimatedCostUsd > policy.maxCostUsd) return { allowed: false, reason: "model cost budget exceeded" };
  if (request.estimatedLatencyMs > policy.maxLatencyMs) return { allowed: false, reason: "model latency budget exceeded" };
  if (request.benchmarkScore < policy.minBenchmarkScore) return { allowed: false, reason: "model benchmark threshold not met" };
  if (!request.requireStructuredOutput) return { allowed: false, reason: "structured output is required for governed downstream automation" };
  return { allowed: true, reason: "model request satisfies tenant policy" };
}

/** The only supported model invocation boundary for application services. */
export async function invokeThroughModelGateway(request: ModelRequest, policy: ModelPolicy, adapter: ModelAdapter): Promise<GovernedModelResult> {
  const decision = enforceModelPolicy(request, policy);
  if (!decision.allowed) throw new Error(`MODEL_POLICY_BLOCK: ${decision.reason}`);
  const result = await adapter.invoke(request);
  if (result.output === undefined || result.output === null) throw new Error("MODEL_SCHEMA_ERROR: provider returned no output");
  return { ...result, provider: request.provider, model: request.model, policyDecision: "ALLOW" };
}

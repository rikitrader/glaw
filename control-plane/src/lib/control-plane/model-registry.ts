export type ModelDeployment = {
  provider: string;
  model: string;
  version: string;
  region: string;
  benchmarkScore: number;
  approvedRiskClasses: Array<"LOW" | "MODERATE" | "HIGH" | "CRITICAL">;
  enabled: boolean;
};

export type RolloutStage = "BENCHMARK" | "SHADOW" | "CANARY_1" | "CANARY_5" | "CANARY_25" | "CANARY_50" | "FULL" | "ROLLED_BACK";

export type RolloutObservation = {
  citationAccuracy: number;
  unsupportedClaimRate: number;
  schemaFailureRate: number;
  p95LatencyMs: number;
  costPerRunUsd: number;
  securityAnomalies: number;
};

export type RolloutPolicy = {
  minCitationAccuracy: number;
  maxUnsupportedClaimRate: number;
  maxSchemaFailureRate: number;
  maxP95LatencyMs: number;
  maxCostPerRunUsd: number;
  maxSecurityAnomalies: number;
};

export function validateDeployment(deployment: ModelDeployment): void {
  if (!deployment.provider || !deployment.model || !deployment.version || !deployment.region) throw new Error("model deployment identity is incomplete");
  if (deployment.benchmarkScore < 0 || deployment.benchmarkScore > 1) throw new Error("benchmark score must be between 0 and 1");
  if (!deployment.enabled && deployment.approvedRiskClasses.length > 0) throw new Error("disabled deployment cannot be approved for risk classes");
}

export function nextRolloutStage(stage: RolloutStage, observation: RolloutObservation, policy: RolloutPolicy): RolloutStage {
  const failed = observation.citationAccuracy < policy.minCitationAccuracy ||
    observation.unsupportedClaimRate > policy.maxUnsupportedClaimRate ||
    observation.schemaFailureRate > policy.maxSchemaFailureRate ||
    observation.p95LatencyMs > policy.maxP95LatencyMs ||
    observation.costPerRunUsd > policy.maxCostPerRunUsd ||
    observation.securityAnomalies > policy.maxSecurityAnomalies;
  if (failed) return "ROLLED_BACK";
  const progression: RolloutStage[] = ["BENCHMARK", "SHADOW", "CANARY_1", "CANARY_5", "CANARY_25", "CANARY_50", "FULL"];
  return progression[Math.min(progression.indexOf(stage) + 1, progression.length - 1)];
}

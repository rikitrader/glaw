export type AgentBudget = { maxTokens: number; maxCostUsd: number; maxToolCalls: number; maxRetries: number; maxExecutionMs: number };
export type AgentUsage = { tokens: number; costUsd: number; toolCalls: number; retries: number; executionMs: number };
export function enforceAgentBudget(budget: AgentBudget, usage: AgentUsage): void {
  if (usage.tokens > budget.maxTokens || usage.costUsd > budget.maxCostUsd || usage.toolCalls > budget.maxToolCalls || usage.retries > budget.maxRetries || usage.executionMs > budget.maxExecutionMs) throw new Error("AGENT_BUDGET_EXCEEDED");
}
export function detectAgentLoop(history: string[], window = 5): boolean { if (history.length < window) return false; const tail = history.slice(-window); return new Set(tail).size === 1 || (tail.length >= 4 && tail[tail.length - 1] === tail[tail.length - 3] && tail[tail.length - 2] === tail[tail.length - 4]); }

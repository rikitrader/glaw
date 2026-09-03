import type { JurisdictionProfile, LegalIssueCode } from '../types/index.ts';
import { CORE_ISSUES, SUPPORTED_JURISDICTIONS } from '../jurisdictions/registry.ts';

export type ResearchReasonCode =
  | 'RESEARCH_REQUIRED_NO_PRIMARY_SOURCE'
  | 'RESEARCH_REQUIRED_TEMPORAL_HISTORY'
  | 'RESEARCH_REQUIRED_PRECEDENT'
  | 'RESEARCH_REQUIRED_POLICY_DEPENDENCY'
  | 'RESEARCH_REQUIRED_CONFLICT'
  | 'RESEARCH_REQUIRED_CITATION_FAILURE'
  | 'RESEARCH_REQUIRED_HUMAN_REVIEW';

export interface RemediationItem {
  jurisdiction: string;
  issue: LegalIssueCode;
  status: string;
  reasonCode: ResearchReasonCode;
  missing: string[];
  action: string;
  priority: number;
}

export function buildRemediationMatrix(
  jurisdictions: JurisdictionProfile[] = SUPPORTED_JURISDICTIONS,
  issues: LegalIssueCode[] = CORE_ISSUES,
): RemediationItem[] {
  return jurisdictions.flatMap((jurisdiction) => issues.map((issue) => ({
    jurisdiction: jurisdiction.code,
    issue,
    status: 'RESEARCH_REQUIRED',
    reasonCode: 'RESEARCH_REQUIRED_NO_PRIMARY_SOURCE' as const,
    missing: ['official source registry', 'verified primary authority', 'temporal version', 'compiled rule', 'benchmark'],
    action: 'discover → retrieve → snapshot → verify → compile → adversarial review → benchmark → human gate',
    priority: issue === 'PROMPT_PAYMENT' || issue === 'MATCHING' || issue === 'LABOR_DEPRECIATION' ? 100 : 70,
  })));
}

export function summarizeRemediation(items: RemediationItem[]): Record<string, number> {
  return items.reduce<Record<string, number>>((summary, item) => {
    summary[item.reasonCode] = (summary[item.reasonCode] ?? 0) + 1;
    return summary;
  }, {});
}

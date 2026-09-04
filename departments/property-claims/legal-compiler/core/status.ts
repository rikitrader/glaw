import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { LegalIssueCode } from '../types/index.ts';
import { CORE_ISSUES } from '../jurisdictions/registry.ts';
import { buildRemediationMatrix, type RemediationItem } from '../remediation/matrix.ts';

export interface JurisdictionStatus {
  jurisdiction: string;
  status: 'COMPLETE_VERIFIED' | 'COMPLETE_WITH_CONFLICT' | 'PARTIAL' | 'RESEARCH_REQUIRED';
  sources: number;
  verifiedSources: number;
  issues: Record<string, string>;
  queue: RemediationItem[];
}

export function getJurisdictionStatus(root: string, jurisdiction: string, issues: LegalIssueCode[] = CORE_ISSUES): JurisdictionStatus {
  const code = jurisdiction.toUpperCase();
  let sources: Array<{ verification_status?: string; issue_codes?: string[] }> = [];
  try { sources = JSON.parse(readFileSync(join(root, code, 'sources.json'), 'utf8')) as Array<{ verification_status?: string; issue_codes?: string[] }>; } catch { /* missing source registry is a real queue item */ }
  const verifiedSources = sources.filter((source) => source.verification_status === 'VERIFIED').length;
  const queue = buildRemediationMatrix([{ code, name: code, level: code === 'DC' ? 'DISTRICT' : 'STATE', sourceRegistryStatus: 'PARTIAL', supportedIssues: issues }], issues);
  const issueStatus = Object.fromEntries(issues.map((issue) => [issue, 'RESEARCH_REQUIRED_NO_PRIMARY_SOURCE']));
  for (const source of sources) if (source.verification_status === 'VERIFIED') for (const issue of source.issue_codes ?? []) issueStatus[issue] = 'SOURCE_VERIFIED_BUT_RULE_NOT_ACTIVATED';
  return { jurisdiction: code, status: verifiedSources ? 'PARTIAL' : 'RESEARCH_REQUIRED', sources: sources.length, verifiedSources, issues: issueStatus, queue };
}

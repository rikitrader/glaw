/**
 * Federal Pleading Engine - Fact Gap & Precondition Helpers
 *
 * Encapsulates the precondition evaluation logic (exhaustion, timing,
 * standing) and gap-derivation helpers used by the orchestrator.
 */

import { CaseInput, ClaimPrecondition, FactGap, FactElementMapping } from '../schema';

/**
 * Evaluate claim preconditions against case input
 */
export function evaluatePreconditions(
  preconditions: ClaimPrecondition[],
  caseInput: CaseInput
): ClaimPrecondition[] {
  return preconditions.map(precondition => {
    let satisfied: boolean | 'unknown' = 'unknown';

    switch (precondition.type) {
      case 'exhaustion':
        // Check exhaustion status
        if (precondition.requirement.toLowerCase().includes('eeoc')) {
          satisfied = caseInput.exhaustion.eeoc_charge_filed;
        } else if (precondition.requirement.toLowerCase().includes('sf-95') ||
                   precondition.requirement.toLowerCase().includes('ftca')) {
          satisfied = caseInput.exhaustion.ftca_admin_claim_filed;
        } else if (precondition.requirement.toLowerCase().includes('erisa')) {
          satisfied = caseInput.exhaustion.erisa_appeal_done;
        } else if (precondition.requirement.toLowerCase().includes('agency')) {
          satisfied = caseInput.exhaustion.agency_final_action;
        }
        break;

      case 'timing':
        // Check if key dates are provided
        if (caseInput.limitations.key_dates.injury_date) {
          satisfied = 'unknown'; // Would need SOL calculation
        }
        break;

      case 'standing':
        // Check if facts indicate injury
        const hasInjury = caseInput.facts.some(f =>
          f.harm && f.harm.length > 0
        );
        satisfied = hasInjury;
        break;

      default:
        satisfied = 'unknown';
    }

    return {
      ...precondition,
      satisfied,
    };
  });
}

/**
 * Derive a FactGap entry for a single element-mapping result,
 * or null if the element already has full coverage.
 *
 * Priorities:
 *   - 'critical'   when coverage === 'none'
 *   - 'important'  when coverage === 'partial'
 */
export function deriveGapForElement(
  element: { number: number; name: string; mustAllege: string; typicalEvidence: string[] },
  mapping: FactElementMapping
): FactGap | null {
  if (mapping.coverage === 'none') {
    return {
      elementNumber: element.number,
      elementName: element.name,
      missingInfo: element.mustAllege,
      priority: 'critical',
      suggestedSources: element.typicalEvidence,
    };
  }
  if (mapping.coverage === 'partial') {
    return {
      elementNumber: element.number,
      elementName: element.name,
      missingInfo: `Partial support for: ${element.mustAllege}`,
      priority: 'important',
      suggestedSources: element.typicalEvidence,
    };
  }
  return null;
}

/**
 * Deduplicate and priority-sort a list of FactGap entries.
 * Matches the original ordering in generateFactGapReport.
 */
export function dedupeAndSortGaps(gaps: FactGap[]): FactGap[] {
  const seen = new Set<string>();
  const deduped: FactGap[] = [];

  for (const gap of gaps) {
    const gapId = `${gap.elementName}-${gap.missingInfo}`;
    if (!seen.has(gapId)) {
      seen.add(gapId);
      deduped.push(gap);
    }
  }

  const priorityOrder = { critical: 0, important: 1, helpful: 2 };
  deduped.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  return deduped;
}

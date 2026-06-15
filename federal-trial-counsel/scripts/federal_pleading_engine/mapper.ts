/**
 * Federal Pleading Engine - Fact to Element Mapper (Orchestrator)
 *
 * Maps case facts to required legal elements using keyword matching,
 * actor analysis, and date proximity heuristics.
 *
 * Implementation is split across `mapper/` to keep each file under the
 * 500-line project cap:
 *   - mapper/keywords.ts    Pure keyword dictionaries
 *   - mapper/heuristics.ts  Keyword-matching / scoring helpers
 *   - mapper/fact_gaps.ts   Precondition & gap helpers
 *
 * This file only orchestrates the public API:
 *   - mapFactsToElements
 *   - autoSuggestClaims
 *   - generateFactGapReport
 *   - checkPreconditionsMet
 */

import {
  CaseInput,
  ClaimMappingResult,
  FactElementMapping,
  FactGap,
} from './schema';
import { getClaimMetadata, CLAIM_LIBRARY } from './claim_library';
import { getElements, getPreconditions } from './elements';

import { mapElementToFacts, scoreClaimFactPatterns } from './mapper/heuristics';
import {
  evaluatePreconditions,
  deriveGapForElement,
  dedupeAndSortGaps,
} from './mapper/fact_gaps';

/**
 * Map facts to elements for a specific claim
 */
export function mapFactsToElements(
  caseInput: CaseInput,
  claimKey: string
): ClaimMappingResult {
  const claimMetadata = getClaimMetadata(claimKey);
  const elements = getElements(claimKey);
  const preconditions = getPreconditions(claimKey);

  if (!claimMetadata || !elements) {
    return {
      claimKey,
      claimName: claimMetadata?.name || 'Unknown Claim',
      elements: [],
      overallCoverage: 0,
      factGaps: [{
        elementNumber: 0,
        elementName: 'Claim Definition',
        missingInfo: 'No element definitions found for this claim',
        priority: 'critical',
        suggestedSources: ['Legal research'],
      }],
      preconditions: [],
    };
  }

  const elementMappings: FactElementMapping[] = [];
  const factGaps: FactGap[] = [];

  // Map each element to relevant facts
  for (const element of elements) {
    const mapping = mapElementToFacts(element, caseInput.facts);
    elementMappings.push(mapping);

    const gap = deriveGapForElement(element, mapping);
    if (gap) factGaps.push(gap);
  }

  // Calculate overall coverage
  const coveredElements = elementMappings.filter(m => m.coverage !== 'none').length;
  const overallCoverage = Math.round((coveredElements / elements.length) * 100);

  // Evaluate preconditions
  const evaluatedPreconditions = evaluatePreconditions(preconditions, caseInput);

  return {
    claimKey,
    claimName: claimMetadata.name,
    elements: elementMappings,
    overallCoverage,
    factGaps,
    preconditions: evaluatedPreconditions,
  };
}

/**
 * Auto-suggest claims based on facts
 */
export function autoSuggestClaims(caseInput: CaseInput): {
  claimKey: string;
  claimName: string;
  matchScore: number;
  reasons: string[];
  showstoppers: string[];
}[] {
  const suggestions: {
    claimKey: string;
    claimName: string;
    matchScore: number;
    reasons: string[];
    showstoppers: string[];
  }[] = [];

  const allFacts = caseInput.facts.map(f =>
    `${f.event} ${f.harm} ${f.actors.join(' ')}`
  ).join(' ').toLowerCase();

  // Check each claim for relevance
  for (const [claimKey, metadata] of Object.entries(CLAIM_LIBRARY)) {
    const elements = getElements(claimKey);
    if (!elements) continue;

    const reasons: string[] = [];
    const showstoppers: string[] = [];
    let matchScore = 0;

    // Check defendant types
    const hasStateActor = caseInput.parties.defendants.some(d =>
      ['state', 'local', 'federal', 'officer'].includes(d.type)
    );
    // Note: hasPrivateDefendant is computed in the legacy code but unused.
    // Preserving the computation would be dead code; it's safely omitted.

    // Constitutional claims need state actors
    if (metadata.category === 'constitutional_civil_rights' || metadata.category === 'bivens') {
      if (hasStateActor) {
        matchScore += 20;
        reasons.push('State actor defendant identified');
      } else {
        showstoppers.push('No state actor defendant - § 1983 requires action under color of law');
        continue; // Skip this claim
      }
    }

    // Fact-pattern scoring (regex ladder over claim-type keywords).
    const patternResult = scoreClaimFactPatterns(claimKey, metadata.category, allFacts);
    matchScore += patternResult.scoreDelta;
    reasons.push(...patternResult.reasons);

    // Check exhaustion requirements
    if (metadata.exhaustionRequired) {
      if (metadata.exhaustionType === 'eeoc' && caseInput.exhaustion.eeoc_charge_filed !== true) {
        showstoppers.push('EEOC charge not filed - administrative exhaustion required');
      }
      if (metadata.exhaustionType === 'ftca_sf95' && caseInput.exhaustion.ftca_admin_claim_filed !== true) {
        showstoppers.push('SF-95 administrative claim not filed - FTCA exhaustion required');
      }
    }

    // Check for viability warnings (Bivens)
    if (metadata.viabilityWarning) {
      showstoppers.push(metadata.viabilityWarning);
    }

    // Map facts to elements for scoring
    if (matchScore > 0 || reasons.length > 0) {
      const mapping = mapFactsToElements(caseInput, claimKey);
      matchScore += mapping.overallCoverage * 0.5;

      if (mapping.overallCoverage >= 50) {
        reasons.push(`${mapping.overallCoverage}% element coverage`);
      }
    }

    if (matchScore > 20 || reasons.length > 0) {
      suggestions.push({
        claimKey,
        claimName: metadata.name,
        matchScore: Math.min(100, Math.round(matchScore)),
        reasons,
        showstoppers,
      });
    }
  }

  // Sort by match score
  suggestions.sort((a, b) => b.matchScore - a.matchScore);

  return suggestions.slice(0, 10); // Top 10 suggestions
}

/**
 * Generate fact gap analysis for multiple claims
 */
export function generateFactGapReport(
  caseInput: CaseInput,
  claimKeys: string[]
): FactGap[] {
  const allGaps: FactGap[] = [];

  for (const claimKey of claimKeys) {
    const mapping = mapFactsToElements(caseInput, claimKey);
    allGaps.push(...mapping.factGaps);
  }

  return dedupeAndSortGaps(allGaps);
}

/**
 * Check if all critical preconditions are met for a claim
 */
export function checkPreconditionsMet(
  caseInput: CaseInput,
  claimKey: string
): { met: boolean; issues: string[] } {
  const preconditions = getPreconditions(claimKey);
  const evaluated = evaluatePreconditions(preconditions, caseInput);

  const issues: string[] = [];

  for (const precondition of evaluated) {
    if (precondition.satisfied === false) {
      issues.push(`${precondition.requirement} - NOT SATISFIED`);
    } else if (precondition.satisfied === 'unknown') {
      issues.push(`${precondition.requirement} - STATUS UNKNOWN`);
    }
  }

  return {
    met: issues.filter(i => i.includes('NOT SATISFIED')).length === 0,
    issues,
  };
}

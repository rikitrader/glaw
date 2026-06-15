/**
 * Federal Pleading Engine - MTD Risk Scoring
 *
 * Calculates motion to dismiss vulnerability scores and identifies
 * specific risk factors with recommended fixes.
 */

import {
  CaseInput,
  ClaimMappingResult,
  MTDRiskScore,
  RiskFactor,
  RiskCategory,
} from './schema';
import { getClaimMetadata, CLAIM_LIBRARY } from './claim_library';
import { getElements, getPreconditions } from './elements';
import { mapFactsToElements } from './mapper';

/**
 * Compute elapsed calendar years between two dates.
 * Counts whole anniversaries then adds a fractional year scaled by the days
 * into the current anniversary cycle. Leap-year safe to within ~1 day.
 */
function calendarYearsBetween(from: Date, to: Date): number {
  const years = to.getUTCFullYear() - from.getUTCFullYear();
  const anniversary = new Date(Date.UTC(
    to.getUTCFullYear(),
    from.getUTCMonth(),
    from.getUTCDate()
  ));
  const wholeYears = to.getTime() >= anniversary.getTime() ? years : years - 1;
  const cycleStart = new Date(Date.UTC(
    to.getUTCFullYear() - (to.getTime() >= anniversary.getTime() ? 0 : 1),
    from.getUTCMonth(),
    from.getUTCDate()
  ));
  const cycleEnd = new Date(cycleStart);
  cycleEnd.setUTCFullYear(cycleEnd.getUTCFullYear() + 1);
  const cycleLen = cycleEnd.getTime() - cycleStart.getTime();
  const intoCycle = to.getTime() - cycleStart.getTime();
  return wholeYears + intoCycle / cycleLen;
}

/**
 * Weight factors for each risk category
 */
const RISK_WEIGHTS: Record<RiskCategory, number> = {
  standing: 15,
  immunity: 20,
  exhaustion: 15,
  sol: 15,
  rule_9b: 10,
  monell: 10,
  causation: 10,
  damages: 5,
  plausibility: 100, // Base weight for overall plausibility
};

/**
 * Calculate comprehensive MTD risk score for a claim
 */
export function calculateMTDRisk(
  caseInput: CaseInput,
  claimKey: string,
  mapping: ClaimMappingResult
): MTDRiskScore {
  const factors: RiskFactor[] = [];

  // 1. Standing Risk
  factors.push(assessStandingRisk(caseInput, claimKey));

  // 2. Immunity Risk
  factors.push(assessImmunityRisk(caseInput, claimKey));

  // 3. Exhaustion Risk
  factors.push(assessExhaustionRisk(caseInput, claimKey));

  // 4. Statute of Limitations Risk
  factors.push(assessSOLRisk(caseInput, claimKey));

  // 5. Rule 9(b) Risk (if applicable)
  const rule9bRisk = assessRule9bRisk(caseInput, claimKey);
  if (rule9bRisk) {
    factors.push(rule9bRisk);
  }

  // 6. Monell Risk (if applicable)
  const monellRisk = assessMonellRisk(caseInput, claimKey);
  if (monellRisk) {
    factors.push(monellRisk);
  }

  // 7. Causation Risk
  factors.push(assessCausationRisk(caseInput, mapping));

  // 8. Damages Risk
  factors.push(assessDamagesRisk(caseInput));

  // 9. Plausibility Risk (based on element coverage)
  factors.push(assessPlausibilityRisk(mapping));

  // Calculate overall score
  const overallScore = calculateOverallScore(factors);

  // Determine risk level
  const riskLevel = getRiskLevel(overallScore);

  // Extract top vulnerabilities and prioritized fixes
  const topVulnerabilities = factors
    .filter(f => f.score > 50)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map(f => f.issue);

  const prioritizedFixes = factors
    .filter(f => f.score > 30)
    .sort((a, b) => (b.score * b.weight) - (a.score * a.weight))
    .slice(0, 5)
    .map(f => f.fix);

  return {
    overallScore,
    riskLevel,
    factors,
    topVulnerabilities,
    prioritizedFixes,
  };
}

/**
 * Assess standing risk
 */
function assessStandingRisk(caseInput: CaseInput, claimKey: string): RiskFactor {
  let score = 0;
  const issues: string[] = [];

  // Check for injury
  const hasInjury = caseInput.facts.some(f => f.harm?.trim().length > 0);
  if (!hasInjury) {
    score += 40;
    issues.push('No injury alleged');
  }

  // Check for causation to defendant
  const hasDefendantInFacts = caseInput.facts.some(f =>
    f.actors.some(a =>
      caseInput.parties.defendants.some(d =>
        d.name.toLowerCase().includes(a.toLowerCase()) ||
        a.toLowerCase().includes(d.name.toLowerCase().split(' ')[0])
      )
    )
  );
  if (!hasDefendantInFacts) {
    score += 30;
    issues.push('Defendant not clearly linked to harm');
  }

  // Check redressability
  if (caseInput.relief_requested.length === 0) {
    score += 20;
    issues.push('No relief requested');
  }

  return {
    category: 'standing',
    score: Math.min(100, score),
    weight: RISK_WEIGHTS.standing,
    issue: issues.length > 0 ? issues.join('; ') : 'Standing appears adequate',
    fix: score > 50 ?
      'Strengthen injury-in-fact allegations with specific harm, causation to defendant, and concrete relief requested' :
      'Standing requirements appear satisfied',
  };
}

/**
 * Assess immunity risk
 */
function assessImmunityRisk(caseInput: CaseInput, claimKey: string): RiskFactor {
  const metadata = getClaimMetadata(claimKey);
  let score = 0;
  const issues: string[] = [];

  if (!metadata) {
    return {
      category: 'immunity',
      score: 0,
      weight: RISK_WEIGHTS.immunity,
      issue: 'Unable to assess immunity',
      fix: 'Verify claim exists in library',
    };
  }

  // Check for qualified immunity
  if (metadata.immunities.includes('qualified')) {
    const hasOfficerDefendant = caseInput.parties.defendants.some(d =>
      d.type === 'officer' && d.capacity === 'individual'
    );

    if (hasOfficerDefendant) {
      score += 60;
      issues.push('Qualified immunity defense likely from individual officers');
    }
  }

  // Check for sovereign immunity
  if (metadata.immunities.includes('sovereign')) {
    const hasFederalDefendant = caseInput.parties.defendants.some(d =>
      d.type === 'federal'
    );

    if (hasFederalDefendant) {
      // Check for FTCA waiver
      if (claimKey.includes('ftca')) {
        score += 30;
        issues.push('FTCA waiver applies but discretionary function exception may apply');
      } else {
        score += 70;
        issues.push('Sovereign immunity may bar claims against federal defendant');
      }
    }
  }

  // Check for Eleventh Amendment immunity
  if (metadata.immunities.includes('eleventh_amendment')) {
    const hasStateDefendant = caseInput.parties.defendants.some(d =>
      d.type === 'state'
    );

    if (hasStateDefendant) {
      score += 70;
      issues.push('Eleventh Amendment bars damages against state');
    }
  }

  return {
    category: 'immunity',
    score: Math.min(100, score),
    weight: RISK_WEIGHTS.immunity,
    issue: issues.length > 0 ? issues.join('; ') : 'No significant immunity concerns',
    fix: score > 50 ?
      'Argue clearly established right for QI; identify specific waiver for sovereign immunity; consider official capacity for prospective relief' :
      'Immunity defense unlikely to succeed',
  };
}

/**
 * Assess exhaustion risk
 */
function assessExhaustionRisk(caseInput: CaseInput, claimKey: string): RiskFactor {
  const metadata = getClaimMetadata(claimKey);
  let score = 0;
  let issue = '';
  let fix = '';

  if (!metadata || !metadata.exhaustionRequired) {
    return {
      category: 'exhaustion',
      score: 0,
      weight: RISK_WEIGHTS.exhaustion,
      issue: 'No exhaustion required for this claim',
      fix: 'N/A',
    };
  }

  switch (metadata.exhaustionType) {
    case 'eeoc':
      if (caseInput.exhaustion.eeoc_charge_filed === false) {
        score = 95;
        issue = 'EEOC charge not filed - claim will be dismissed';
        fix = 'File EEOC charge immediately; case cannot proceed without exhaustion';
      } else if (caseInput.exhaustion.eeoc_charge_filed === 'unknown') {
        score = 50;
        issue = 'EEOC exhaustion status unknown';
        fix = 'Confirm EEOC charge was filed and right-to-sue letter received';
      }
      break;

    case 'ftca_sf95':
      if (caseInput.exhaustion.ftca_admin_claim_filed === false) {
        score = 95;
        issue = 'SF-95 administrative claim not filed - FTCA claim will be dismissed';
        fix = 'File SF-95 with appropriate agency; wait for denial or 6 months';
      } else if (caseInput.exhaustion.ftca_admin_claim_filed === 'unknown') {
        score = 50;
        issue = 'FTCA exhaustion status unknown';
        fix = 'Confirm SF-95 was filed and either denied or 6 months passed';
      }
      break;

    case 'erisa_internal':
      if (caseInput.exhaustion.erisa_appeal_done === false) {
        score = 80;
        issue = 'ERISA internal appeal not completed';
        fix = 'Complete internal appeal process unless futility exception applies';
      } else if (caseInput.exhaustion.erisa_appeal_done === 'unknown') {
        score = 40;
        issue = 'ERISA exhaustion status unknown';
        fix = 'Confirm internal appeal was completed';
      }
      break;

    case 'apa_final_action':
      if (caseInput.exhaustion.agency_final_action === false) {
        score = 90;
        issue = 'No final agency action - APA claim premature';
        fix = 'Wait for final agency action or argue exhaustion not required';
      } else if (caseInput.exhaustion.agency_final_action === 'unknown') {
        score = 40;
        issue = 'Final agency action status unknown';
        fix = 'Confirm agency action is final and not subject to further review';
      }
      break;

    case 'plra':
      if (caseInput.exhaustion.plra_exhaustion_done === false) {
        score = 95;
        issue = 'PLRA exhaustion NOT completed - claim will be dismissed';
        fix = 'Complete prison administrative grievance process before filing';
      } else if (caseInput.exhaustion.plra_exhaustion_done === 'unknown') {
        score = 50;
        issue = 'PLRA exhaustion status unknown';
        fix = 'Confirm all administrative remedies were exhausted per 42 U.S.C. 1997e(a)';
      }
      break;

    case 'administrative':
      if (caseInput.exhaustion.administrative_exhaustion_done === false) {
        score = 80;
        issue = 'Administrative exhaustion not completed';
        fix = 'Complete administrative remedy process before filing';
      } else if (caseInput.exhaustion.administrative_exhaustion_done === 'unknown') {
        score = 40;
        issue = 'Administrative exhaustion status unknown';
        fix = 'Confirm all administrative remedies were exhausted';
      }
      break;

    case 'irs_claim':
      if (caseInput.exhaustion.irs_claim_filed === false) {
        score = 95;
        issue = 'IRS administrative claim NOT filed - suit barred';
        fix = 'File administrative claim with IRS; pay full assessment (Flora rule)';
      } else if (caseInput.exhaustion.irs_claim_filed === 'unknown') {
        score = 50;
        issue = 'IRS claim filing status unknown';
        fix = 'Confirm administrative claim filed and full tax paid';
      }
      break;

    default:
      score = 30;
      issue = 'Exhaustion may be required';
      fix = 'Verify all administrative prerequisites are met';
  }

  return {
    category: 'exhaustion',
    score,
    weight: RISK_WEIGHTS.exhaustion,
    issue: issue || 'Exhaustion requirements appear satisfied',
    fix: fix || 'Exhaustion complete',
  };
}

/**
 * Assess statute of limitations risk
 */
function assessSOLRisk(caseInput: CaseInput, claimKey: string): RiskFactor {
  const metadata = getClaimMetadata(claimKey);
  let score = 0;
  let issue = '';
  let fix = '';

  if (!metadata) {
    return {
      category: 'sol',
      score: 0,
      weight: RISK_WEIGHTS.sol,
      issue: 'Unable to assess SOL',
      fix: 'Verify claim exists',
    };
  }

  const injuryDate = caseInput.limitations?.key_dates?.injury_date;

  if (!injuryDate) {
    score = 30;
    issue = 'Injury date not specified - cannot calculate SOL';
    fix = 'Specify injury date to verify statute of limitations compliance';
  } else {
    // Parse dates and calculate
    const injury = new Date(injuryDate);
    if (isNaN(injury.getTime())) {
      return {
        category: 'sol',
        score: 30,
        weight: RISK_WEIGHTS.sol,
        issue: 'Invalid injury date format - cannot calculate SOL',
        fix: 'Provide valid date in ISO format (YYYY-MM-DD)',
      };
    }
    const today = new Date();
    // Calendar-aware year elapsed computation — avoids /365 drift on leap-year
    // boundaries that can miss an SOL deadline by 1-2 days.
    const yearsSinceInjury = calendarYearsBetween(injury, today);

    // Extract SOL from metadata
    const solText = metadata.statuteOfLimitations.toLowerCase();

    // Handle no fixed SOL (laches only)
    if (/\bnone\b/i.test(solText) || /\blaches\b/i.test(solText)) {
      return {
        category: 'sol',
        score: 0,
        weight: RISK_WEIGHTS.sol,
        issue: `No fixed SOL - ${metadata.statuteOfLimitations}`,
        fix: 'Laches defense may apply; file promptly to minimize risk',
      };
    }

    // Handle "varies" SOL - flag for manual verification
    if (/\bvaries\b/i.test(solText) && !/\b\d+\s*(year|month|day)/i.test(solText)) {
      return {
        category: 'sol',
        score: 30,
        weight: RISK_WEIGHTS.sol,
        issue: `SOL varies - ${metadata.statuteOfLimitations}`,
        fix: 'Verify applicable SOL based on specific plan terms or state law',
      };
    }

    let solYears = 4; // Default

    if (/\b90\s*day/i.test(solText)) solYears = 0.25;
    else if (/\b9\s*month/i.test(solText)) solYears = 0.75;
    else if (/\b1\s*year\b/i.test(solText)) solYears = 1;
    else if (/\b2\s*year/i.test(solText)) solYears = 2;
    else if (/\b3\s*year/i.test(solText)) solYears = 3;
    else if (/\b4\s*year/i.test(solText)) solYears = 4;
    else if (/\b6\s*year/i.test(solText)) solYears = 6;

    if (yearsSinceInjury > solYears) {
      score = 95;
      issue = `SOL expired - ${metadata.statuteOfLimitations}`;
      fix = 'Investigate tolling doctrines (discovery rule, equitable tolling, continuing violation)';
    } else if (yearsSinceInjury > solYears * 0.8) {
      score = 40;
      issue = `SOL expires soon - ${metadata.statuteOfLimitations}`;
      fix = 'File immediately to preserve claims';
    } else {
      issue = `Within SOL - ${metadata.statuteOfLimitations}`;
      fix = 'SOL not a concern';
    }
  }

  return {
    category: 'sol',
    score,
    weight: RISK_WEIGHTS.sol,
    issue,
    fix,
  };
}

/**
 * Assess Rule 9(b) risk for fraud claims
 */
function assessRule9bRisk(caseInput: CaseInput, claimKey: string): RiskFactor | null {
  const metadata = getClaimMetadata(claimKey);

  if (!metadata || !metadata.heightenedPleading) {
    return null;
  }

  let score = 0;
  const issues: string[] = [];

  // Check for specificity in facts
  for (const fact of caseInput.facts) {
    if (!fact.date) {
      score += 15;
      issues.push('Missing date for factual allegation');
    }
    if (!fact.location) {
      score += 10;
      issues.push('Missing location');
    }
    if (fact.actors.length === 0) {
      score += 20;
      issues.push('No specific actors identified');
    }
  }

  // Cap the score
  score = Math.min(100, score);

  return {
    category: 'rule_9b',
    score,
    weight: RISK_WEIGHTS.rule_9b,
    issue: issues.length > 0 ?
      `Rule 9(b) particularity concerns: ${issues.slice(0, 3).join('; ')}` :
      'Rule 9(b) requirements appear satisfied',
    fix: score > 50 ?
      'Add specific who/what/when/where/how for each fraudulent act' :
      'Particularity adequate',
  };
}

/**
 * Assess Monell risk for municipal liability claims
 */
function assessMonellRisk(caseInput: CaseInput, claimKey: string): RiskFactor | null {
  if (!claimKey.includes('monell')) {
    // Check if municipal defendant but no Monell claim
    const hasMunicipalDefendant = caseInput.parties.defendants.some(d =>
      d.type === 'local' && d.entity_type === 'municipality'
    );

    if (hasMunicipalDefendant) {
      return {
        category: 'monell',
        score: 60,
        weight: RISK_WEIGHTS.monell,
        issue: 'Municipal defendant requires Monell policy/custom allegations',
        fix: 'Add Monell claim alleging official policy, custom, or failure to train',
      };
    }
    return null;
  }

  let score = 0;
  const issues: string[] = [];

  // Check for policy allegations in facts
  const factsText = caseInput.facts.map(f => f.event).join(' ').toLowerCase();

  if (!factsText.includes('policy') && !factsText.includes('custom') &&
      !factsText.includes('training') && !factsText.includes('pattern')) {
    score += 50;
    issues.push('No policy/custom allegations in facts');
  }

  // Check for pattern evidence
  if (!factsText.includes('pattern') && !factsText.includes('multiple') &&
      !factsText.includes('repeated') && !factsText.includes('prior incidents')) {
    score += 30;
    issues.push('No pattern evidence alleged');
  }

  return {
    category: 'monell',
    score: Math.min(100, score),
    weight: RISK_WEIGHTS.monell,
    issue: issues.length > 0 ?
      `Monell deficiencies: ${issues.join('; ')}` :
      'Monell requirements appear addressed',
    fix: score > 50 ?
      'Allege specific policy, widespread custom, or failure to train with deliberate indifference' :
      'Monell allegations adequate',
  };
}

/**
 * Assess causation risk
 */
function assessCausationRisk(caseInput: CaseInput, mapping: ClaimMappingResult): RiskFactor {
  let score = 0;
  const issues: string[] = [];

  // Check if causation element is covered
  const causationElement = mapping.elements.find(e =>
    e.elementName.toLowerCase().includes('causation') ||
    e.elementName.toLowerCase().includes('cause')
  );

  if (causationElement && causationElement.coverage === 'none') {
    score += 50;
    issues.push('Causation element not supported by facts');
  } else if (causationElement && causationElement.coverage === 'partial') {
    score += 25;
    issues.push('Causation element only partially supported');
  }

  // Check for intervening causes
  const factsText = caseInput.facts.map(f => f.event).join(' ').toLowerCase();
  if (factsText.includes('intervening') || factsText.includes('superseding')) {
    score += 20;
    issues.push('Potential intervening cause mentioned');
  }

  return {
    category: 'causation',
    score: Math.min(100, score),
    weight: RISK_WEIGHTS.causation,
    issue: issues.length > 0 ? issues.join('; ') : 'Causation appears adequately alleged',
    fix: score > 30 ?
      'Strengthen direct link between defendant\'s conduct and plaintiff\'s injury' :
      'Causation adequately pleaded',
  };
}

/**
 * Assess damages risk
 */
function assessDamagesRisk(caseInput: CaseInput): RiskFactor {
  let score = 0;
  const issues: string[] = [];

  // Check for damages evidence
  const hasDamagesEstimate = caseInput.facts.some(f => f.damages_estimate);
  const hasHarm = caseInput.facts.some(f => f.harm && f.harm.length > 0);

  if (!hasDamagesEstimate && !hasHarm) {
    score += 40;
    issues.push('No damages or harm alleged');
  } else if (!hasDamagesEstimate) {
    score += 20;
    issues.push('Damages not quantified');
  }

  // Check for supporting evidence
  const hasDocuments = caseInput.facts.some(f => f.documents.length > 0);
  if (!hasDocuments) {
    score += 15;
    issues.push('No supporting documents referenced');
  }

  return {
    category: 'damages',
    score: Math.min(100, score),
    weight: RISK_WEIGHTS.damages,
    issue: issues.length > 0 ? issues.join('; ') : 'Damages adequately alleged',
    fix: score > 30 ?
      'Add specific damages amounts and supporting documentation' :
      'Damages pleading adequate',
  };
}

/**
 * Assess overall plausibility based on element coverage
 */
function assessPlausibilityRisk(mapping: ClaimMappingResult): RiskFactor {
  // Invert coverage to get risk score
  const riskScore = 100 - mapping.overallCoverage;

  let issue = '';
  let fix = '';

  if (riskScore > 60) {
    issue = `Only ${mapping.overallCoverage}% of elements supported by facts`;
    fix = 'Develop facts for missing elements or reconsider claim viability';
  } else if (riskScore > 30) {
    issue = `${mapping.overallCoverage}% element coverage - some gaps remain`;
    fix = 'Strengthen factual allegations for partially covered elements';
  } else {
    issue = `${mapping.overallCoverage}% element coverage - plausibility strong`;
    fix = 'Continue with current allegations';
  }

  return {
    category: 'plausibility',
    score: riskScore,
    weight: 20, // High weight for overall plausibility
    issue,
    fix,
  };
}

/**
 * Calculate weighted overall score
 */
function calculateOverallScore(factors: RiskFactor[]): number {
  let totalWeightedScore = 0;
  let totalWeight = 0;

  for (const factor of factors) {
    totalWeightedScore += factor.score * factor.weight;
    totalWeight += factor.weight;
  }

  return totalWeight > 0 ? Math.round(totalWeightedScore / totalWeight) : 50;
}

/**
 * Determine risk level from score
 */
function getRiskLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
  if (score < 25) return 'low';
  if (score < 50) return 'medium';
  if (score < 75) return 'high';
  return 'critical';
}

/**
 * Generate comprehensive defense matrix
 */
export function generateDefenseMatrix(
  caseInput: CaseInput,
  claimKeys: string[]
): {
  rule12bDefenses: { type: string; risk: string; counter: string }[];
  immunityDefenses: { type: string; risk: string; counter: string }[];
  proceduralDefenses: { type: string; risk: string; counter: string }[];
  pleadingAttacks: { type: string; risk: string; counter: string }[];
  substantiveDefenses: { type: string; risk: string; counter: string }[];
} {
  const rule12bDefenses: { type: string; risk: string; counter: string }[] = [];
  const immunityDefenses: { type: string; risk: string; counter: string }[] = [];
  const proceduralDefenses: { type: string; risk: string; counter: string }[] = [];
  const pleadingAttacks: { type: string; risk: string; counter: string }[] = [];
  const substantiveDefenses: { type: string; risk: string; counter: string }[] = [];

  // Analyze each claim
  for (const claimKey of claimKeys) {
    const metadata = getClaimMetadata(claimKey);
    if (!metadata) continue;

    // Rule 12(b) defenses
    rule12bDefenses.push({
      type: '12(b)(1) Subject Matter Jurisdiction',
      risk: metadata.jurisdiction === 'federal_question' ? 'Low' : 'Medium',
      counter: 'Ensure jurisdictional allegations are complete and supported',
    });

    rule12bDefenses.push({
      type: '12(b)(6) Failure to State a Claim',
      risk: 'High',
      counter: 'Ensure each element has specific factual support per Twombly/Iqbal',
    });

    // Immunity defenses
    for (const immunity of metadata.immunities) {
      immunityDefenses.push({
        type: immunity === 'qualified' ? 'Qualified Immunity' :
              immunity === 'sovereign' ? 'Sovereign Immunity' :
              immunity === 'eleventh_amendment' ? 'Eleventh Amendment' :
              immunity,
        risk: 'High',
        counter: immunity === 'qualified' ?
          'Identify clearly established law with specific factual similarity' :
          'Identify specific waiver or sue in appropriate capacity',
      });
    }

    // Procedural defenses
    if (metadata.exhaustionRequired) {
      proceduralDefenses.push({
        type: 'Failure to Exhaust',
        risk: 'High',
        counter: `Document ${metadata.exhaustionType} exhaustion with attached records`,
      });
    }

    proceduralDefenses.push({
      type: 'Statute of Limitations',
      risk: 'Medium',
      counter: `Verify filing within ${metadata.statuteOfLimitations}`,
    });

    // Pleading attacks
    if (metadata.heightenedPleading) {
      pleadingAttacks.push({
        type: 'Rule 9(b) Particularity',
        risk: 'High',
        counter: 'Plead who/what/when/where/how for each misrepresentation',
      });
    }

    // Substantive defenses
    for (const defense of metadata.typicalDefenses) {
      substantiveDefenses.push({
        type: defense,
        risk: 'Medium',
        counter: '[Develop specific counter based on case facts]',
      });
    }
  }

  return {
    rule12bDefenses,
    immunityDefenses,
    proceduralDefenses,
    pleadingAttacks,
    substantiveDefenses,
  };
}

/**
 * Calculate case survival probability
 */
export function calculateSurvivalProbability(
  caseInput: CaseInput,
  claimKeys: string[]
): {
  mtdSurvival: number;
  sjSurvival: number;
  trialLikelihood: number;
  killRiskFlags: string[];
  strengthBoosters: string[];
  recommendation: string;
} {
  // Baseline survival percentages are heuristic priors, not derived from case
  // data. They reflect rough empirical base rates for civil federal cases:
  //  - ~70% of well-pleaded complaints survive MTD (claim-specific MTD risk
  //    factors then discount this).
  //  - ~50% of cases that survive MTD reach or survive SJ (element coverage
  //    moves this up/down).
  //  - ~30% of surviving cases actually reach trial; most settle.
  // These are starting values; the per-claim logic below is what matters.
  let mtdScore = 70;
  let sjScore = 50;
  let trialLikelihood = 30;
  const killRiskFlags: string[] = [];
  const strengthBoosters: string[] = [];

  for (const claimKey of claimKeys) {
    const mapping = mapFactsToElements(caseInput, claimKey);
    const mtdRisk = calculateMTDRisk(caseInput, claimKey, mapping);

    // Adjust MTD survival
    if (mtdRisk.riskLevel === 'critical') {
      mtdScore -= 30;
      killRiskFlags.push(`${claimKey}: ${mtdRisk.topVulnerabilities[0]}`);
    } else if (mtdRisk.riskLevel === 'high') {
      mtdScore -= 15;
    }

    // Element coverage affects SJ survival
    if (mapping.overallCoverage > 80) {
      sjScore += 10;
      strengthBoosters.push(`${claimKey}: Strong element coverage (${mapping.overallCoverage}%)`);
    } else if (mapping.overallCoverage < 50) {
      sjScore -= 15;
      killRiskFlags.push(`${claimKey}: Weak element coverage (${mapping.overallCoverage}%)`);
    }
  }

  // Check evidence strength
  const hasDocuments = caseInput.facts.some(f => f.documents.length > 0);
  const hasWitnesses = caseInput.facts.some(f => f.witnesses.length > 0);
  const hasEvidence = caseInput.facts.some(f => f.evidence.length > 0);

  if (hasDocuments && hasWitnesses && hasEvidence) {
    sjScore += 15;
    trialLikelihood += 10;
    strengthBoosters.push('Strong documentary and testimonial evidence');
  } else if (!hasDocuments && !hasEvidence) {
    sjScore -= 20;
    killRiskFlags.push('Weak evidence base');
  }

  // Cap scores
  mtdScore = Math.max(10, Math.min(90, mtdScore));
  sjScore = Math.max(10, Math.min(80, sjScore));
  trialLikelihood = Math.max(5, Math.min(60, trialLikelihood));

  // Recommendation
  let recommendation = '';
  if (mtdScore < 40) {
    recommendation = 'Consider voluntary dismissal or significant amendment before MTD response';
  } else if (mtdScore < 60) {
    recommendation = 'Amend complaint to address vulnerabilities; consider settlement';
  } else if (sjScore < 40) {
    recommendation = 'Focus on evidence development; early settlement may be optimal';
  } else {
    recommendation = 'Proceed with litigation; case has reasonable viability';
  }

  return {
    mtdSurvival: mtdScore,
    sjSurvival: sjScore,
    trialLikelihood,
    killRiskFlags,
    strengthBoosters,
    recommendation,
  };
}

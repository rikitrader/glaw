/**
 * Federal Pleading Engine - Complaint Drafter
 *
 * Generates Rule 8/9(b) compliant causes of action with element tables,
 * pleading checklists, and formatted complaint sections.
 */

import {
  CaseInput,
  ClaimMappingResult,
  DraftCount,
  DraftAllegation,
  ElementsTableRow,
  PleadingChecklistEntry,
  ComplaintSkeleton,
  ClaimDraftOutput,
  DefenseWarning,
  JurisdictionAnalysis,
} from './schema';
import { getClaimMetadata, CLAIM_LIBRARY } from './claim_library';
import { getElements, CLAIM_ELEMENTS } from './elements';
import { mapFactsToElements } from './mapper';
import { calculateMTDRisk } from './risk';

/**
 * Generate elements table for a claim
 */
export function generateElementsTable(claimKey: string): ElementsTableRow[] {
  const elements = getElements(claimKey);
  if (!elements) return [];

  return elements.map(element => ({
    number: element.number,
    element: element.name,
    mustAllege: element.mustAllege,
    typicalEvidence: element.typicalEvidence.join('; '),
    pitfalls: element.pitfalls,
  }));
}

/**
 * Generate pleading checklist from mapping
 */
export function generatePleadingChecklist(
  mapping: ClaimMappingResult
): PleadingChecklistEntry[] {
  return mapping.elements.map(elementMapping => ({
    elementNumber: elementMapping.elementNumber,
    elementName: elementMapping.elementName,
    facts: elementMapping.supportingFacts,
    status: elementMapping.coverage === 'full' ? 'satisfied' :
            elementMapping.coverage === 'partial' ? 'partial' : 'missing',
    notes: elementMapping.gaps.length > 0 ?
           `Missing: ${elementMapping.gaps.join('; ')}` : 'Element supported by facts',
  }));
}

/**
 * Generate draft count for a cause of action
 */
export function generateDraftCount(
  caseInput: CaseInput,
  claimKey: string,
  mapping: ClaimMappingResult,
  countNumber: number
): DraftCount {
  const metadata = getClaimMetadata(claimKey);
  const elements = getElements(claimKey);

  if (!metadata || !elements) {
    return {
      countNumber,
      title: 'Unknown Claim',
      statutoryCitation: '',
      incorporationParagraph: '',
      allegations: [],
      damagesParagraph: '',
    };
  }

  // Build allegations for each element
  const allegations: DraftAllegation[] = [];
  let paragraphNumber = 1;

  // Incorporation paragraph
  const lastParagraph = countNumber > 1 ? (countNumber - 1) * 10 : 0;

  for (const element of elements) {
    const elementMapping = mapping.elements.find(m => m.elementNumber === element.number);
    const supportingFacts = elementMapping?.supportingFacts || [];

    // Generate allegation text
    let allegationText = generateAllegationText(
      element,
      supportingFacts,
      caseInput,
      metadata.heightenedPleading
    );

    // Calculate plausibility score
    const plausibilityScore = calculatePlausibilityScore(elementMapping);

    allegations.push({
      paragraphNumber: paragraphNumber++,
      text: allegationText,
      elementAddressed: element.number,
      plausibilityScore,
      rule9bCompliant: metadata.heightenedPleading ? checkRule9bCompliance(allegationText) : undefined,
    });
  }

  // Damages paragraph
  const damagesParagraph = generateDamagesParagraph(caseInput, claimKey);

  return {
    countNumber,
    title: metadata.name,
    statutoryCitation: metadata.source,
    incorporationParagraph: lastParagraph > 0 ?
      `Plaintiff re-alleges and incorporates by reference paragraphs 1 through ${lastParagraph} as if fully set forth herein.` :
      'Plaintiff re-alleges and incorporates by reference all preceding paragraphs as if fully set forth herein.',
    allegations,
    damagesParagraph,
  };
}

/**
 * Generate allegation text for an element
 */
function generateAllegationText(
  element: { number: number; name: string; mustAllege: string; typicalEvidence: string[]; pitfalls: string },
  supportingFacts: string[],
  caseInput: CaseInput,
  heightenedPleading: boolean
): string {
  const plaintiff = caseInput.parties.plaintiffs[0]?.name || 'Plaintiff';
  const defendant = caseInput.parties.defendants[0]?.name || 'Defendant';

  if (supportingFacts.length === 0) {
    // Generate placeholder for missing facts
    return `[FACT GAP: ${element.mustAllege}]`;
  }

  // Build fact-based allegation
  let text = '';

  switch (element.name.toLowerCase()) {
    case 'state action':
    case 'state actor':
      text = `At all times relevant hereto, ${defendant} was acting under color of state law, as ${defendant} was ${getDefendantCapacityDescription(caseInput)}.`;
      break;

    case 'seizure occurred':
    case 'arrest/detention':
      const arrestFacts = supportingFacts.join('. ');
      text = `${defendant} seized ${plaintiff} by ${arrestFacts}.`;
      break;

    case 'force applied':
      const forceFacts = supportingFacts.join('. ');
      text = `${defendant} applied physical force to ${plaintiff}, specifically: ${forceFacts}.`;
      break;

    case 'objective unreasonableness':
      text = `The force used by ${defendant} was objectively unreasonable under the circumstances. Specifically, ${supportingFacts.join('. ')}. Applying the factors set forth in Graham v. Connor, 490 U.S. 386 (1989), the force was excessive because [SPECIFY GRAHAM FACTORS].`;
      break;

    case 'protected activity':
      text = `${plaintiff} engaged in constitutionally protected activity when ${plaintiff} ${supportingFacts.join('; ')}.`;
      break;

    case 'adverse action':
      text = `${defendant} took adverse action against ${plaintiff} by ${supportingFacts.join('; ')}.`;
      break;

    case 'causation':
      text = `${defendant}'s conduct was the direct and proximate cause of ${plaintiff}'s injuries. ${supportingFacts.join('. ')}.`;
      break;

    case 'injury/damages':
      text = `As a direct and proximate result of ${defendant}'s conduct, ${plaintiff} suffered injuries including ${supportingFacts.join(', ')}.`;
      break;

    default:
      // Generic element allegation
      text = `${supportingFacts.join('. ')}.`;
  }

  // Add heightened pleading details if required
  if (heightenedPleading) {
    text = enhanceForRule9b(text, caseInput);
  }

  return text;
}

/**
 * Get description of defendant's capacity
 */
function getDefendantCapacityDescription(caseInput: CaseInput): string {
  const defendant = caseInput.parties.defendants[0];
  if (!defendant) return 'a state actor';

  switch (defendant.type) {
    case 'officer':
      return `a law enforcement officer employed by ${defendant.role_title || 'a government entity'}`;
    case 'local':
      return `a local government entity`;
    case 'state':
      return `a state agency or official`;
    case 'federal':
      return `a federal government employee or agency`;
    default:
      return `acting under color of state law`;
  }
}

/**
 * Enhance allegation for Rule 9(b) compliance
 */
function enhanceForRule9b(text: string, caseInput: CaseInput): string {
  // Add who, what, when, where, how specifics
  const facts = caseInput.facts[0];
  if (!facts) return text;

  const enhancements: string[] = [];

  if (facts.date) {
    enhancements.push(`On or about ${facts.date}`);
  }
  if (facts.location) {
    enhancements.push(`at ${facts.location}`);
  }
  if (facts.actors.length > 0) {
    enhancements.push(`${facts.actors.join(' and ')}`);
  }

  if (enhancements.length > 0) {
    return `${enhancements.join(', ')}, ${text}`;
  }

  return text;
}

/**
 * Check if text meets Rule 9(b) particularity requirements
 */
function checkRule9bCompliance(text: string): boolean {
  const hasWho = /\b(defendant|plaintiff|officer|company|individual|\w+\s+\w+)\b/i.test(text);
  const hasWhat = text.length > 50; // Some substantive content
  const hasWhen = /\b(on\s+or\s+about|date|january|february|march|april|may\s+\d|june|july|august|september|october|november|december|\d{4}|\d{1,2}\/\d{1,2})\b/i.test(text);
  const hasWhere = /\b(at|in|location|address|city|state|county)\b/i.test(text);

  // Require at least 3 of 4 specifics for fraud claims
  const specifics = [hasWho, hasWhat, hasWhen, hasWhere].filter(Boolean).length;
  return specifics >= 3;
}

/**
 * Calculate plausibility score for an element mapping
 */
function calculatePlausibilityScore(
  elementMapping?: { coverage: 'full' | 'partial' | 'none'; supportingFacts: string[] }
): number {
  if (!elementMapping) return 0;

  let score = 0;

  switch (elementMapping.coverage) {
    case 'full':
      score = 80;
      break;
    case 'partial':
      score = 50;
      break;
    case 'none':
      score = 10;
      break;
  }

  // Bonus for multiple supporting facts
  if (elementMapping.supportingFacts.length >= 3) {
    score += 15;
  } else if (elementMapping.supportingFacts.length >= 2) {
    score += 10;
  }

  return Math.min(100, score);
}

/**
 * Generate damages paragraph
 */
function generateDamagesParagraph(caseInput: CaseInput, claimKey: string): string {
  const plaintiff = caseInput.parties.plaintiffs[0]?.name || 'Plaintiff';
  const defendant = caseInput.parties.defendants[0]?.name || 'Defendant';

  const damagesTypes: string[] = [];

  // Check facts for damages evidence
  for (const fact of caseInput.facts) {
    if (fact.harm) {
      damagesTypes.push(fact.harm);
    }
    if (fact.damages_estimate) {
      damagesTypes.push(`damages estimated at ${fact.damages_estimate}`);
    }
  }

  // Check relief requested
  const reliefPhrases: string[] = [];
  if (caseInput.relief_requested.includes('money')) {
    reliefPhrases.push('compensatory damages');
  }
  if (caseInput.relief_requested.includes('injunction')) {
    reliefPhrases.push('injunctive relief');
  }
  if (caseInput.relief_requested.includes('declaratory')) {
    reliefPhrases.push('declaratory relief');
  }
  if (caseInput.relief_requested.includes('fees')) {
    reliefPhrases.push('reasonable attorneys\' fees and costs');
  }

  const damagesText = damagesTypes.length > 0 ?
    damagesTypes.join(', ') : '[SPECIFY DAMAGES]';

  return `As a direct and proximate result of ${defendant}'s conduct as alleged herein, ${plaintiff} has suffered and continues to suffer damages including ${damagesText}. ${plaintiff} is entitled to ${reliefPhrases.join(', ') || '[SPECIFY RELIEF]'}.`;
}

/**
 * Generate defense warnings for a claim
 */
export function generateDefenseWarnings(
  caseInput: CaseInput,
  claimKey: string
): DefenseWarning[] {
  const metadata = getClaimMetadata(claimKey);
  if (!metadata) return [];

  const warnings: DefenseWarning[] = [];

  // Check immunities
  for (const immunity of metadata.immunities) {
    switch (immunity) {
      case 'qualified':
        warnings.push({
          type: 'Qualified Immunity',
          likelihood: 'high',
          description: 'Individual government defendants will likely raise qualified immunity defense',
          counterArguments: [
            'Right was clearly established at time of violation',
            'Cite to binding precedent with materially similar facts',
            'Argue obvious violation even without directly on-point case',
          ],
        });
        break;

      case 'sovereign':
        warnings.push({
          type: 'Sovereign Immunity',
          likelihood: 'medium',
          description: 'Federal/state government may claim sovereign immunity',
          counterArguments: [
            'Identify specific waiver statute',
            'Sue individual in personal capacity',
            'Seek prospective injunctive relief (Ex parte Young)',
          ],
        });
        break;

      case 'eleventh_amendment':
        warnings.push({
          type: 'Eleventh Amendment Immunity',
          likelihood: 'high',
          description: 'State agencies and arms of state immune from damages',
          counterArguments: [
            'Sue individual officials in personal capacity',
            'Seek prospective injunctive relief',
            'Identify congressional abrogation',
          ],
        });
        break;
    }
  }

  // Check exhaustion
  if (metadata.exhaustionRequired) {
    warnings.push({
      type: 'Exhaustion Defense',
      likelihood: caseInput.exhaustion.eeoc_charge_filed === true ||
                  caseInput.exhaustion.ftca_admin_claim_filed === true ? 'low' : 'high',
      description: `Claim requires ${metadata.exhaustionType} exhaustion before filing`,
      counterArguments: [
        'Document all exhaustion steps taken',
        'Attach administrative charge/claim to complaint',
        'If not exhausted, file administrative claim immediately',
      ],
    });
  }

  // Check heightened pleading
  if (metadata.heightenedPleading) {
    warnings.push({
      type: 'Rule 9(b) Challenge',
      likelihood: 'high',
      description: 'Fraud-based claims require heightened pleading particularity',
      counterArguments: [
        'Plead who, what, when, where, how for each misrepresentation',
        'Identify specific false statements',
        'Explain reliance and causation',
      ],
    });
  }

  // Check typical defenses
  for (const defense of metadata.typicalDefenses.slice(0, 3)) {
    if (!warnings.some(w => w.description.includes(defense.substring(0, 20)))) {
      warnings.push({
        type: 'Substantive Defense',
        likelihood: 'medium',
        description: defense,
        counterArguments: ['[Develop counter-arguments based on specific facts]'],
      });
    }
  }

  return warnings;
}

/**
 * Generate full claim draft output
 */
export function generateClaimDraftOutput(
  caseInput: CaseInput,
  claimKey: string,
  countNumber: number
): ClaimDraftOutput {
  const mapping = mapFactsToElements(caseInput, claimKey);
  const elementsTable = generateElementsTable(claimKey);
  const pleadingChecklist = generatePleadingChecklist(mapping);
  const draftCount = generateDraftCount(caseInput, claimKey, mapping, countNumber);
  const defenses = generateDefenseWarnings(caseInput, claimKey);
  const mtdRisk = calculateMTDRisk(caseInput, claimKey, mapping);

  return {
    claimKey,
    elementsTable,
    preconditions: mapping.preconditions,
    defenses,
    pleadingChecklist,
    draftCount,
    factGaps: mapping.factGaps,
    mtdRisk,
  };
}

/**
 * Generate jurisdiction analysis
 */
export function analyzeJurisdiction(caseInput: CaseInput): JurisdictionAnalysis {
  // Resolve claims - if auto_suggest, use all claims from library that match facts
  let claimsRequested = caseInput.claims_requested;
  if (claimsRequested.length === 0 || claimsRequested[0] === 'auto_suggest') {
    // Use all registered federal claims as candidates
    claimsRequested = Object.keys(CLAIM_LIBRARY);
  }

  let primaryBasis: 'federal_question' | 'diversity' | 'supplemental' = 'federal_question';
  const citations: string[] = [];

  // Check if any claims are federal question
  const hasFederalClaims = claimsRequested.some(claim => {
    const metadata = getClaimMetadata(claim);
    return metadata?.jurisdiction === 'federal_question';
  });

  // Check diversity jurisdiction
  const plaintiffStates = caseInput.parties.plaintiffs.map(p => p.citizenship);
  const defendantStates = caseInput.parties.defendants.map(d => d.citizenship);
  const completeDiversity = !plaintiffStates.some(ps =>
    defendantStates.includes(ps)
  );

  // Check amount in controversy for diversity (estimate from damages)
  const totalDamagesEstimate = caseInput.facts.reduce((sum, f) => {
    if (f.damages_estimate) {
      const numericValue = parseFloat(f.damages_estimate.replace(/[^0-9.]/g, ''));
      return sum + (isNaN(numericValue) ? 0 : numericValue);
    }
    return sum;
  }, 0);
  const meetsAmountInControversy = totalDamagesEstimate > 75000;

  if (hasFederalClaims) {
    primaryBasis = 'federal_question';
    citations.push('28 U.S.C. § 1331');
    if (completeDiversity && meetsAmountInControversy) {
      citations.push('28 U.S.C. § 1332 (alternative basis)');
    }
  } else if (completeDiversity && meetsAmountInControversy) {
    primaryBasis = 'diversity';
    citations.push('28 U.S.C. § 1332');
  } else if (completeDiversity && !meetsAmountInControversy) {
    primaryBasis = 'diversity';
    citations.push('28 U.S.C. § 1332');
    // Will be flagged as unsatisfied below
  }

  const subjectMatterSatisfied = hasFederalClaims || (completeDiversity && meetsAmountInControversy);

  let subjectMatterAnalysis: string;
  if (hasFederalClaims) {
    subjectMatterAnalysis = 'Federal question jurisdiction exists because claims arise under federal law.';
  } else if (completeDiversity && meetsAmountInControversy) {
    subjectMatterAnalysis = 'Diversity jurisdiction exists because parties are citizens of different states and amount in controversy exceeds $75,000.';
  } else if (completeDiversity && !meetsAmountInControversy) {
    subjectMatterAnalysis = `WARNING: Complete diversity exists but amount in controversy ($${totalDamagesEstimate.toLocaleString()}) may not exceed $75,000 threshold. Verify damages exceed jurisdictional minimum.`;
  } else {
    subjectMatterAnalysis = 'WARNING: No federal question claims identified and complete diversity does not exist. Subject matter jurisdiction may be lacking.';
  }

  // Personal jurisdiction analysis - evaluate defendant connections to forum
  const courtState = caseInput.court.state.toLowerCase();
  const defendantInForum = caseInput.parties.defendants.some(d =>
    d.citizenship.toLowerCase() === courtState
  );
  const eventsInForum = caseInput.facts.some(f =>
    f.location?.toLowerCase().includes(courtState)
  );
  const defendantIsGovernment = caseInput.parties.defendants.some(d =>
    ['local', 'state', 'federal', 'officer'].includes(d.type)
  );

  let pjSatisfied: boolean;
  let pjBasis: 'general' | 'specific' | 'consent';
  let pjAnalysis: string;

  if (defendantInForum) {
    pjSatisfied = true;
    pjBasis = 'general';
    pjAnalysis = 'Defendant is domiciled/located in this forum state, establishing general jurisdiction.';
  } else if (eventsInForum) {
    pjSatisfied = true;
    pjBasis = 'specific';
    pjAnalysis = 'Specific jurisdiction exists because the claims arise from events occurring in this forum.';
  } else if (defendantIsGovernment) {
    pjSatisfied = true;
    pjBasis = 'specific';
    pjAnalysis = 'Government defendant is subject to jurisdiction where its employees acted under color of law.';
  } else {
    pjSatisfied = false;
    pjBasis = 'specific';
    pjAnalysis = 'WARNING: Personal jurisdiction may be lacking. Defendant does not appear domiciled in this forum and events may not have occurred here. Verify minimum contacts with forum state.';
  }

  // Venue analysis - check all three statutory bases
  const venueDefendantResides = caseInput.parties.defendants.some(d =>
    d.citizenship.toLowerCase() === courtState
  );
  const venueEventsOccurred = caseInput.facts.some(f =>
    f.location?.toLowerCase().includes(courtState)
  );
  const venueProper = venueDefendantResides || venueEventsOccurred;

  let venueBasis: string;
  let venueAnalysis: string;
  if (venueEventsOccurred) {
    venueBasis = '28 U.S.C. § 1391(b)(2)';
    venueAnalysis = 'Venue is proper because a substantial part of the events or omissions giving rise to the claims occurred in this district.';
  } else if (venueDefendantResides) {
    venueBasis = '28 U.S.C. § 1391(b)(1)';
    venueAnalysis = 'Venue is proper because defendant resides in this judicial district.';
  } else {
    venueBasis = '28 U.S.C. § 1391(b)';
    venueAnalysis = 'WARNING: Venue may be improper. Neither events nor defendant residence clearly connect to this district. Consider § 1391(b)(3) fallback if no other district is appropriate.';
  }

  // Standing analysis
  const hasInjury = caseInput.facts.some(f => f.harm && f.harm.length > 0);
  const hasCausation = caseInput.facts.length > 0;
  const reliefRequested = caseInput.relief_requested.length > 0;

  return {
    subjectMatter: {
      basis: primaryBasis,
      satisfied: subjectMatterSatisfied,
      analysis: subjectMatterAnalysis,
      citations,
    },
    personalJurisdiction: {
      satisfied: pjSatisfied,
      basis: pjBasis,
      analysis: pjAnalysis,
    },
    venue: {
      proper: venueProper,
      basis: venueBasis,
      analysis: venueAnalysis,
    },
    standing: {
      injuryInFact: hasInjury,
      causation: hasCausation,
      redressability: reliefRequested,
      analysis: hasInjury && hasCausation && reliefRequested ?
        'Standing requirements appear satisfied.' :
        'Standing analysis requires additional fact development.',
    },
  };
}

/**
 * Generate complete complaint skeleton
 */
export function generateComplaintSkeleton(
  caseInput: CaseInput,
  claimOutputs: ClaimDraftOutput[]
): ComplaintSkeleton {
  const plaintiff = caseInput.parties.plaintiffs[0]?.name || '[PLAINTIFF]';
  const defendant = caseInput.parties.defendants[0]?.name || '[DEFENDANT]';

  // Caption
  const caption = `
UNITED STATES DISTRICT COURT
${caseInput.court.district.toUpperCase()}
${caseInput.court.division.toUpperCase()} DIVISION

${plaintiff.toUpperCase()},
                                    Plaintiff,

v.                                              Case No. __________

${defendant.toUpperCase()},
                                    Defendant.
_______________________________________/
`;

  // Parties section
  const partiesSection = generatePartiesSection(caseInput);

  // Jurisdiction section
  const jurisdictionAnalysis = analyzeJurisdiction(caseInput);
  const jurisdictionSection = generateJurisdictionSection(caseInput, jurisdictionAnalysis);

  // Venue section
  const venueSection = generateVenueSection(caseInput);

  // General allegations
  const generalAllegations = generateGeneralAllegations(caseInput);

  // Counts from claim outputs
  const counts = claimOutputs.map(co => co.draftCount);

  // Prayer for relief
  const prayerForRelief = generatePrayerForRelief(caseInput);

  // Jury demand
  const juryDemand = true; // Default to jury trial

  return {
    caption,
    partiesSection,
    jurisdictionSection,
    venueSection,
    generalAllegations,
    counts,
    prayerForRelief,
    juryDemand,
    certificateOfService: generateCertificateOfService(),
  };
}

function generatePartiesSection(caseInput: CaseInput): string {
  const lines: string[] = ['PARTIES'];

  caseInput.parties.plaintiffs.forEach((p, i) => {
    lines.push(`\n     ${i + 1}. Plaintiff ${p.name} is ${getPartyDescription(p)}.`);
  });

  caseInput.parties.defendants.forEach((d, i) => {
    const num = caseInput.parties.plaintiffs.length + i + 1;
    lines.push(`\n     ${num}. Defendant ${d.name} is ${getDefendantDescription(d)}.`);
  });

  return lines.join('');
}

function getPartyDescription(party: { entity_type: string; citizenship: string; residence?: string }): string {
  switch (party.entity_type) {
    case 'individual':
      return `a citizen of the State of ${party.citizenship}, residing at ${party.residence || '[ADDRESS]'}`;
    case 'corporation':
      return `a corporation organized under the laws of [STATE OF INCORPORATION] with its principal place of business in ${party.citizenship}`;
    case 'llc':
      return `a limited liability company organized under the laws of [STATE], with its member(s) being citizens of ${party.citizenship}`;
    default:
      return `an entity located in ${party.citizenship}`;
  }
}

function getDefendantDescription(defendant: {
  type: string;
  entity_type: string;
  citizenship: string;
  capacity: string;
  role_title?: string;
}): string {
  switch (defendant.type) {
    case 'officer':
      return `an individual who, at all relevant times, was employed as ${defendant.role_title || 'a government official'}, sued in ${defendant.capacity === 'both' ? 'both individual and official' : defendant.capacity} capacity`;
    case 'local':
      return `a municipal corporation organized under the laws of ${defendant.citizenship}`;
    case 'state':
      return `a state agency of ${defendant.citizenship}`;
    case 'federal':
      return `a federal agency of the United States`;
    default:
      return getPartyDescription(defendant);
  }
}

function generateJurisdictionSection(
  caseInput: CaseInput,
  analysis: JurisdictionAnalysis
): string {
  return `JURISDICTION

     This Court has subject matter jurisdiction pursuant to ${analysis.subjectMatter.citations.join(' and ')} because ${analysis.subjectMatter.analysis}`;
}

function generateVenueSection(caseInput: CaseInput): string {
  return `VENUE

     Venue is proper in this District pursuant to 28 U.S.C. § 1391(b) because a substantial part of the events or omissions giving rise to the claims occurred in this District.`;
}

function generateGeneralAllegations(caseInput: CaseInput): string[] {
  const allegations: string[] = ['FACTUAL ALLEGATIONS'];

  caseInput.facts.forEach((fact, i) => {
    let text = '';
    if (fact.date) {
      text += `On or about ${fact.date}, `;
    }
    if (fact.location) {
      text += `at ${fact.location}, `;
    }
    text += fact.event;
    if (fact.harm) {
      text += `. As a result, ${fact.harm}`;
    }
    allegations.push(`     ${i + 1}. ${text}.`);
  });

  return allegations;
}

function generatePrayerForRelief(caseInput: CaseInput): string {
  const reliefItems: string[] = [];

  if (caseInput.relief_requested.includes('money')) {
    reliefItems.push('Compensatory damages in an amount to be determined at trial');
    reliefItems.push('Punitive damages in an amount to be determined at trial');
  }
  if (caseInput.relief_requested.includes('injunction')) {
    reliefItems.push('Preliminary and permanent injunctive relief');
  }
  if (caseInput.relief_requested.includes('declaratory')) {
    reliefItems.push('A declaratory judgment');
  }
  reliefItems.push('Pre-judgment and post-judgment interest');
  if (caseInput.relief_requested.includes('fees')) {
    reliefItems.push('Reasonable attorneys\' fees and costs');
  }
  reliefItems.push('Such other and further relief as this Court deems just and proper');

  return `PRAYER FOR RELIEF

     WHEREFORE, Plaintiff respectfully requests that this Court enter judgment in Plaintiff's favor as follows:

${reliefItems.map((r, i) => `     ${String.fromCharCode(97 + i)}. ${r};`).join('\n')}`;
}

function generateCertificateOfService(): string {
  return `CERTIFICATE OF SERVICE

     I hereby certify that on [DATE], I electronically filed the foregoing with the Clerk of Court using the CM/ECF system, which will send notification of such filing to all counsel of record.

                                        /s/ [ATTORNEY NAME]
                                        [ATTORNEY NAME]
                                        Attorney for Plaintiff`;
}

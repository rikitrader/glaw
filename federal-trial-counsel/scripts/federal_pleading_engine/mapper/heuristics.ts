/**
 * Federal Pleading Engine - Matching & Scoring Heuristics
 *
 * Internal helpers that:
 *  - Resolve keyword lists for a given element name (getKeywordsForElement)
 *  - Match facts against element keywords and compute coverage
 *    (mapElementToFacts)
 *  - Score a claim's fact-pattern relevance for auto-suggest
 *    (scoreClaimFactPatterns)
 *
 * These helpers are not part of the public mapper API; they're consumed
 * only by mapper.ts orchestration.
 */

import { FactEntry, FactElementMapping } from '../schema';
import { ELEMENT_KEYWORDS } from './keywords';

/**
 * Get keywords associated with an element name
 */
export function getKeywordsForElement(elementName: string): string[] {
  const normalizedName = elementName.toLowerCase().replace(/[^a-z]/g, '_');

  // Check direct matches
  for (const [key, keywords] of Object.entries(ELEMENT_KEYWORDS)) {
    if (normalizedName.includes(key) || key.includes(normalizedName.substring(0, 5))) {
      return keywords;
    }
  }

  // Fallback: extract key terms from element name
  const terms = elementName.toLowerCase().split(/\s+/);
  const relevantTerms: string[] = [];

  for (const term of terms) {
    if (term.length > 3 && !['the', 'and', 'for', 'was', 'were', 'that', 'with'].includes(term)) {
      relevantTerms.push(term);
    }
  }

  return relevantTerms;
}

/**
 * Map a single element to matching facts
 */
export function mapElementToFacts(
  element: { number: number; name: string; mustAllege: string; typicalEvidence: string[]; pitfalls: string },
  facts: FactEntry[]
): FactElementMapping {
  const matchingFactIndices: number[] = [];
  const supportingFacts: string[] = [];
  const gaps: string[] = [];

  // Get keywords for this element type
  const keywords = getKeywordsForElement(element.name);

  // Check each fact for matches
  facts.forEach((fact, index) => {
    const factText = `${fact.event} ${fact.harm} ${fact.actors.join(' ')} ${fact.documents.join(' ')}`.toLowerCase();

    const hasMatch = keywords.some(keyword => {
      const escaped = keyword.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return new RegExp(`\\b${escaped}\\b`, 'i').test(factText);
    });

    if (hasMatch) {
      matchingFactIndices.push(index);
      supportingFacts.push(fact.event);
    }
  });

  // Determine coverage level
  let coverage: 'full' | 'partial' | 'none';
  if (matchingFactIndices.length >= 2) {
    coverage = 'full';
  } else if (matchingFactIndices.length === 1) {
    coverage = 'partial';
  } else {
    coverage = 'none';
    gaps.push(element.mustAllege);
  }

  return {
    elementNumber: element.number,
    elementName: element.name,
    factIndices: matchingFactIndices,
    coverage,
    supportingFacts,
    gaps,
  };
}

/**
 * Score a claim's relevance based on fact patterns in the
 * concatenated/normalized fact text. Returns additive score delta
 * and human-readable reasons.
 *
 * NOTE: Behavior is identical to the inline regex ladder that lived
 * in mapper.ts before the split. Do not re-order or tweak thresholds.
 */
export function scoreClaimFactPatterns(
  claimKey: string,
  category: string,
  allFacts: string
): { scoreDelta: number; reasons: string[] } {
  let scoreDelta = 0;
  const reasons: string[] = [];

  // === Force / Excessive Force ===
  if (/\b(force|beat|shot|tased|pepper.?spray|punched|kicked|slammed|choked|struck|baton|tackled)\b/.test(allFacts)) {
    if (claimKey.includes('excessive_force')) {
      scoreDelta += 30;
      reasons.push('Force-related facts detected');
    }
  }

  // === Arrest / Detention / False Arrest ===
  if (/\b(arrest|detained|seized|handcuffed|custody|taken.?into|booked|jailed)\b/.test(allFacts)) {
    if (claimKey.includes('false_arrest')) {
      scoreDelta += 30;
      reasons.push('Arrest/detention facts detected');
    }
  }

  // === Search / Seizure ===
  if (/\b(search|warrant|entered|confiscated|seized.?property|searched|raided|pat.?down|strip.?search)\b/.test(allFacts)) {
    if (claimKey.includes('unlawful_search_seizure') || claimKey === 'bivens_fourth_search_seizure') {
      scoreDelta += 30;
      reasons.push('Search/seizure facts detected');
    }
  }

  // === Employment Adverse Action ===
  if (/\b(fired|terminated|demoted|suspended|laid.?off|not.?promoted|disciplined|written.?up|transferred)\b/.test(allFacts)) {
    if (category === 'employment') {
      scoreDelta += 25;
      reasons.push('Employment adverse action detected');
    }
  }

  // === Discrimination ===
  if (/\b(discriminat|because.?of|race|gender|sex|national.?origin|religion|color|protected.?class)\b/.test(allFacts)) {
    if (claimKey.includes('title_vii') || claimKey.includes('equal_protection') ||
        claimKey.includes('adea') || claimKey.includes('ada_title')) {
      scoreDelta += 25;
      reasons.push('Discrimination language detected');
    }
  }

  // === Harassment / Hostile Work Environment ===
  if (/\b(harass|hostile|offensive|slur|grop|intimidat|unwelcome|severe.?and.?pervasive)\b/.test(allFacts)) {
    if (claimKey.includes('hostile_work_environment')) {
      scoreDelta += 30;
      reasons.push('Harassment/hostile environment facts detected');
    }
  }

  // === Retaliation ===
  if (/\b(retaliat|complained|reported|whistleblow|filed.?complaint|protected.?activity|adverse.?after)\b/.test(allFacts)) {
    if (claimKey.includes('retaliation')) {
      scoreDelta += 30;
      reasons.push('Retaliation facts detected');
    }
  }

  // === Speech / First Amendment ===
  if (/\b(speech|spoke|protest|public.?concern|silence|censor|viewpoint|expression|petition)\b/.test(allFacts)) {
    if (claimKey.includes('first_amendment')) {
      scoreDelta += 25;
      reasons.push('First Amendment / speech facts detected');
    }
  }

  // === Due Process ===
  if (/\b(hearing|notice|without.?process|license.?revoked|property.?taken|deprive|no.?hearing|terminated.?without)\b/.test(allFacts)) {
    if (claimKey.includes('due_process') || claimKey.includes('procedural_due') || claimKey.includes('substantive_due')) {
      scoreDelta += 25;
      reasons.push('Due process facts detected');
    }
  }

  // === Age Discrimination ===
  if (/\b(age|older|younger.?worker|over.?40|replaced.?by.?younger|too.?old)\b/.test(allFacts)) {
    if (claimKey.includes('adea')) {
      scoreDelta += 25;
      reasons.push('Age discrimination facts detected');
    }
  }

  // === Disability / ADA ===
  if (/\b(disabilit|accommodat|wheelchair|impairment|ada|medical.?condition|reasonable.?modification)\b/.test(allFacts)) {
    if (claimKey.includes('ada_title')) {
      scoreDelta += 25;
      reasons.push('Disability/accommodation facts detected');
    }
  }

  // === FMLA / Medical Leave ===
  if (/\b(fmla|medical.?leave|family.?leave|maternity|paternity|serious.?health|leave.?request)\b/.test(allFacts)) {
    if (claimKey.includes('fmla')) {
      scoreDelta += 30;
      reasons.push('FMLA/medical leave facts detected');
    }
  }

  // === Wages / FLSA ===
  if (/\b(unpaid|overtime|minimum.?wage|hours.?worked|wages|off.?the.?clock|misclassif|exempt)\b/.test(allFacts)) {
    if (claimKey.includes('flsa')) {
      scoreDelta += 30;
      reasons.push('Wage/overtime facts detected');
    }
  }

  // === FTCA / Federal Negligence ===
  if (/\b(negligent|careless|failed.?to|should.?have|malpractice|va.?hospital|federal.?hospital)\b/.test(allFacts)) {
    if (claimKey.includes('ftca')) {
      scoreDelta += 20;
      reasons.push('Negligence/FTCA facts detected');
    }
  }

  // === Medical Malpractice ===
  if (/\b(medical|hospital|treatment|surgery|doctor|nurse|misdiagnos|standard.?of.?care|patient)\b/.test(allFacts)) {
    if (claimKey.includes('medical_malpractice')) {
      scoreDelta += 25;
      reasons.push('Medical malpractice facts detected');
    }
  }

  // === Wrongful Death ===
  if (/\b(death|died|killed|fatal|decedent|surviving|wrongful.?death)\b/.test(allFacts)) {
    if (claimKey.includes('wrongful_death')) {
      scoreDelta += 30;
      reasons.push('Wrongful death facts detected');
    }
  }

  // === Monell / Municipal Policy ===
  if (/\b(policy|custom|training|pattern|widespread|failure.?to.?train|deliberate.?indifference|policymaker)\b/.test(allFacts)) {
    if (claimKey.includes('monell')) {
      scoreDelta += 25;
      reasons.push('Municipal policy/custom facts detected');
    }
  }

  // === Conspiracy (§ 1985) ===
  if (/\b(conspir|agreed|coordinated|concerted.?action|acting.?together|colluded|joint.?action)\b/.test(allFacts)) {
    if (claimKey.includes('1985_conspiracy') || claimKey.includes('1986_failure')) {
      scoreDelta += 20;
      reasons.push('Conspiracy facts detected');
    }
  }

  // === Federal Employee / Bivens ===
  if (/\b(federal.?officer|federal.?agent|federal.?employee|fbi|ice|dea|atf|cbp|usms|bop|irs.?agent|secret.?service)\b/.test(allFacts)) {
    if (category === 'bivens') {
      scoreDelta += 25;
      reasons.push('Federal actor identified — Bivens applicable');
    }
    if (claimKey.includes('ftca')) {
      scoreDelta += 15;
      reasons.push('Federal employee — FTCA may apply');
    }
  }

  // === Prison / Eighth Amendment ===
  if (/\b(prison|inmate|jail|correctional|conditions.?of|cell|lockdown|solitary|medical.?care|deliberate.?indifference)\b/.test(allFacts)) {
    if (claimKey.includes('eighth') || claimKey.includes('deliberate_indifference')) {
      scoreDelta += 25;
      reasons.push('Prison/conditions of confinement facts detected');
    }
  }

  // === Habeas ===
  if (/\b(habeas|detention|custody|immigration.?detention|unlawful.?imprisonment|release|parole|sentence)\b/.test(allFacts)) {
    if (claimKey.includes('habeas')) {
      scoreDelta += 25;
      reasons.push('Detention/habeas facts detected');
    }
  }

  // === APA / Agency Delay ===
  if (/\b(agency|petition|visa|immigration|unreasonable.?delay|application.?pending|adjudicat|final.?action|withholding)\b/.test(allFacts)) {
    if (claimKey.includes('apa_') || claimKey.includes('mandamus')) {
      scoreDelta += 20;
      reasons.push('Administrative delay/agency action facts detected');
    }
  }

  // === RICO / Enterprise ===
  if (/\b(enterprise|racketeering|pattern|scheme|predicate.?acts|mail.?fraud|wire.?fraud|ongoing.?criminal)\b/.test(allFacts)) {
    if (claimKey.includes('rico')) {
      scoreDelta += 25;
      reasons.push('RICO/enterprise facts detected');
    }
  }

  // === False Claims / Qui Tam / Whistleblower ===
  if (/\b(false.?claim|qui.?tam|whistleblower|government.?fraud|billing.?fraud|medicare.?fraud|overbill|kickback)\b/.test(allFacts)) {
    if (claimKey.includes('false_claims_act')) {
      scoreDelta += 30;
      reasons.push('False claims/whistleblower facts detected');
    }
  }

  // === Antitrust ===
  if (/\b(antitrust|monopol|price.?fix|restraint.?of.?trade|market.?power|cartel|bid.?rig|boycott|tying)\b/.test(allFacts)) {
    if (claimKey.includes('antitrust_sherman') || claimKey.includes('sherman')) {
      scoreDelta += 25;
      reasons.push('Antitrust facts detected');
    }
  }

  // === Trademark / Lanham Act ===
  if (/\b(trademark|brand|confusion|counterfeit|trade.?dress|infring.*mark|knock.?off|dilution)\b/.test(allFacts)) {
    if (claimKey.includes('lanham') || claimKey.includes('trademark')) {
      scoreDelta += 25;
      reasons.push('Trademark infringement facts detected');
    }
  }

  // === Copyright ===
  if (/\b(copyright|copied|pirat|reproduction|derivative.?work|dmca|infring.*work|original.?work)\b/.test(allFacts)) {
    if (claimKey.includes('copyright')) {
      scoreDelta += 25;
      reasons.push('Copyright infringement facts detected');
    }
  }

  // === Patent ===
  if (/\b(patent|invent|claim.?chart|infring.*patent|prior.?art|prosecution|patent.?holder)\b/.test(allFacts)) {
    if (claimKey.includes('patent')) {
      scoreDelta += 25;
      reasons.push('Patent infringement facts detected');
    }
  }

  // === FCRA / Credit Reporting ===
  if (/\b(credit.?report|inaccurate.?report|credit.?score|furnisher|consumer.?report|dispute.*credit|equifax|experian|transunion)\b/.test(allFacts)) {
    if (claimKey.includes('fcra')) {
      scoreDelta += 25;
      reasons.push('Credit reporting violation facts detected');
    }
  }

  // === FDCPA / Debt Collection ===
  if (/\b(debt.?collect|harassing.?calls|collection.?letter|cease.?and.?desist|third.?party.?disclosure|validation.?notice)\b/.test(allFacts)) {
    if (claimKey.includes('fdcpa')) {
      scoreDelta += 25;
      reasons.push('Debt collection violation facts detected');
    }
  }

  // === TILA / Lending ===
  if (/\b(lending|loan|apr|interest.?rate|disclosure|truth.?in.?lending|rescission|finance.?charge|annual.?percentage)\b/.test(allFacts)) {
    if (claimKey.includes('tila')) {
      scoreDelta += 25;
      reasons.push('Lending disclosure violation facts detected');
    }
  }

  // === ERISA / Benefits ===
  if (/\b(erisa|benefits|plan.?denied|long.?term.?disability|pension|401k|fiduciary|claim.?denied|insurance.?denied)\b/.test(allFacts)) {
    if (claimKey.includes('erisa')) {
      scoreDelta += 25;
      reasons.push('ERISA/benefits facts detected');
    }
  }

  // === Tax / IRS ===
  if (/\b(tax|irs|refund|levy|lien|assessment|taxpayer|collection|internal.?revenue)\b/.test(allFacts)) {
    if (claimKey.includes('tax_')) {
      scoreDelta += 20;
      reasons.push('Tax dispute facts detected');
    }
  }

  return { scoreDelta, reasons };
}

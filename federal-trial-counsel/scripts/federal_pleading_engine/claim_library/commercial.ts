/**
 * Federal Pleading Engine - Commercial / Fraud / Antitrust / FCA / RICO / IP Claims
 *
 * False Claims Act, RICO, Sherman Act, Lanham Act, Copyright, and Patent claims.
 */

import { ClaimMetadata } from '../schema';

export const COMMERCIAL_CLAIMS: Record<string, ClaimMetadata> = {
  'false_claims_act_qui_tam': {
    name: 'False Claims Act - Qui Tam',
    category: 'commercial',
    source: '31 U.S.C. § 3730(b)',
    sourceType: 'statute',
    heightenedPleading: true,  // Rule 9(b) applies
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'Public disclosure bar',
      'First-to-file bar',
      'No false claim submitted',
      'No scienter (knowledge)',
      'Government knowledge',
      'Materiality lacking',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '6 years from violation; 3 years from discovery',
    viabilityWarning: 'VERIFY: Must file under seal. Government must be served. First-to-file and public disclosure bars apply.',
  },

  'rico_1962c': {
    name: 'RICO - Pattern of Racketeering (§ 1962(c))',
    category: 'commercial',
    source: '18 U.S.C. § 1962(c)',
    sourceType: 'statute',
    heightenedPleading: true,  // If predicate is fraud
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No enterprise',
      'No pattern (continuity + relationship)',
      'No predicate acts',
      'No injury to business or property',
      'No proximate causation',
      'Rule 9(b) particularity lacking',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '4 years from discovery of injury',
  },

  'rico_1962d_conspiracy': {
    name: 'RICO - Conspiracy (§ 1962(d))',
    category: 'commercial',
    source: '18 U.S.C. § 1962(d)',
    sourceType: 'statute',
    heightenedPleading: true,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No underlying RICO violation',
      'No agreement to participate',
      'No knowledge of pattern',
      'Withdrawal from conspiracy',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '4 years from discovery of injury',
  },

  'antitrust_sherman_section_1': {
    name: 'Sherman Act § 1 - Restraint of Trade',
    category: 'commercial',
    source: '15 U.S.C. § 1',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No agreement (unilateral conduct)',
      'Rule of reason analysis (procompetitive justification)',
      'No antitrust injury',
      'State action immunity',
      'Noerr-Pennington doctrine',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '4 years',
  },

  'antitrust_sherman_section_2': {
    name: 'Sherman Act § 2 - Monopolization',
    category: 'commercial',
    source: '15 U.S.C. § 2',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No monopoly power',
      'No anticompetitive conduct',
      'Superior product/skill/foresight',
      'No antitrust injury',
      'State action immunity',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '4 years',
  },

  'lanham_trademark_infringement': {
    name: 'Lanham Act - Trademark Infringement',
    category: 'commercial',
    source: '15 U.S.C. § 1114',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No likelihood of confusion',
      'Fair use (descriptive, nominative)',
      'Abandonment',
      'Laches/acquiescence',
      'First Amendment (expressive works)',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'None (but laches applies)',
  },

  'copyright_infringement': {
    name: 'Copyright Infringement',
    category: 'commercial',
    source: '17 U.S.C. § 501',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,  // Registration required for suit
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'No valid copyright',
      'No copying (independent creation)',
      'Fair use',
      'License/permission',
      'De minimis use',
      'Statute of limitations (3 years)',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '3 years from infringement',
  },

  'patent_infringement': {
    name: 'Patent Infringement',
    category: 'commercial',
    source: '35 U.S.C. § 271',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Invalidity (anticipation, obviousness)',
      'Non-infringement',
      'Exhaustion',
      'License/permission',
      'Inequitable conduct',
      'Laches/equitable estoppel',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '6 years (damages limitation)',
    viabilityWarning: 'VERIFY: Special venue requirements under TC Heartland. Patent must be issued and valid.',
  },
};

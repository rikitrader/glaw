/**
 * Federal Pleading Engine - Employment / Civil Rights Statutes
 *
 * Title VII, ADEA, ADA Title I, FMLA, and FLSA employment claims.
 */

import { ClaimMetadata } from '../schema';

export const EMPLOYMENT_CLAIMS: Record<string, ClaimMetadata> = {
  'title_vii_disparate_treatment': {
    name: 'Title VII - Disparate Treatment',
    category: 'employment',
    source: '42 U.S.C. § 2000e-2',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'eeoc',
    immunities: ['eleventh_amendment'],  // For state employers
    typicalDefenses: [
      'Failure to exhaust (no EEOC charge)',
      'EEOC charge untimely (180/300 days)',
      'Legitimate non-discriminatory reason',
      'Same actor inference',
      'Comparators not similarly situated',
      'Insufficient evidence of pretext',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '90 days from right-to-sue letter',
  },

  'title_vii_hostile_work_environment': {
    name: 'Title VII - Hostile Work Environment',
    category: 'employment',
    source: '42 U.S.C. § 2000e-2',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'eeoc',
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Failure to exhaust',
      'Not severe or pervasive',
      'Not based on protected class',
      'Faragher/Ellerth defense (supervisor harassment)',
      'Prompt remedial action taken',
      'Plaintiff unreasonably failed to report',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '90 days from right-to-sue letter',
  },

  'title_vii_retaliation': {
    name: 'Title VII - Retaliation',
    category: 'employment',
    source: '42 U.S.C. § 2000e-3',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'eeoc',
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Failure to exhaust',
      'No protected activity',
      'No materially adverse action',
      'No causal connection',
      'Same decision regardless',
      'Temporal proximity insufficient alone',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '90 days from right-to-sue letter',
  },

  'adea_age_discrimination': {
    name: 'ADEA - Age Discrimination',
    category: 'employment',
    source: '29 U.S.C. § 621 et seq.',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'eeoc',
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Failure to exhaust',
      'Plaintiff under 40',
      'RFOA (reasonable factor other than age)',
      'Bona fide occupational qualification',
      'Same actor inference',
      'Legitimate non-discriminatory reason',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '90 days from right-to-sue; 60 days after filing charge',
  },

  'ada_title_i_employment_disability': {
    name: 'ADA Title I - Disability Discrimination',
    category: 'employment',
    source: '42 U.S.C. § 12112',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'eeoc',
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Failure to exhaust',
      'Not a qualified individual',
      'No disability under ADA',
      'Cannot perform essential functions',
      'Undue hardship for accommodation',
      'Direct threat defense',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '90 days from right-to-sue letter',
  },

  'fmla_interference': {
    name: 'FMLA - Interference',
    category: 'employment',
    source: '29 U.S.C. § 2615(a)(1)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Employer has fewer than 50 employees',
      'Employee not eligible (1 year, 1,250 hours)',
      'Not a serious health condition',
      'Employee would have been terminated anyway',
      'Employee failed to provide adequate notice',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years (3 years for willful violations)',
  },

  'fmla_retaliation': {
    name: 'FMLA - Retaliation',
    category: 'employment',
    source: '29 U.S.C. § 2615(a)(2)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Employer has fewer than 50 employees',
      'Employee not eligible',
      'No causal connection',
      'Same decision regardless of FMLA use',
      'Legitimate non-retaliatory reason',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years (3 years for willful violations)',
  },

  'flsa_unpaid_wages_overtime': {
    name: 'FLSA - Unpaid Wages/Overtime',
    category: 'employment',
    source: '29 U.S.C. § 201 et seq.',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['eleventh_amendment'],
    typicalDefenses: [
      'Employee exempt (executive, administrative, professional)',
      'Independent contractor',
      'Not engaged in commerce',
      'Good faith defense (liquidated damages)',
      'SOL expired',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years (3 years for willful violations)',
  },
};

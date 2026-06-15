/**
 * Federal Pleading Engine - Administrative / APA / Mandamus / Habeas Claims
 *
 * Claims challenging federal agency action, compelling ministerial duties,
 * and challenging detention.
 */

import { ClaimMetadata } from '../schema';

export const ADMINISTRATIVE_CLAIMS: Record<string, ClaimMetadata> = {
  'apa_arbitrary_capricious': {
    name: 'APA - Arbitrary and Capricious Agency Action',
    category: 'administrative',
    source: '5 U.S.C. § 706(2)(A)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'apa_final_action',
    immunities: ['sovereign'],  // Waived for non-monetary relief
    typicalDefenses: [
      'No final agency action',
      'Committed to agency discretion',
      'Plaintiff not within zone of interests',
      'Agency action reasonable',
      'Adequate explanation provided',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '6 years (28 U.S.C. § 2401)',
  },

  'apa_unlawful_withholding_unreasonable_delay': {
    name: 'APA - Unlawful Withholding/Unreasonable Delay',
    category: 'administrative',
    source: '5 U.S.C. § 706(1)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'apa_final_action',
    immunities: ['sovereign'],
    typicalDefenses: [
      'No discrete action unlawfully withheld',
      'Agency proceeding reasonably',
      'Complex matter requiring time',
      'TRAC factors favor agency',
      'No statutory deadline',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'None (but laches may apply)',
  },

  'mandamus_compel_ministerial_duty': {
    name: 'Mandamus - Compel Ministerial Duty',
    category: 'administrative',
    source: '28 U.S.C. § 1361',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['sovereign'],
    typicalDefenses: [
      'Duty is discretionary, not ministerial',
      'No clear right to relief',
      'Adequate alternative remedy exists',
      'Plaintiff lacks standing',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'None (but laches may apply)',
  },

  'habeas_detention_challenge': {
    name: 'Habeas Corpus - Challenge to Detention',
    category: 'administrative',
    source: '28 U.S.C. § 2241',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'administrative',
    immunities: ['sovereign'],
    typicalDefenses: [
      'Failure to exhaust administrative remedies',
      'Improper custody',
      'AEDPA time bar (conviction challenges)',
      'Successive petition bar',
      'Procedural default',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'Varies; 1 year for conviction challenges',
  },
};

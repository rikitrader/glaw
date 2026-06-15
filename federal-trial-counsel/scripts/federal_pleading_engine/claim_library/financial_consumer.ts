/**
 * Federal Pleading Engine - Financial / Consumer Protection Claims
 *
 * FCRA, FDCPA, and TILA claims.
 */

import { ClaimMetadata } from '../schema';

export const FINANCIAL_CONSUMER_CLAIMS: Record<string, ClaimMetadata> = {
  'fcra_inaccurate_reporting': {
    name: 'FCRA - Inaccurate Credit Reporting',
    category: 'financial_consumer',
    source: '15 U.S.C. § 1681 et seq.',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'Information was accurate',
      'Reasonable procedures followed',
      'No willfulness (statutory damages)',
      'Plaintiff failed to dispute',
      'No damages suffered',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years from discovery; 5 years absolute',
  },

  'fdcpa_prohibited_practices': {
    name: 'FDCPA - Prohibited Debt Collection Practices',
    category: 'financial_consumer',
    source: '15 U.S.C. § 1692 et seq.',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'Defendant is not a debt collector',
      'Plaintiff is not a consumer',
      'Not a consumer debt',
      'Bona fide error defense',
      'SOL expired (1 year)',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '1 year from violation',
  },

  'tila_disclosure_violations': {
    name: 'TILA - Disclosure Violations',
    category: 'financial_consumer',
    source: '15 U.S.C. § 1601 et seq.',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: [],
    typicalDefenses: [
      'No material disclosure violation',
      'Bona fide error',
      'SOL expired (1 year for damages)',
      'No actual damages',
      'Right of rescission waived',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '1 year for damages; 3 years for rescission',
  },
};

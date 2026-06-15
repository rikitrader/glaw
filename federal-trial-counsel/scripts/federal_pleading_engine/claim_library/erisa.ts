/**
 * Federal Pleading Engine - ERISA Claims
 *
 * ERISA § 502(a)(1)(B) denial of benefits and § 502(a)(3) equitable relief claims.
 */

import { ClaimMetadata } from '../schema';

export const ERISA_CLAIMS: Record<string, ClaimMetadata> = {
  'erisa_502a1b_benefits': {
    name: 'ERISA § 502(a)(1)(B) - Denial of Benefits',
    category: 'erisa',
    source: '29 U.S.C. § 1132(a)(1)(B)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'erisa_internal',
    immunities: [],
    typicalDefenses: [
      'Failure to exhaust internal appeals',
      'Plan interpretation reasonable',
      'Abuse of discretion standard',
      'No plan coverage',
      'Pre-existing condition exclusion',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'Plan terms or state limitations (varies)',
  },

  'erisa_502a3_equitable_relief': {
    name: 'ERISA § 502(a)(3) - Equitable Relief',
    category: 'erisa',
    source: '29 U.S.C. § 1132(a)(3)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'erisa_internal',
    immunities: [],
    typicalDefenses: [
      'Adequate remedy under § 502(a)(1)(B)',
      'Relief not equitable in nature',
      'No fiduciary breach',
      'Plan followed',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'Plan terms or state limitations (varies)',
  },
};

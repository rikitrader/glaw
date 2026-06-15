/**
 * Federal Pleading Engine - Tax Claims
 *
 * Tax refund suits and wrongful levy claims.
 */

import { ClaimMetadata } from '../schema';

export const TAX_CLAIMS: Record<string, ClaimMetadata> = {
  'tax_refund_suit': {
    name: 'Tax Refund Suit',
    category: 'tax',
    source: '28 U.S.C. § 1346(a)(1)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'irs_claim',
    immunities: ['sovereign'],
    typicalDefenses: [
      'Failure to pay full assessment',
      'No timely administrative claim',
      'Tax properly assessed',
      'Variance doctrine (new issues)',
      'SOL expired',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years from denial or 6 months deemed denial',
    viabilityWarning: 'VERIFY: Must pay full tax before suit. Administrative claim required. Complex jurisdictional rules.',
  },

  'tax_wrongful_levy': {
    name: 'Tax Wrongful Levy',
    category: 'tax',
    source: '26 U.S.C. § 7426',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['sovereign'],
    typicalDefenses: [
      'Proper levy procedures followed',
      'Plaintiff not owner of property',
      'No interest in property at time of levy',
      'SOL expired (9 months)',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '9 months from levy',
    viabilityWarning: 'VERIFY: Very short SOL. Specific procedural requirements.',
  },
};

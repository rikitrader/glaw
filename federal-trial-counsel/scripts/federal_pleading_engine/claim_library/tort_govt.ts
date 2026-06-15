/**
 * Federal Pleading Engine - Federal Tort Claims Act (FTCA)
 *
 * FTCA negligence, medical malpractice, and wrongful death claims against the
 * United States.
 */

import { ClaimMetadata } from '../schema';

export const TORT_GOVT_CLAIMS: Record<string, ClaimMetadata> = {
  'ftca_negligence': {
    name: 'FTCA - Negligence',
    category: 'tort_government',
    source: '28 U.S.C. § 1346(b)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'ftca_sf95',
    immunities: ['sovereign', 'discretionary_function'],
    typicalDefenses: [
      'Failure to exhaust (no SF-95 filed)',
      'Discretionary function exception',
      'Intentional tort exception',
      'Federal employee acting outside scope',
      'State law does not recognize claim',
      'Failure to file within 2 years',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years from accrual; 6 months from denial',
  },

  'ftca_medical_malpractice': {
    name: 'FTCA - Medical Malpractice',
    category: 'tort_government',
    source: '28 U.S.C. § 1346(b)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'ftca_sf95',
    immunities: ['sovereign', 'discretionary_function'],
    typicalDefenses: [
      'Failure to exhaust (no SF-95)',
      'Failure to meet state malpractice requirements',
      'No duty owed',
      'Standard of care met',
      'No causation',
      'Statute of repose',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years from accrual; 6 months from denial',
  },

  'ftca_wrongful_death': {
    name: 'FTCA - Wrongful Death',
    category: 'tort_government',
    source: '28 U.S.C. § 1346(b)',
    sourceType: 'statute',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'ftca_sf95',
    immunities: ['sovereign', 'discretionary_function'],
    typicalDefenses: [
      'Failure to exhaust',
      'Discretionary function exception',
      'No state law wrongful death claim',
      'Plaintiff lacks standing',
      'Contributory/comparative negligence',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: '2 years from death; 6 months from denial',
  },
};

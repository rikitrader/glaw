/**
 * Federal Pleading Engine - Administrative Elements
 *
 * Element definitions and preconditions for APA, mandamus, and habeas
 * claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const ADMINISTRATIVE_ELEMENTS: Record<string, ClaimElement[]> = {
  'apa_arbitrary_capricious': [
    {
      number: 1,
      name: 'Final Agency Action',
      mustAllege: 'The challenged action is final agency action',
      typicalEvidence: ['Agency decision letter', 'Order', 'Regulation', 'Denial of petition'],
      pitfalls: 'Must mark consummation of decision-making process and determine rights/obligations.',
    },
    {
      number: 2,
      name: 'Agency Action',
      mustAllege: 'The agency took "action" as defined by the APA',
      typicalEvidence: ['Rule', 'Order', 'License', 'Sanction', 'Relief'],
      pitfalls: 'Inaction may require § 706(1) unreasonable delay claim instead.',
    },
    {
      number: 3,
      name: 'Within Zone of Interests',
      mustAllege: 'Plaintiff\'s interests are arguably within the zone of interests protected by the statute',
      typicalEvidence: ['Statutory purposes', 'Legislative history', 'Relationship to regulated activity'],
      pitfalls: 'Prudential standing requirement. Must be more than marginally related.',
    },
    {
      number: 4,
      name: 'Arbitrary and Capricious',
      mustAllege: 'Agency action was arbitrary, capricious, an abuse of discretion, or otherwise not in accordance with law',
      typicalEvidence: ['Administrative record gaps', 'Failure to consider relevant factors', 'Departure from prior policy without explanation'],
      pitfalls: 'Highly deferential standard. Must show agency failed to consider important aspect, offered implausible explanation, or acted contrary to evidence.',
    },
  ],

  'apa_unlawful_withholding_unreasonable_delay': [
    {
      number: 1,
      name: 'Discrete Agency Action Owed',
      mustAllege: 'Agency has a legal duty to take a discrete action that it has failed to take',
      typicalEvidence: ['Statutory mandate', 'Regulatory requirement', 'Pending application', 'Required response timeline'],
      pitfalls: 'Must be a discrete, non-discretionary duty. Cannot compel broad programmatic action (Norton v. SUWA).',
    },
    {
      number: 2,
      name: 'Unreasonable Delay',
      mustAllege: 'Agency delay in acting is unreasonable under TRAC factors: (1) rule of reason for time; (2) congressional timetable; (3) human health/welfare at stake; (4) effect of expediting on other agency actions; (5) impropriety of agency; (6) nature/extent of interests prejudiced',
      typicalEvidence: ['Timeline of agency inaction', 'Statutory deadlines missed', 'Comparison to typical processing times', 'Impact on plaintiff'],
      pitfalls: 'Courts very reluctant to impose timelines on agencies. Must show delay well beyond norms.',
    },
    {
      number: 3,
      name: 'No Adequate Alternative Remedy',
      mustAllege: 'Plaintiff has no other adequate remedy in a court',
      typicalEvidence: ['Absence of other statutory remedies', 'Administrative remedies exhausted or futile'],
      pitfalls: 'If other adequate remedies exist, APA claim may be precluded.',
    },
  ],

  'mandamus_compel_ministerial_duty': [
    {
      number: 1,
      name: 'Clear Right to Relief',
      mustAllege: 'Plaintiff has a clear and indisputable right to the relief sought',
      typicalEvidence: ['Statutory mandate', 'Regulatory obligation', 'Constitutional duty'],
      pitfalls: 'Must be "clear and indisputable" - not debatable or discretionary.',
    },
    {
      number: 2,
      name: 'Ministerial Duty',
      mustAllege: 'Defendant has a non-discretionary, ministerial duty to perform the act sought',
      typicalEvidence: ['Statute imposing duty', 'Mandatory language ("shall")', 'No discretion in performance'],
      pitfalls: 'If duty involves any discretion, mandamus is improper. Must be purely ministerial.',
    },
    {
      number: 3,
      name: 'No Adequate Alternative Remedy',
      mustAllege: 'Plaintiff has no other adequate means to obtain the relief',
      typicalEvidence: ['Exhaustion of alternatives', 'No statutory appeal path', 'APA remedies inadequate'],
      pitfalls: 'Mandamus is an extraordinary remedy. Must show other avenues are inadequate or unavailable.',
    },
  ],

  'habeas_detention_challenge': [
    {
      number: 1,
      name: 'In Custody',
      mustAllege: 'Petitioner is in custody (physical confinement, parole, supervised release, or sufficient restraint on liberty)',
      typicalEvidence: ['Commitment order', 'Detention records', 'Conditions of confinement'],
      pitfalls: 'Must be "in custody" at time of filing. Expired sentence generally moots petition unless collateral consequences.',
    },
    {
      number: 2,
      name: 'Proper Respondent',
      mustAllege: 'Petition names the immediate custodian (warden, officer in charge)',
      typicalEvidence: ['Facility records', 'BOP designation', 'Immigration detention facility identification'],
      pitfalls: 'Must name immediate custodian, not Attorney General or agency head (in most circuits).',
    },
    {
      number: 3,
      name: 'Jurisdictional Basis',
      mustAllege: 'Basis for federal habeas jurisdiction (constitutional violation, jurisdictional defect, or other legal error rendering detention unlawful)',
      typicalEvidence: ['Constitutional arguments', 'Statutory construction', 'Sentencing errors'],
      pitfalls: 'For § 2254 (state prisoners): AEDPA deference applies. For § 2241 (federal): fewer restrictions but must exhaust BOP remedies.',
    },
    {
      number: 4,
      name: 'Exhaustion',
      mustAllege: 'Petitioner has exhausted available administrative or state-court remedies',
      typicalEvidence: ['Administrative grievances', 'State court records', 'BOP remedy responses'],
      pitfalls: '§ 2254: must exhaust state courts. § 2241: must exhaust BOP remedies. Exceptions for futility are narrow.',
    },
  ],
};

export const ADMINISTRATIVE_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'apa_arbitrary_capricious': [
    {
      type: 'exhaustion',
      requirement: 'Final agency action',
      notes: 'Must be consummation of decision-making. Preliminary steps don\'t qualify.',
    },
  ],

  'habeas_detention_challenge': [
    {
      type: 'exhaustion',
      requirement: 'Exhaust available administrative or state-court remedies',
      notes: '§ 2254: state courts. § 2241: BOP administrative remedies. Futility exception narrow.',
    },
  ],
};

/**
 * Federal Pleading Engine - ERISA Elements
 *
 * Element definitions and preconditions for ERISA benefits and equitable
 * relief claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const ERISA_ELEMENTS: Record<string, ClaimElement[]> = {
  'erisa_502a1b_benefits': [
    {
      number: 1,
      name: 'ERISA Plan',
      mustAllege: 'A plan exists that is governed by ERISA',
      typicalEvidence: ['Plan documents', 'SPD', 'Form 5500'],
      pitfalls: 'Governmental and church plans may be exempt.',
    },
    {
      number: 2,
      name: 'Participant or Beneficiary',
      mustAllege: 'Plaintiff is a participant or beneficiary of the plan',
      typicalEvidence: ['Enrollment records', 'Plan eligibility provisions', 'Employment records'],
      pitfalls: 'Former employees may lose participant status for some purposes.',
    },
    {
      number: 3,
      name: 'Denial of Benefits',
      mustAllege: 'Benefits were denied or not paid as required by the plan',
      typicalEvidence: ['Denial letter', 'Claim records', 'Plan terms', 'Correspondence'],
      pitfalls: 'Must identify specific benefit and how plan entitles claimant.',
    },
    {
      number: 4,
      name: 'Proper Under Plan Terms',
      mustAllege: 'Benefits are due under the terms of the plan',
      typicalEvidence: ['Plan language', 'SPD provisions', 'Coverage analysis'],
      pitfalls: 'Plan interpretation may be reviewed for abuse of discretion if plan grants discretion.',
    },
  ],

  'erisa_502a3_equitable_relief': [
    {
      number: 1,
      name: 'ERISA Plan',
      mustAllege: 'A plan governed by ERISA exists',
      typicalEvidence: ['Plan documents', 'SPD', 'Form 5500', 'Employer benefits documentation'],
      pitfalls: 'Governmental and church plans exempt from ERISA.',
    },
    {
      number: 2,
      name: 'Fiduciary Breach or Violation',
      mustAllege: 'Defendant violated ERISA or the plan terms, or breached fiduciary duty',
      typicalEvidence: ['Plan terms violated', 'Fiduciary duty analysis', 'Self-dealing evidence', 'Prohibited transactions'],
      pitfalls: 'Must identify specific ERISA provision violated or specific fiduciary breach.',
    },
    {
      number: 3,
      name: 'Equitable Relief Sought',
      mustAllege: 'Relief sought is equitable in nature (injunction, restitution, surcharge, reformation)',
      typicalEvidence: ['Nature of relief requested', 'Trust law analogues', 'Equitable remedies analysis'],
      pitfalls: 'After Great-West v. Knudson and CIGNA v. Amara: only "appropriate equitable relief" available. Legal damages (money) generally not available under § 502(a)(3).',
    },
    {
      number: 4,
      name: 'No Adequate Remedy Under § 502(a)(1)(B)',
      mustAllege: 'Plaintiff has no adequate remedy under § 502(a)(1)(B) for denial of benefits (Varity Corp. v. Howe limitation)',
      typicalEvidence: ['Analysis of why (a)(1)(B) is inadequate', 'Nature of claim beyond benefits denial'],
      pitfalls: 'Cannot use § 502(a)(3) as a duplicate remedy when § 502(a)(1)(B) provides adequate relief.',
    },
  ],
};

export const ERISA_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'erisa_502a1b_benefits': [
    {
      type: 'exhaustion',
      requirement: 'Complete internal appeal process under the plan',
      notes: 'Usually one or two levels of internal appeal. Futility exception narrow.',
    },
  ],

  'erisa_502a3_equitable_relief': [
    {
      type: 'exhaustion',
      requirement: 'Complete internal appeal process under the plan (if applicable)',
      notes: 'Exhaustion may not be required for all § 502(a)(3) claims, particularly fiduciary breach claims.',
    },
  ],
};

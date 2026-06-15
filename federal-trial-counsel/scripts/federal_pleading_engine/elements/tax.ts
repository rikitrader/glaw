/**
 * Federal Pleading Engine - Tax Elements
 *
 * Element definitions and preconditions for tax refund and wrongful levy
 * claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const TAX_ELEMENTS: Record<string, ClaimElement[]> = {
  'tax_refund_suit': [
    {
      number: 1,
      name: 'Full Payment',
      mustAllege: 'Plaintiff paid the full amount of assessed tax before filing suit (Flora full-payment rule)',
      typicalEvidence: ['Tax payment records', 'IRS account transcripts', 'Bank statements showing payment'],
      pitfalls: 'Must pay full assessed amount (including penalties and interest) before district court has jurisdiction. Partial payment insufficient.',
    },
    {
      number: 2,
      name: 'Administrative Claim',
      mustAllege: 'Plaintiff filed a timely administrative claim for refund with the IRS (Form 1040X or Form 843)',
      typicalEvidence: ['Amended return', 'Refund claim form', 'IRS receipt/acknowledgment'],
      pitfalls: 'Must file within 3 years of return or 2 years of payment. Amount cannot exceed tax paid within lookback period.',
    },
    {
      number: 3,
      name: 'Denial or Deemed Denial',
      mustAllege: 'IRS denied the refund claim or 6 months elapsed without action (deemed denial)',
      typicalEvidence: ['Denial notice', 'Proof of 6-month passage without action'],
      pitfalls: 'Suit must be filed within 2 years of denial. No deadline if deemed denial (6-month wait only).',
    },
    {
      number: 4,
      name: 'Overpayment',
      mustAllege: 'Tax was erroneously or illegally assessed and collected, resulting in an overpayment',
      typicalEvidence: ['Tax law analysis', 'Correct tax calculation', 'Basis for refund'],
      pitfalls: 'Variance doctrine: cannot raise new grounds not presented in administrative claim.',
    },
  ],

  'tax_wrongful_levy': [
    {
      number: 1,
      name: 'Levy Occurred',
      mustAllege: 'IRS levied on property',
      typicalEvidence: ['Notice of levy', 'Seizure records', 'IRS Form 668-A/W'],
      pitfalls: 'Must distinguish between lien (security interest) and levy (actual seizure).',
    },
    {
      number: 2,
      name: 'Property Interest',
      mustAllege: 'Plaintiff had an ownership interest in or lien on the property levied upon, and the property was not the taxpayer\'s property or was exempt',
      typicalEvidence: ['Title records', 'Purchase documentation', 'UCC filings', 'Exemption documentation'],
      pitfalls: 'Only available to third parties (not the taxpayer). Must show superior property interest.',
    },
    {
      number: 3,
      name: 'Wrongfulness',
      mustAllege: 'The levy was wrongful because the property belonged to plaintiff, not the taxpayer, or was exempt from levy',
      typicalEvidence: ['Ownership evidence', 'Exemption status', 'Prior claims on property'],
      pitfalls: 'Mere procedural irregularity may not make levy wrongful if substantive authority existed.',
    },
    {
      number: 4,
      name: 'Timely Filing',
      mustAllege: 'Suit filed within 9 months of the levy',
      typicalEvidence: ['Date of levy', 'Date suit filed'],
      pitfalls: 'Very short 9-month statute of limitations. No equitable tolling generally available.',
    },
  ],
};

export const TAX_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'tax_refund_suit': [
    {
      type: 'exhaustion',
      requirement: 'Pay full assessed tax and file administrative refund claim (Form 1040X or 843)',
      notes: 'Flora full-payment rule: must pay entire assessment. Administrative claim within 3 years of return or 2 years of payment.',
    },
    {
      type: 'timing',
      requirement: 'Suit within 2 years of IRS denial or 6 months after filing (deemed denial)',
      notes: 'Variance doctrine prevents raising grounds not in administrative claim.',
    },
  ],
};

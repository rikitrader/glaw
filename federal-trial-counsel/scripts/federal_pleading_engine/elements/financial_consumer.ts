/**
 * Federal Pleading Engine - Financial / Consumer Elements
 *
 * Element definitions and preconditions for FCRA, FDCPA, and TILA claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const FINANCIAL_CONSUMER_ELEMENTS: Record<string, ClaimElement[]> = {
  'fcra_inaccurate_reporting': [
    {
      number: 1,
      name: 'Consumer Report',
      mustAllege: 'Defendant is a consumer reporting agency, furnisher of information, or user of consumer reports subject to FCRA',
      typicalEvidence: ['Credit reports', 'Business registration', 'Furnisher agreement with CRA'],
      pitfalls: 'Different duties apply to CRAs, furnishers, and users. Identify defendant\'s role.',
    },
    {
      number: 2,
      name: 'Inaccurate Information',
      mustAllege: 'Consumer report contained inaccurate or incomplete information',
      typicalEvidence: ['Credit report showing errors', 'Correct information', 'Comparison documentation'],
      pitfalls: 'Technically accurate but misleading information may also be actionable.',
    },
    {
      number: 3,
      name: 'Dispute/Notice',
      mustAllege: 'Plaintiff disputed the inaccuracy with the CRA and/or furnisher',
      typicalEvidence: ['Dispute letters', 'CRA response', 'Furnisher investigation results'],
      pitfalls: 'For furnisher liability under § 1681s-2(b), CRA must first notify furnisher of dispute.',
    },
    {
      number: 4,
      name: 'Failure to Investigate/Correct',
      mustAllege: 'Defendant failed to reasonably investigate and/or correct the inaccuracy after notice',
      typicalEvidence: ['Investigation records', 'Continued reporting of inaccuracy', 'Insufficient investigation'],
      pitfalls: 'CRA must conduct "reasonable" investigation. Furnisher must investigate after CRA notification.',
    },
    {
      number: 5,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered damages (actual damages for negligence; statutory damages for willful violations)',
      typicalEvidence: ['Credit denial letters', 'Higher interest rates', 'Emotional distress', 'Financial losses'],
      pitfalls: 'Willful violation: statutory damages $100-$1,000 per violation plus punitive. Negligent: actual damages only.',
    },
  ],

  'fdcpa_prohibited_practices': [
    {
      number: 1,
      name: 'Debt Collector',
      mustAllege: 'Defendant is a "debt collector" as defined by FDCPA (regularly collects debts owed to others)',
      typicalEvidence: ['Business registration', 'Collection letters', 'Third-party collection activity'],
      pitfalls: 'Original creditors generally not covered. Must be collecting debts owed to another.',
    },
    {
      number: 2,
      name: 'Consumer Debt',
      mustAllege: 'The debt is a "consumer debt" (incurred primarily for personal, family, or household purposes)',
      typicalEvidence: ['Nature of original transaction', 'Account records', 'Purpose of credit'],
      pitfalls: 'Business/commercial debts not covered. Must be primarily personal.',
    },
    {
      number: 3,
      name: 'Prohibited Practice',
      mustAllege: 'Defendant engaged in a practice prohibited by the FDCPA (harassment, false representations, unfair practices, or validation failures)',
      typicalEvidence: ['Collection letters', 'Phone recordings', 'Written communications', 'Third-party disclosures'],
      pitfalls: 'Specific prohibitions in §§ 1692c-1692f. Identify which specific provision violated.',
    },
    {
      number: 4,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered damages (actual damages and/or statutory damages up to $1,000)',
      typicalEvidence: ['Financial harm', 'Emotional distress', 'Out-of-pocket costs'],
      pitfalls: 'Statutory damages capped at $1,000 per action for individual claims. Attorney fees available.',
    },
  ],

  'tila_disclosure_violations': [
    {
      number: 1,
      name: 'Creditor Subject to TILA',
      mustAllege: 'Defendant is a creditor who regularly extends consumer credit subject to TILA',
      typicalEvidence: ['Lending records', 'Business registration', 'Credit agreement'],
      pitfalls: 'Seller credit and certain transactions may be exempt. Check Regulation Z.',
    },
    {
      number: 2,
      name: 'Consumer Credit Transaction',
      mustAllege: 'Transaction was a consumer credit transaction covered by TILA',
      typicalEvidence: ['Loan agreement', 'Credit card application', 'Mortgage documents'],
      pitfalls: 'Business purpose credit generally excluded. Must be primarily personal/family/household.',
    },
    {
      number: 3,
      name: 'Material Disclosure Violation',
      mustAllege: 'Creditor failed to make required disclosures or made inaccurate disclosures (APR, finance charge, amount financed, total of payments, payment schedule)',
      typicalEvidence: ['Loan documents', 'Truth-in-lending disclosure', 'Comparison to required disclosures'],
      pitfalls: 'Minor technical violations may not be actionable. Focus on material disclosures.',
    },
    {
      number: 4,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered actual damages and/or is entitled to statutory damages',
      typicalEvidence: ['Financial harm from reliance on incorrect disclosures', 'Comparison of terms'],
      pitfalls: 'Statutory damages: $200-$2,000 (individual), up to lesser of $1M or 1% of net worth (class). 1-year SOL for damages, 3 years for rescission.',
    },
  ],
};

export const FINANCIAL_CONSUMER_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {};

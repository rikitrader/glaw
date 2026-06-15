/**
 * Federal Pleading Engine - Government Tort (FTCA) Elements
 *
 * Element definitions and preconditions for Federal Tort Claims Act
 * claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const TORT_GOVT_ELEMENTS: Record<string, ClaimElement[]> = {
  'ftca_negligence': [
    {
      number: 1,
      name: 'Federal Employee',
      mustAllege: 'Negligent actor was a federal employee acting within scope of employment',
      typicalEvidence: ['Employment records', 'Job description', 'Scope of duties'],
      pitfalls: 'Contractors are generally not covered. Scope must be analyzed.',
    },
    {
      number: 2,
      name: 'State Law Tort',
      mustAllege: 'Conduct would constitute a tort under the law of the state where it occurred',
      typicalEvidence: ['State tort law analysis', 'Duty analysis', 'Standard of care'],
      pitfalls: 'FTCA adopts state substantive law. Research specific state requirements.',
    },
    {
      number: 3,
      name: 'Duty',
      mustAllege: 'Federal employee owed plaintiff a duty of care',
      typicalEvidence: ['Relationship', 'Foreseeability', 'State law duty analysis'],
      pitfalls: 'Many federal functions have no private analog (discretionary function).',
    },
    {
      number: 4,
      name: 'Breach',
      mustAllege: 'Federal employee breached the duty of care',
      typicalEvidence: ['Deviation from standard', 'Expert testimony', 'Policy violations'],
      pitfalls: 'Discretionary function exception may bar claim.',
    },
    {
      number: 5,
      name: 'Causation',
      mustAllege: 'Breach was proximate cause of plaintiff\'s injury',
      typicalEvidence: ['Medical causation', 'Expert testimony', 'Timeline'],
      pitfalls: 'Must establish both cause-in-fact and proximate cause.',
    },
    {
      number: 6,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered cognizable damages',
      typicalEvidence: ['Medical bills', 'Lost wages', 'Pain and suffering documentation'],
      pitfalls: 'Punitive damages not available under FTCA.',
    },
  ],

  'ftca_medical_malpractice': [
    {
      number: 1,
      name: 'Federal Employee',
      mustAllege: 'Negligent medical provider was a federal employee (or deemed employee) acting within scope of employment',
      typicalEvidence: ['Employment records', 'Federal facility records', 'Scope of duties documentation'],
      pitfalls: 'Contract physicians may be "deemed employees" under Gonzalez Act. Verify status.',
    },
    {
      number: 2,
      name: 'Standard of Care',
      mustAllege: 'Applicable standard of care under the law of the state where the malpractice occurred',
      typicalEvidence: ['Expert opinion on standard of care', 'Medical guidelines', 'Practice standards'],
      pitfalls: 'FTCA adopts state substantive law including state malpractice requirements (expert affidavit, etc.).',
    },
    {
      number: 3,
      name: 'Breach of Standard',
      mustAllege: 'Federal medical provider breached the applicable standard of care',
      typicalEvidence: ['Expert testimony', 'Medical records showing deviation', 'Comparison to accepted practices'],
      pitfalls: 'Usually requires expert testimony. Some states have additional pre-suit requirements.',
    },
    {
      number: 4,
      name: 'Causation',
      mustAllege: 'Breach of standard of care was the proximate cause of plaintiff\'s injury',
      typicalEvidence: ['Medical expert causation opinion', 'Timeline of treatment and injury', 'Differential diagnosis'],
      pitfalls: 'Must establish both cause-in-fact and proximate cause through expert testimony.',
    },
    {
      number: 5,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered compensable damages',
      typicalEvidence: ['Medical bills', 'Future care costs', 'Lost wages', 'Pain and suffering documentation'],
      pitfalls: 'No punitive damages under FTCA. No jury trial (bench trial only).',
    },
    {
      number: 6,
      name: 'Administrative Exhaustion (SF-95)',
      mustAllege: 'Plaintiff filed SF-95 administrative tort claim with appropriate agency before filing suit',
      typicalEvidence: ['SF-95 form', 'Agency receipt/response', 'Six-month deemed denial or formal denial letter'],
      pitfalls: 'Must include sum certain in SF-95. Cannot exceed amount claimed administratively.',
    },
  ],

  'ftca_wrongful_death': [
    {
      number: 1,
      name: 'Federal Employee Negligence',
      mustAllege: 'Death was caused by negligence of a federal employee acting within scope of employment',
      typicalEvidence: ['Death certificate', 'Autopsy report', 'Federal employment records', 'Incident report'],
      pitfalls: 'State law determines whether wrongful death claim exists and who can bring it.',
    },
    {
      number: 2,
      name: 'State Law Wrongful Death Claim',
      mustAllege: 'Claim satisfies wrongful death requirements under the law of the state where death occurred',
      typicalEvidence: ['State wrongful death statute', 'Elements analysis', 'Proper party plaintiff'],
      pitfalls: 'FTCA applies state law. Must meet all state-specific wrongful death requirements.',
    },
    {
      number: 3,
      name: 'Standing',
      mustAllege: 'Plaintiff is a proper party under applicable state wrongful death statute (spouse, children, estate)',
      typicalEvidence: ['Marriage certificate', 'Birth certificates', 'Estate appointment', 'Dependency evidence'],
      pitfalls: 'State law determines who has standing. Some states limit to statutory beneficiaries.',
    },
    {
      number: 4,
      name: 'Causation',
      mustAllege: 'Federal employee\'s negligence was the proximate cause of death',
      typicalEvidence: ['Expert causation opinion', 'Medical records', 'Autopsy findings'],
      pitfalls: 'Must establish both actual and proximate causation.',
    },
    {
      number: 5,
      name: 'Administrative Exhaustion (SF-95)',
      mustAllege: 'SF-95 administrative tort claim filed with appropriate agency',
      typicalEvidence: ['SF-95 form', 'Agency response', 'Denial letter or six-month deemed denial'],
      pitfalls: 'Must include sum certain. 2-year filing deadline from date of death.',
    },
  ],
};

export const TORT_GOVT_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'ftca_negligence': [
    {
      type: 'exhaustion',
      requirement: 'SF-95 administrative claim filed with appropriate agency',
      notes: 'Must include sum certain. Claim must be finally denied or 6 months pass.',
    },
    {
      type: 'timing',
      requirement: 'Administrative claim within 2 years of accrual; suit within 6 months of denial',
      notes: 'If no final denial, must wait 6 months but can sue any time after.',
    },
  ],

  'ftca_medical_malpractice': [
    {
      type: 'exhaustion',
      requirement: 'SF-95 administrative tort claim filed with appropriate agency',
      notes: 'Must include sum certain. Cannot recover more in suit than claimed on SF-95.',
    },
    {
      type: 'timing',
      requirement: 'Administrative claim within 2 years of accrual; suit within 6 months of denial',
      notes: 'State malpractice pre-suit requirements (expert affidavit, etc.) may also apply.',
    },
  ],

  'ftca_wrongful_death': [
    {
      type: 'exhaustion',
      requirement: 'SF-95 administrative tort claim filed with appropriate agency',
      notes: 'Must include sum certain. Filed by proper party under state law.',
    },
    {
      type: 'timing',
      requirement: 'Administrative claim within 2 years of death; suit within 6 months of denial',
      notes: 'SOL runs from date of death, not discovery of negligence.',
    },
  ],
};

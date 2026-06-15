/**
 * Federal Pleading Engine - Bivens Elements
 *
 * Element definitions and preconditions for Bivens constitutional tort
 * claims against federal actors.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const BIVENS_ELEMENTS: Record<string, ClaimElement[]> = {
  'bivens_fourth_search_seizure': [
    {
      number: 1,
      name: 'Federal Actor',
      mustAllege: 'Defendant was a federal agent acting under color of federal authority',
      typicalEvidence: ['Federal employment records', 'Badge/credentials', 'Federal agency assignment'],
      pitfalls: 'Must be federal actor (not state). State actors use § 1983 instead.',
    },
    {
      number: 2,
      name: 'Unreasonable Search/Seizure',
      mustAllege: 'Federal agent conducted an unreasonable search or seizure in violation of the Fourth Amendment',
      typicalEvidence: ['Search warrant deficiencies', 'Arrest records', 'Video evidence', 'Witness statements'],
      pitfalls: 'Same substantive standard as § 1983 but against federal actors.',
    },
    {
      number: 3,
      name: 'Not a New Context',
      mustAllege: 'This Bivens claim does not present a "new context" or, if it does, no special factors counsel hesitation',
      typicalEvidence: ['Similarity to Bivens itself (1971)', 'No alternative remedies', 'No national security implications'],
      pitfalls: 'CRITICAL: After Ziglar v. Abbasi (2017) and Egbert v. Boule (2022), courts rarely extend Bivens to new contexts. Must argue this is a recognized context.',
    },
    {
      number: 4,
      name: 'Injury/Damages',
      mustAllege: 'Plaintiff suffered injury as a result of the unreasonable search or seizure',
      typicalEvidence: ['Medical records', 'Property damage', 'Emotional distress', 'Financial losses'],
      pitfalls: 'No punitive damages in Bivens actions against federal agents.',
    },
  ],

  'bivens_fifth_due_process': [
    {
      number: 1,
      name: 'Federal Actor',
      mustAllege: 'Defendant was a federal employee or official acting under federal authority',
      typicalEvidence: ['Federal employment records', 'Official capacity', 'Federal agency association'],
      pitfalls: 'Only applies to federal actors. State actors use § 1983.',
    },
    {
      number: 2,
      name: 'Due Process Violation',
      mustAllege: 'Federal actor deprived plaintiff of life, liberty, or property without due process of law in violation of the Fifth Amendment',
      typicalEvidence: ['Termination records', 'Discriminatory actions', 'Deprivation evidence'],
      pitfalls: 'Fifth Amendment (not Fourteenth) applies to federal actors.',
    },
    {
      number: 3,
      name: 'Not a New Context',
      mustAllege: 'Claim falls within recognized Bivens context (employment discrimination as in Davis v. Passman) or no special factors counsel hesitation',
      typicalEvidence: ['Similarity to Davis v. Passman facts', 'Absence of alternative remedies'],
      pitfalls: 'Very narrow. CSRA may provide exclusive remedy for federal employees. Most new contexts rejected.',
    },
    {
      number: 4,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered cognizable damages',
      typicalEvidence: ['Lost wages', 'Emotional distress', 'Career harm documentation'],
      pitfalls: 'Equitable relief generally not available in Bivens. Damages only.',
    },
  ],

  'bivens_eighth_deliberate_indifference': [
    {
      number: 1,
      name: 'Federal Prisoner Status',
      mustAllege: 'Plaintiff was a federal prisoner in the custody of defendant',
      typicalEvidence: ['BOP commitment records', 'Facility records', 'Custody documentation'],
      pitfalls: 'Only applies to federal prisoners. State prisoners use § 1983.',
    },
    {
      number: 2,
      name: 'Serious Medical Need',
      mustAllege: 'Plaintiff had a serious medical need (condition diagnosed by physician requiring treatment, or so obvious that a lay person would recognize the need)',
      typicalEvidence: ['Medical records', 'Diagnosis', 'Physician statements', 'Visible symptoms'],
      pitfalls: 'Must be objectively serious. Disagreement with treatment plan generally insufficient.',
    },
    {
      number: 3,
      name: 'Deliberate Indifference',
      mustAllege: 'Defendant knew of and disregarded an excessive risk to plaintiff\'s health or safety',
      typicalEvidence: ['Sick call requests', 'Grievances filed', 'Staff awareness of condition', 'Delay in treatment'],
      pitfalls: 'Must show subjective awareness of risk, not just objective unreasonableness. Negligent medical care not actionable.',
    },
    {
      number: 4,
      name: 'Not a New Context',
      mustAllege: 'Claim falls within recognized Bivens context (federal prisoner medical care as in Carlson v. Green)',
      typicalEvidence: ['Similarity to Carlson v. Green facts', 'BOP context'],
      pitfalls: 'This is one of the three recognized Bivens contexts, but even here courts may find new-context factors.',
    },
    {
      number: 5,
      name: 'Exhaustion (PLRA)',
      mustAllege: 'Plaintiff exhausted all available administrative remedies through BOP grievance system',
      typicalEvidence: ['BOP grievance forms (BP-8, BP-9, BP-10, BP-11)', 'Administrative remedy responses'],
      pitfalls: 'PLRA exhaustion is mandatory and jurisdictional. Must complete all levels.',
    },
  ],
};

export const BIVENS_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'bivens_eighth_deliberate_indifference': [
    {
      type: 'exhaustion',
      requirement: 'Complete BOP administrative remedy process (BP-8, BP-9, BP-10, BP-11)',
      notes: 'PLRA exhaustion is mandatory. Must complete all levels before filing suit.',
    },
  ],
};

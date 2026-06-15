/**
 * Federal Pleading Engine - Bivens Claims (Federal Actors)
 *
 * Constitutional tort claims against federal officials under Bivens and its progeny.
 * Modern doctrine severely limits extension to new contexts.
 */

import { ClaimMetadata } from '../schema';

export const BIVENS_CLAIMS: Record<string, ClaimMetadata> = {
  'bivens_fourth_search_seizure': {
    name: 'Bivens Fourth Amendment (Search/Seizure)',
    category: 'bivens',
    source: 'Bivens v. Six Unknown Named Agents, 403 U.S. 388 (1971)',
    sourceType: 'constitutional',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['qualified', 'sovereign'],
    typicalDefenses: [
      'Qualified immunity',
      'New context (Ziglar v. Abbasi factors)',
      'Special factors counseling hesitation',
      'Alternative remedies available',
      'National security implications',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'State personal injury SOL (typically 2-4 years)',
    viabilityWarning: 'VERIFY: Modern Bivens doctrine severely limited. Courts rarely extend to new contexts. See Ziglar v. Abbasi, 582 U.S. 120 (2017); Egbert v. Boule, 596 U.S. 482 (2022).',
  },

  'bivens_fifth_due_process': {
    name: 'Bivens Fifth Amendment (Due Process)',
    category: 'bivens',
    source: 'Davis v. Passman, 442 U.S. 228 (1979)',
    sourceType: 'constitutional',
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ['qualified', 'sovereign'],
    typicalDefenses: [
      'Qualified immunity',
      'New context',
      'Special factors',
      'Alternative remedies',
      'CSRA preclusion (federal employees)',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'State personal injury SOL (typically 2-4 years)',
    viabilityWarning: 'VERIFY: Rarely extended beyond employment discrimination context. CSRA may provide exclusive remedy for federal employees.',
  },

  'bivens_eighth_deliberate_indifference': {
    name: 'Bivens Eighth Amendment (Deliberate Indifference)',
    category: 'bivens',
    source: 'Carlson v. Green, 446 U.S. 14 (1980)',
    sourceType: 'constitutional',
    heightenedPleading: false,
    exhaustionRequired: true,
    exhaustionType: 'plra',
    immunities: ['qualified', 'sovereign'],
    typicalDefenses: [
      'Qualified immunity',
      'PLRA exhaustion not complete',
      'No subjective knowledge of risk',
      'Reasonable response to risk',
      'BOP administrative remedies not exhausted',
    ],
    jurisdiction: 'federal_question',
    statuteOfLimitations: 'State personal injury SOL (typically 2-4 years)',
    viabilityWarning: 'VERIFY: Limited to federal prisoner medical care context. PLRA exhaustion required. New contexts rarely recognized.',
  },
};

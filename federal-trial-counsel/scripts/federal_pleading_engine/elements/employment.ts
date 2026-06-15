/**
 * Federal Pleading Engine - Employment Elements
 *
 * Element definitions and preconditions for Title VII, ADEA, ADA, FMLA,
 * and FLSA claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const EMPLOYMENT_ELEMENTS: Record<string, ClaimElement[]> = {
  'title_vii_disparate_treatment': [
    {
      number: 1,
      name: 'Protected Class',
      mustAllege: 'Plaintiff is a member of a protected class (race, color, religion, sex, national origin)',
      typicalEvidence: ['Self-identification', 'Personnel records', 'Witness testimony'],
      pitfalls: 'Must identify specific protected characteristic.',
    },
    {
      number: 2,
      name: 'Qualification',
      mustAllege: 'Plaintiff was qualified for the position or performing job adequately',
      typicalEvidence: ['Performance reviews', 'Qualifications vs. job requirements', 'Commendations'],
      pitfalls: 'Defendant will attack qualifications. Document all accomplishments.',
    },
    {
      number: 3,
      name: 'Adverse Employment Action',
      mustAllege: 'Plaintiff suffered an adverse employment action (termination, demotion, failure to hire, etc.)',
      typicalEvidence: ['Termination letter', 'Demotion records', 'Rejection letter', 'Wage records'],
      pitfalls: 'Lateral transfers or minor changes may not qualify. Must be materially adverse.',
    },
    {
      number: 4,
      name: 'Circumstances Suggesting Discrimination',
      mustAllege: 'Circumstances give rise to an inference of discrimination',
      typicalEvidence: ['Comparative treatment', 'Discriminatory comments', 'Timing', 'Statistical evidence'],
      pitfalls: 'Stray remarks by non-decisionmakers have limited weight.',
    },
    {
      number: 5,
      name: 'Causation',
      mustAllege: 'Protected characteristic was a motivating factor in the adverse action',
      typicalEvidence: ['Decisionmaker statements', 'Pattern evidence', 'Departure from procedure'],
      pitfalls: 'Same-actor inference may undercut claim if same person hired and fired.',
    },
  ],

  'title_vii_hostile_work_environment': [
    {
      number: 1,
      name: 'Protected Class',
      mustAllege: 'Plaintiff is a member of a protected class',
      typicalEvidence: ['Self-identification', 'Personnel records'],
      pitfalls: 'Harassment must be "because of" protected status.',
    },
    {
      number: 2,
      name: 'Unwelcome Conduct',
      mustAllege: 'Plaintiff was subjected to unwelcome conduct',
      typicalEvidence: ['Complaints made', 'Witness testimony', 'Documented objections'],
      pitfalls: 'Participation in conduct may undercut "unwelcome" showing.',
    },
    {
      number: 3,
      name: 'Based on Protected Class',
      mustAllege: 'Conduct was based on plaintiff\'s protected characteristic',
      typicalEvidence: ['Nature of comments', 'Target selection', 'Comparative treatment'],
      pitfalls: 'General rudeness or harassment not based on protected status insufficient.',
    },
    {
      number: 4,
      name: 'Severe or Pervasive',
      mustAllege: 'Conduct was sufficiently severe or pervasive to alter conditions of employment and create abusive environment',
      typicalEvidence: ['Frequency of incidents', 'Severity documentation', 'Physical threats', 'Interference with work'],
      pitfalls: 'Single incident rarely sufficient unless extremely severe. Consider totality.',
    },
    {
      number: 5,
      name: 'Employer Liability',
      mustAllege: 'Basis for employer liability (supervisor with tangible action, or negligence for co-worker harassment)',
      typicalEvidence: ['Supervisor status', 'Complaints to HR', 'Employer response', 'Policy failures'],
      pitfalls: 'Faragher/Ellerth defense available if no tangible employment action by supervisor.',
    },
  ],

  'flsa_unpaid_wages_overtime': [
    {
      number: 1,
      name: 'Employment Relationship',
      mustAllege: 'Plaintiff was an employee of defendant (not independent contractor)',
      typicalEvidence: ['W-2 forms', 'Employment agreement', 'Control factors analysis'],
      pitfalls: 'FLSA uses "economic reality" test. Misclassification is common.',
    },
    {
      number: 2,
      name: 'Coverage',
      mustAllege: 'Defendant is covered by FLSA (enterprise coverage or individual coverage)',
      typicalEvidence: ['Annual sales > $500K', 'Interstate commerce activity'],
      pitfalls: 'Small employers may not be covered. Check both enterprise and individual coverage.',
    },
    {
      number: 3,
      name: 'Hours Worked',
      mustAllege: 'Plaintiff worked hours in excess of 40 per week (overtime) or was not paid minimum wage',
      typicalEvidence: ['Time records', 'Schedules', 'Testimony', 'Electronic records'],
      pitfalls: 'Records often controlled by employer. Employee estimates may suffice initially.',
    },
    {
      number: 4,
      name: 'Non-Exempt Status',
      mustAllege: 'Plaintiff was not exempt from overtime requirements',
      typicalEvidence: ['Job duties', 'Salary level', 'Discretion exercised', 'Management duties'],
      pitfalls: 'Executive, administrative, professional exemptions common. Analyze actual duties.',
    },
    {
      number: 5,
      name: 'Failure to Pay',
      mustAllege: 'Defendant failed to pay required wages or overtime premium',
      typicalEvidence: ['Pay stubs', 'Bank records', 'Comparison of hours to pay'],
      pitfalls: 'Must show actual hours worked vs. pay received.',
    },
  ],

  'title_vii_retaliation': [
    {
      number: 1,
      name: 'Protected Activity',
      mustAllege: 'Plaintiff engaged in activity protected by Title VII (opposing unlawful practice or participating in EEOC proceeding)',
      typicalEvidence: ['EEOC charge', 'Internal complaint', 'Testimony in proceeding', 'Opposition to discriminatory practice'],
      pitfalls: 'Opposition must be to conduct that plaintiff reasonably believed violated Title VII.',
    },
    {
      number: 2,
      name: 'Materially Adverse Action',
      mustAllege: 'Employer took action that would dissuade a reasonable worker from making or supporting a charge of discrimination (Burlington Northern standard)',
      typicalEvidence: ['Termination', 'Demotion', 'Reassignment', 'Exclusion from meetings', 'Negative references'],
      pitfalls: 'Broader than adverse employment action for discrimination claims. Must be "materially adverse" not just trivial.',
    },
    {
      number: 3,
      name: 'Causal Connection',
      mustAllege: 'Protected activity was a but-for cause of the materially adverse action',
      typicalEvidence: ['Temporal proximity', 'Retaliatory statements', 'Departure from procedure', 'Comparative treatment'],
      pitfalls: 'After Nassar (2013): must show but-for causation, not just motivating factor. Temporal proximity alone may not suffice.',
    },
    {
      number: 4,
      name: 'EEOC Exhaustion',
      mustAllege: 'Plaintiff filed EEOC charge encompassing retaliation claim and received right-to-sue letter',
      typicalEvidence: ['EEOC charge', 'Right-to-sue letter', 'Filing date documentation'],
      pitfalls: 'Retaliation occurring after EEOC charge may be "reasonably related" to original charge.',
    },
  ],

  'adea_age_discrimination': [
    {
      number: 1,
      name: 'Age 40 or Older',
      mustAllege: 'Plaintiff was 40 years of age or older at the time of the adverse action',
      typicalEvidence: ['Birth certificate', 'Personnel records', 'Driver\'s license'],
      pitfalls: 'ADEA only protects those 40 and older. No reverse age discrimination claims.',
    },
    {
      number: 2,
      name: 'Qualification',
      mustAllege: 'Plaintiff was qualified for the position',
      typicalEvidence: ['Performance reviews', 'Job qualifications vs. requirements', 'Skills documentation'],
      pitfalls: 'Same standard as Title VII prima facie case.',
    },
    {
      number: 3,
      name: 'Adverse Employment Action',
      mustAllege: 'Plaintiff suffered an adverse employment action',
      typicalEvidence: ['Termination notice', 'Demotion records', 'Failure to hire documentation'],
      pitfalls: 'Must be materially adverse. Minor slights insufficient.',
    },
    {
      number: 4,
      name: 'Age Was But-For Cause',
      mustAllege: 'Age was the but-for cause of the adverse action (not just a motivating factor)',
      typicalEvidence: ['Age-related comments', 'Replacement by younger person', 'Pattern of age-based decisions', 'Statistical evidence'],
      pitfalls: 'After Gross v. FBL (2009): must prove but-for causation. No mixed-motive framework under ADEA.',
    },
    {
      number: 5,
      name: 'EEOC Exhaustion',
      mustAllege: 'Plaintiff filed timely EEOC charge and either received right-to-sue or waited 60 days',
      typicalEvidence: ['EEOC charge', 'Right-to-sue letter or 60-day waiting period documentation'],
      pitfalls: 'Can file suit 60 days after EEOC charge (no need to wait for right-to-sue letter).',
    },
  ],

  'ada_title_i_employment_disability': [
    {
      number: 1,
      name: 'Disability',
      mustAllege: 'Plaintiff has a disability as defined by the ADA: (a) physical/mental impairment substantially limiting major life activity; (b) record of such impairment; or (c) regarded as having impairment',
      typicalEvidence: ['Medical records', 'Diagnosis', 'Functional limitations documentation', 'Treatment records'],
      pitfalls: 'ADA Amendments Act (2008) broadened definition significantly. "Substantially limits" construed broadly.',
    },
    {
      number: 2,
      name: 'Qualified Individual',
      mustAllege: 'Plaintiff can perform the essential functions of the job, with or without reasonable accommodation',
      typicalEvidence: ['Job description', 'Performance evaluations', 'Essential functions analysis', 'Accommodation request'],
      pitfalls: 'Must distinguish essential from marginal functions. Employer\'s judgment gets some deference.',
    },
    {
      number: 3,
      name: 'Adverse Employment Action',
      mustAllege: 'Employer took adverse employment action against plaintiff because of disability',
      typicalEvidence: ['Termination', 'Failure to hire', 'Failure to accommodate', 'Demotion records'],
      pitfalls: 'Includes failure to provide reasonable accommodation as separate theory.',
    },
    {
      number: 4,
      name: 'Discriminatory Basis',
      mustAllege: 'Disability was the reason for the adverse action (or employer failed to provide reasonable accommodation)',
      typicalEvidence: ['Comments about disability', 'Timing of adverse action', 'Interactive process failures', 'Comparative treatment'],
      pitfalls: 'Failure to engage in interactive process is strong evidence but not automatic violation.',
    },
    {
      number: 5,
      name: 'EEOC Exhaustion',
      mustAllege: 'Plaintiff filed EEOC charge and received right-to-sue letter',
      typicalEvidence: ['EEOC charge', 'Right-to-sue letter'],
      pitfalls: 'Same procedural requirements as Title VII.',
    },
  ],

  'fmla_interference': [
    {
      number: 1,
      name: 'FMLA Eligibility',
      mustAllege: 'Plaintiff was an eligible employee (worked for employer with 50+ employees within 75 miles, employed 12+ months, worked 1,250+ hours)',
      typicalEvidence: ['Employment records', 'Hours worked', 'Employer size documentation', 'Hire date'],
      pitfalls: 'Both employer size and employee hours requirements must be met.',
    },
    {
      number: 2,
      name: 'Qualifying Reason',
      mustAllege: 'Plaintiff was entitled to FMLA leave for a qualifying reason (serious health condition of self or family member, birth/adoption, military caregiver/exigency)',
      typicalEvidence: ['Medical certification', 'Birth/adoption records', 'Military orders'],
      pitfalls: '"Serious health condition" requires inpatient care or continuing treatment. Common cold generally excluded.',
    },
    {
      number: 3,
      name: 'Notice to Employer',
      mustAllege: 'Plaintiff provided adequate notice of need for leave (30 days if foreseeable; as soon as practicable if not)',
      typicalEvidence: ['Leave request', 'Email/written notice', 'Verbal notice documentation', 'Medical forms submitted'],
      pitfalls: 'Need not specifically invoke FMLA, but must provide sufficient information for employer to know leave may be FMLA-qualifying.',
    },
    {
      number: 4,
      name: 'Employer Interference',
      mustAllege: 'Employer denied, interfered with, or restrained plaintiff\'s exercise of FMLA rights',
      typicalEvidence: ['Denied leave request', 'Discouragement of leave', 'Failure to reinstate', 'Counting FMLA leave as absence'],
      pitfalls: 'Interference is not intent-based. No need to prove employer acted with discriminatory motive.',
    },
    {
      number: 5,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered damages as a result of the interference (lost wages, lost benefits, other monetary losses)',
      typicalEvidence: ['Lost wages calculation', 'Benefits documentation', 'Out-of-pocket costs'],
      pitfalls: 'Liquidated damages available for willful violations. Must show actual prejudice from interference.',
    },
  ],

  'fmla_retaliation': [
    {
      number: 1,
      name: 'FMLA-Protected Activity',
      mustAllege: 'Plaintiff exercised rights under the FMLA (took or requested leave)',
      typicalEvidence: ['Leave request', 'FMLA certification', 'Leave records'],
      pitfalls: 'Requesting leave is protected even if leave is ultimately denied.',
    },
    {
      number: 2,
      name: 'Adverse Employment Action',
      mustAllege: 'Employer took adverse employment action against plaintiff',
      typicalEvidence: ['Termination', 'Demotion', 'Negative evaluation', 'Disciplinary action'],
      pitfalls: 'Must be materially adverse. De minimis changes insufficient.',
    },
    {
      number: 3,
      name: 'Causal Connection',
      mustAllege: 'Causal connection between FMLA-protected activity and adverse action',
      typicalEvidence: ['Temporal proximity', 'Retaliatory statements', 'Departure from procedure', 'Pattern evidence'],
      pitfalls: 'Unlike interference, retaliation requires proving employer\'s retaliatory intent.',
    },
  ],
};

export const EMPLOYMENT_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'title_vii_disparate_treatment': [
    {
      type: 'exhaustion',
      requirement: 'EEOC charge filed within 180/300 days of adverse action',
      notes: '300 days if state has FEP agency. Must wait 180 days or receive right-to-sue letter.',
    },
    {
      type: 'timing',
      requirement: 'Suit filed within 90 days of right-to-sue letter',
      notes: 'Strict deadline. No equitable tolling in most circuits.',
    },
  ],

  'title_vii_retaliation': [
    {
      type: 'exhaustion',
      requirement: 'EEOC charge filed within 180/300 days of retaliatory action',
      notes: 'Retaliation occurring after initial EEOC charge may be "reasonably related" and not require separate charge.',
    },
    {
      type: 'timing',
      requirement: 'Suit filed within 90 days of right-to-sue letter',
      notes: 'Same timing as other Title VII claims.',
    },
  ],

  'title_vii_hostile_work_environment': [
    {
      type: 'exhaustion',
      requirement: 'EEOC charge filed within 180/300 days',
      notes: 'Continuing violation doctrine may extend time for ongoing hostile environment.',
    },
    {
      type: 'timing',
      requirement: 'Suit filed within 90 days of right-to-sue letter',
      notes: 'Same timing as other Title VII claims.',
    },
  ],

  'adea_age_discrimination': [
    {
      type: 'exhaustion',
      requirement: 'EEOC charge filed within 180/300 days of adverse action',
      notes: 'Can file suit 60 days after filing charge (no need to wait for right-to-sue letter).',
    },
  ],

  'ada_title_i_employment_disability': [
    {
      type: 'exhaustion',
      requirement: 'EEOC charge filed within 180/300 days of adverse action',
      notes: 'Same procedural requirements as Title VII.',
    },
    {
      type: 'timing',
      requirement: 'Suit filed within 90 days of right-to-sue letter',
      notes: 'Strict deadline. No equitable tolling in most circuits.',
    },
  ],
};

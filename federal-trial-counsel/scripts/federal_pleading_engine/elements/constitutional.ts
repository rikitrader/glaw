/**
 * Federal Pleading Engine - Constitutional / Civil Rights Elements
 *
 * Element definitions and preconditions for 42 U.S.C. § 1983, § 1985,
 * and § 1986 claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const CONSTITUTIONAL_ELEMENTS: Record<string, ClaimElement[]> = {
  '1983_first_amendment_retaliation': [
    {
      number: 1,
      name: 'Protected Activity',
      mustAllege: 'Plaintiff engaged in constitutionally protected speech or conduct (petition, assembly, religion)',
      typicalEvidence: ['Speech transcript', 'Emails', 'Meeting records', 'Witness testimony'],
      pitfalls: 'Speech pursuant to official duties is NOT protected (Garcetti). Must be on matter of public concern.',
    },
    {
      number: 2,
      name: 'Adverse Action',
      mustAllege: 'Defendant took an action that would chill a person of ordinary firmness from continuing to engage in protected activity',
      typicalEvidence: ['Termination letter', 'Disciplinary records', 'Demotion notice', 'Transfer orders'],
      pitfalls: 'De minimis actions may not qualify. Must deter reasonable person.',
    },
    {
      number: 3,
      name: 'Causation',
      mustAllege: 'The protected activity was a substantial or motivating factor in the adverse action',
      typicalEvidence: ['Timeline/temporal proximity', 'Defendant statements', 'Comparative treatment', 'Pattern evidence'],
      pitfalls: 'Temporal proximity alone usually insufficient. Need additional evidence of retaliatory motive.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Employment records', 'Badge/uniform', 'Policy invocation', 'Official capacity evidence'],
      pitfalls: 'Private actors require state involvement. Off-duty conduct may not qualify.',
    },
  ],

  '1983_fourth_excessive_force': [
    {
      number: 1,
      name: 'Seizure Occurred',
      mustAllege: 'Defendant seized plaintiff through intentional application of physical force or show of authority that terminated movement',
      typicalEvidence: ['Arrest records', 'Body camera', 'Witness statements', 'Medical records'],
      pitfalls: 'Accidental force may not constitute seizure. Must be intentional.',
    },
    {
      number: 2,
      name: 'Force Applied',
      mustAllege: 'Defendant applied physical force to plaintiff\'s person',
      typicalEvidence: ['Medical records', 'Photos of injuries', 'Video evidence', 'Use of force reports'],
      pitfalls: 'Minimal force may not suffice. Document all force used.',
    },
    {
      number: 3,
      name: 'Objective Unreasonableness',
      mustAllege: 'The force used was objectively unreasonable under the circumstances, considering: (a) severity of crime; (b) immediate threat to safety; (c) active resistance/flight (Graham v. Connor factors)',
      typicalEvidence: ['Video showing events', 'Witness testimony on threat level', 'Use of force policy', 'Training records'],
      pitfalls: 'Must analyze from perspective of reasonable officer on scene, not hindsight. Tense situations favor officers.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['On-duty status', 'Uniform/badge', 'Invocation of authority'],
      pitfalls: 'Off-duty officers may still act under color of law if invoking authority.',
    },
    {
      number: 5,
      name: 'Injury/Damages',
      mustAllege: 'Plaintiff suffered injury as a result of the force',
      typicalEvidence: ['Medical records', 'Photos', 'Bills', 'Expert testimony'],
      pitfalls: 'Some circuits require more than de minimis injury for damages.',
    },
  ],

  '1983_fourth_false_arrest': [
    {
      number: 1,
      name: 'Arrest/Detention',
      mustAllege: 'Defendant caused plaintiff to be detained against plaintiff\'s will',
      typicalEvidence: ['Arrest records', 'Booking records', 'Witness statements'],
      pitfalls: 'Brief investigative stops (Terry) have different standard.',
    },
    {
      number: 2,
      name: 'Lack of Probable Cause',
      mustAllege: 'Defendant lacked probable cause to believe plaintiff committed a crime',
      typicalEvidence: ['Arrest report deficiencies', 'Witness testimony', 'Video evidence', 'Lack of investigation'],
      pitfalls: 'Only need arguable probable cause for qualified immunity. Low bar.',
    },
    {
      number: 3,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Official capacity', 'Badge/uniform', 'Authority invocation'],
      pitfalls: 'Private security generally not state actors.',
    },
    {
      number: 4,
      name: 'Causation',
      mustAllege: 'Defendant\'s actions were proximate cause of plaintiff\'s detention',
      typicalEvidence: ['Chain of events', 'Defendant decisions', 'Timing'],
      pitfalls: 'Intervening actors (prosecutors, judges) may break chain.',
    },
  ],

  '1983_monell_municipal_liability': [
    {
      number: 1,
      name: 'Constitutional Violation',
      mustAllege: 'A municipal employee violated plaintiff\'s constitutional rights',
      typicalEvidence: ['Same evidence as underlying § 1983 claim'],
      pitfalls: 'Must first establish an underlying violation. No vicarious liability.',
    },
    {
      number: 2,
      name: 'Official Policy or Custom',
      mustAllege: 'The violation resulted from: (a) official policy; (b) widespread practice so persistent as to constitute custom; (c) decision by final policymaker; or (d) failure to train amounting to deliberate indifference',
      typicalEvidence: ['Written policies', 'Training manuals', 'Prior incident records', 'Pattern evidence', 'Policymaker directives'],
      pitfalls: 'Single incident rarely sufficient. Must show policy/custom, not just respondeat superior.',
    },
    {
      number: 3,
      name: 'Moving Force Causation',
      mustAllege: 'The policy or custom was the "moving force" behind the constitutional violation',
      typicalEvidence: ['Link between policy and specific violation', 'Failure to train evidence', 'Deliberate indifference to known risk'],
      pitfalls: 'Must show direct causation between policy and harm. Not just "but for" causation.',
    },
    {
      number: 4,
      name: 'Municipal Defendant',
      mustAllege: 'Defendant is a municipality or local government entity',
      typicalEvidence: ['Municipal charter', 'Organizational documents'],
      pitfalls: 'States and state agencies have Eleventh Amendment immunity. Municipalities do not.',
    },
  ],

  '1983_fourteenth_procedural_due_process': [
    {
      number: 1,
      name: 'Protected Interest',
      mustAllege: 'Plaintiff possessed a protected property or liberty interest',
      typicalEvidence: ['Employment contract', 'Statute creating entitlement', 'Tenured status', 'Professional license'],
      pitfalls: 'At-will employment generally no property interest. Need objective source.',
    },
    {
      number: 2,
      name: 'Deprivation',
      mustAllege: 'Defendant deprived plaintiff of that interest',
      typicalEvidence: ['Termination records', 'License revocation', 'Benefit denial'],
      pitfalls: 'Must be actual deprivation, not just threatened.',
    },
    {
      number: 3,
      name: 'Inadequate Process',
      mustAllege: 'Defendant failed to provide adequate procedural protections before or after the deprivation',
      typicalEvidence: ['Lack of notice', 'No opportunity to be heard', 'Biased decisionmaker'],
      pitfalls: 'Post-deprivation remedies may satisfy due process. Check Parratt/Hudson doctrine.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Government employment', 'State power invocation'],
      pitfalls: 'Private entities generally not covered unless state action nexus.',
    },
  ],

  '1983_fourteenth_equal_protection': [
    {
      number: 1,
      name: 'Discriminatory Treatment',
      mustAllege: 'Defendant treated plaintiff differently from similarly situated individuals',
      typicalEvidence: ['Comparative treatment evidence', 'Statistical data', 'Policy documents'],
      pitfalls: 'Comparators must be genuinely similarly situated in all material respects.',
    },
    {
      number: 2,
      name: 'Discriminatory Intent',
      mustAllege: 'Defendant acted with intent to discriminate based on protected class (or irrational basis for class-of-one)',
      typicalEvidence: ['Statements by decisionmakers', 'Pattern of discrimination', 'Departures from procedure'],
      pitfalls: 'Disparate impact alone insufficient. Must show intent.',
    },
    {
      number: 3,
      name: 'Protected Class or Class of One',
      mustAllege: 'Discrimination was based on protected class (race, religion, national origin, sex) or plaintiff was intentionally singled out for different treatment without rational basis',
      typicalEvidence: ['Class membership', 'Comparative treatment', 'Lack of rational basis'],
      pitfalls: 'Different scrutiny levels apply to different classes.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Government capacity', 'State power exercise'],
      pitfalls: 'Private discrimination generally not covered.',
    },
  ],

  '1983_first_amendment_speech_restriction': [
    {
      number: 1,
      name: 'Protected Speech',
      mustAllege: 'Plaintiff engaged in speech or expressive conduct protected by the First Amendment',
      typicalEvidence: ['Speech/writing content', 'Protest records', 'Social media posts', 'Meeting minutes'],
      pitfalls: 'Not all speech is protected equally. Obscenity, true threats, and incitement may be excluded.',
    },
    {
      number: 2,
      name: 'Government Restriction',
      mustAllege: 'Government imposed a restriction, regulation, or prohibition on plaintiff\'s speech',
      typicalEvidence: ['Ordinance/policy', 'Permit denial', 'Cease-and-desist letter', 'Arrest for speech'],
      pitfalls: 'Private actors generally cannot violate First Amendment. Must be state action.',
    },
    {
      number: 3,
      name: 'Content or Viewpoint Discrimination',
      mustAllege: 'Restriction is content-based or viewpoint-based (triggering strict scrutiny) OR fails intermediate scrutiny for content-neutral restrictions',
      typicalEvidence: ['Text of restriction', 'Enforcement patterns', 'Legislative history', 'Comparative treatment of speech'],
      pitfalls: 'Content-neutral time/place/manner restrictions get intermediate scrutiny (Ward v. Rock Against Racism).',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Government employment', 'Official policy', 'State power invocation'],
      pitfalls: 'Private entities generally not covered unless state action nexus exists.',
    },
  ],

  '1983_fourth_unlawful_search_seizure': [
    {
      number: 1,
      name: 'Search or Seizure',
      mustAllege: 'Government conducted a search of plaintiff\'s person, property, papers, or effects, or seized plaintiff or plaintiff\'s property',
      typicalEvidence: ['Search warrant', 'Arrest report', 'Inventory of seized items', 'Body camera footage'],
      pitfalls: 'Must have reasonable expectation of privacy in area searched (Katz test).',
    },
    {
      number: 2,
      name: 'Without Warrant or Exception',
      mustAllege: 'Search/seizure was conducted without a valid warrant and no exception to the warrant requirement applies',
      typicalEvidence: ['Absence of warrant', 'Defective warrant affidavit', 'Warrant scope exceeded'],
      pitfalls: 'Numerous exceptions: consent, exigent circumstances, plain view, search incident to arrest, automobile, Terry stop, inventory search.',
    },
    {
      number: 3,
      name: 'Unreasonableness',
      mustAllege: 'The search or seizure was unreasonable under the totality of circumstances',
      typicalEvidence: ['Scope of search', 'Duration of detention', 'Manner of execution', 'Level of intrusion'],
      pitfalls: 'Reasonableness is the ultimate standard. Even warrantless searches may be reasonable.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['On-duty status', 'Badge/uniform', 'Invocation of authority'],
      pitfalls: 'Private searches not covered unless acting as government agent.',
    },
    {
      number: 5,
      name: 'Injury/Damages',
      mustAllege: 'Plaintiff suffered injury as a result of the unlawful search or seizure',
      typicalEvidence: ['Property damage', 'Emotional distress', 'Lost property', 'Criminal charges from fruits of search'],
      pitfalls: 'Exclusionary rule is separate remedy. Civil damages require actual injury.',
    },
  ],

  '1983_fourteenth_substantive_due_process': [
    {
      number: 1,
      name: 'Fundamental Right or Liberty Interest',
      mustAllege: 'Government action infringed a fundamental right or liberty interest protected by substantive due process',
      typicalEvidence: ['Nature of right at issue', 'Historical recognition', 'Constitutional text'],
      pitfalls: 'Right must be "deeply rooted in this Nation\'s history and tradition." If explicit constitutional text covers the right, use that instead (Graham v. Connor for excessive force).',
    },
    {
      number: 2,
      name: 'Conscience-Shocking Conduct',
      mustAllege: 'Government conduct was so egregious, arbitrary, or conscience-shocking that it violated substantive due process',
      typicalEvidence: ['Pattern of abuse', 'Deliberate indifference', 'Intentional harm', 'No legitimate justification'],
      pitfalls: 'Negligence never shocks the conscience. Deliberate indifference may suffice only where time for deliberation exists (County of Sacramento v. Lewis).',
    },
    {
      number: 3,
      name: 'No Rational Basis (Non-Fundamental Rights)',
      mustAllege: 'For non-fundamental rights: government action lacks any rational relationship to a legitimate state interest',
      typicalEvidence: ['Absence of justification', 'Arbitrary targeting', 'No legitimate purpose'],
      pitfalls: 'Rational basis review is highly deferential. Court will hypothesize legitimate purposes.',
    },
    {
      number: 4,
      name: 'State Action',
      mustAllege: 'Defendant acted under color of state law',
      typicalEvidence: ['Government capacity', 'Official acts', 'Policy implementation'],
      pitfalls: 'No affirmative duty to protect from private violence (DeShaney) absent special relationship.',
    },
  ],

  '1985_conspiracy': [
    {
      number: 1,
      name: 'Conspiracy/Agreement',
      mustAllege: 'Two or more persons conspired (agreed) to deprive plaintiff of constitutional rights',
      typicalEvidence: ['Communications between defendants', 'Coordinated actions', 'Meeting records', 'Parallel conduct'],
      pitfalls: 'Must show actual agreement, not just parallel conduct. Intracorporate conspiracy doctrine may bar claims against employees of same entity.',
    },
    {
      number: 2,
      name: 'Class-Based Animus',
      mustAllege: 'Conspiracy was motivated by class-based, invidiously discriminatory animus (race, religion, national origin, etc.)',
      typicalEvidence: ['Discriminatory statements', 'Pattern targeting protected class', 'Comparative treatment'],
      pitfalls: 'Under § 1985(3), must show class-based animus. Political affiliation may not qualify in all circuits.',
    },
    {
      number: 3,
      name: 'Overt Act',
      mustAllege: 'One or more conspirators committed an overt act in furtherance of the conspiracy',
      typicalEvidence: ['Specific actions taken', 'Timeline of events', 'Implementation of agreement'],
      pitfalls: 'At least one overt act required. Must be connected to the conspiratorial purpose.',
    },
    {
      number: 4,
      name: 'Deprivation of Rights',
      mustAllege: 'Plaintiff was deprived of constitutional or statutory rights as a result of the conspiracy',
      typicalEvidence: ['Evidence of underlying rights violation', 'Harm suffered', 'Causal connection'],
      pitfalls: 'Must identify the specific constitutional right violated.',
    },
    {
      number: 5,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered injury as a result of the conspiracy',
      typicalEvidence: ['Medical records', 'Financial losses', 'Emotional distress documentation'],
      pitfalls: 'Must show actual injury proximately caused by the conspiratorial acts.',
    },
  ],

  '1986_failure_to_prevent': [
    {
      number: 1,
      name: 'Underlying § 1985 Conspiracy',
      mustAllege: 'A conspiracy actionable under 42 U.S.C. § 1985 existed',
      typicalEvidence: ['Same evidence as § 1985 claim'],
      pitfalls: '§ 1986 claim cannot exist without a viable § 1985 claim.',
    },
    {
      number: 2,
      name: 'Knowledge',
      mustAllege: 'Defendant had knowledge that the conspiracy existed and that wrongs were about to be committed',
      typicalEvidence: ['Complaints received', 'Reports filed', 'Prior incidents', 'Direct observation'],
      pitfalls: 'Must show actual knowledge or strong circumstantial evidence of knowledge.',
    },
    {
      number: 3,
      name: 'Power to Prevent',
      mustAllege: 'Defendant had power to prevent or aid in preventing the wrongs',
      typicalEvidence: ['Supervisory authority', 'Policy-making power', 'Ability to discipline'],
      pitfalls: 'Must show defendant had actual ability to intervene or prevent the harm.',
    },
    {
      number: 4,
      name: 'Failure to Act',
      mustAllege: 'Defendant neglected or refused to prevent the wrongs from being committed',
      typicalEvidence: ['Inaction documentation', 'Failure to investigate', 'Ignored reports'],
      pitfalls: 'Short 1-year SOL. Must show actual failure, not just inadequate response.',
    },
  ],

  '1983_eighth_deliberate_indifference': [
    {
      number: 1,
      name: 'State Actor Under Color of Law',
      mustAllege: 'Defendant was a state actor who acted under color of state law',
      typicalEvidence: ['Employment records', 'Badge/ID', 'Duty status', 'Government facility records'],
      pitfalls: 'Private prison contractors may or may not qualify as state actors.',
    },
    {
      number: 2,
      name: 'Serious Medical Need',
      mustAllege: 'Plaintiff had a serious medical need — one diagnosed by a physician as requiring treatment, or so obvious that a lay person would recognize the need for medical attention',
      typicalEvidence: ['Medical records', 'Diagnosis', 'Visible symptoms', 'Prior treatment history'],
      pitfalls: 'Must show condition is "sufficiently serious." Estelle v. Gamble, 429 U.S. 97 (1976).',
    },
    {
      number: 3,
      name: 'Subjective Knowledge of Risk',
      mustAllege: 'Defendant was subjectively aware of a substantial risk of serious harm to plaintiff',
      typicalEvidence: ['Grievances filed', 'Sick call requests', 'Communication to staff', 'Obvious symptoms'],
      pitfalls: 'Mere negligence or inadvertent failure is insufficient. Must show defendant actually knew of the risk.',
    },
    {
      number: 4,
      name: 'Deliberate Indifference',
      mustAllege: 'Despite knowledge of the risk, defendant deliberately disregarded it by failing to take reasonable steps to abate the danger',
      typicalEvidence: ['Delayed treatment', 'Denied treatment', 'Ignored requests', 'Inadequate response'],
      pitfalls: 'Disagreement over treatment method is generally not deliberate indifference. Must show more than negligence.',
    },
    {
      number: 5,
      name: 'Causation and Injury',
      mustAllege: 'Defendant\'s deliberate indifference caused plaintiff to suffer physical or substantial emotional injury',
      typicalEvidence: ['Worsened condition', 'Medical records showing decline', 'Pain documentation'],
      pitfalls: 'PLRA requires physical injury for emotional distress claims. 42 U.S.C. § 1997e(e).',
    },
  ],
};

export const CONSTITUTIONAL_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  '1983_fourth_excessive_force': [
    {
      type: 'standing',
      requirement: 'Actual injury from use of force',
      notes: 'Some circuits require more than de minimis injury for compensatory damages.',
    },
  ],
};

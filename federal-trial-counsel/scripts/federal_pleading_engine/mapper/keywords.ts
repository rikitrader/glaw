/**
 * Federal Pleading Engine - Keyword Dictionaries
 *
 * Pure data: keyword lists used by the fact-to-element matcher and by
 * the auto-suggest claim scorer. Keeping these large blobs isolated
 * keeps the orchestration code readable and under the 500-line cap.
 */

/**
 * Keywords associated with each element type for matching
 */
export const ELEMENT_KEYWORDS: Record<string, string[]> = {
  // Constitutional / Civil Rights elements
  'protected_activity': ['speech', 'spoke', 'said', 'wrote', 'published', 'protest', 'complaint', 'petition', 'assembly', 'religion', 'criticized', 'reported', 'whistleblow', 'opposed', 'filed charge'],
  'protected_speech': ['speech', 'expression', 'wrote', 'published', 'social media', 'protest', 'demonstration', 'petition', 'leaflet', 'sign'],
  'adverse_action': ['fired', 'terminated', 'demoted', 'suspended', 'transferred', 'disciplined', 'denied', 'rejected', 'retaliated', 'punished', 'reassigned'],
  'state_actor': ['officer', 'police', 'deputy', 'agent', 'government', 'municipal', 'city', 'county', 'state', 'federal', 'official', 'badge', 'uniform'],
  'state_action': ['officer', 'police', 'deputy', 'agent', 'government', 'municipal', 'city', 'county', 'state', 'federal', 'official', 'badge', 'uniform'],
  'seizure': ['arrest', 'detained', 'seized', 'stopped', 'handcuffed', 'custody', 'taken into'],
  'force': ['force', 'struck', 'hit', 'shot', 'tased', 'pepper spray', 'beat', 'punched', 'kicked', 'slammed', 'thrown', 'choked'],
  'search': ['search', 'warrant', 'entered', 'seized property', 'took', 'confiscated', 'ransacked', 'rummaged'],
  'probable_cause': ['without cause', 'no reason', 'wrongful', 'false', 'baseless', 'groundless'],
  'unreasonable': ['excessive', 'unnecessary', 'unreasonable', 'disproportionate', 'brutal', 'warrantless', 'no warrant'],
  'objective_unreasonable': ['excessive', 'unnecessary', 'unreasonable', 'disproportionate', 'brutal', 'Graham'],
  'government_restriction': ['banned', 'prohibited', 'restricted', 'censored', 'silenced', 'permit denied', 'ordinance', 'injunction'],
  'content_viewpoint': ['because of content', 'viewpoint', 'targeted speech', 'selective enforcement', 'content-based'],

  // Due process elements
  'protected_interest': ['property interest', 'liberty interest', 'employment', 'license', 'benefit', 'entitlement', 'tenure', 'contract'],
  'deprivation': ['deprived', 'taken', 'revoked', 'terminated', 'denied', 'lost', 'suspended', 'removed'],
  'inadequate_process': ['no hearing', 'no notice', 'without opportunity', 'biased', 'no process', 'no appeal'],
  'conscience_shocking': ['egregious', 'outrageous', 'arbitrary', 'conscience-shocking', 'shocks the conscience', 'deliberate', 'irrational'],
  'fundamental_right': ['fundamental right', 'liberty', 'privacy', 'bodily integrity', 'family', 'marriage', 'procreation'],

  // Equal protection
  'discriminatory_treatment': ['treated differently', 'discriminated', 'singled out', 'targeted', 'disparate treatment'],
  'discriminatory_intent': ['because of race', 'because of gender', 'motivated by', 'animus', 'bias', 'prejudice', 'discriminatory intent'],

  // Conspiracy (1985/1986)
  'conspiracy': ['conspired', 'agreed', 'coordinated', 'colluded', 'planned together', 'scheme', 'plot'],
  'class_based_animus': ['race', 'religion', 'national origin', 'animus', 'hatred', 'bigotry', 'class-based'],
  'overt_act': ['overt act', 'acted', 'implemented', 'carried out', 'executed', 'took steps'],
  'knowledge': ['knew', 'aware', 'informed', 'notified', 'told', 'witnessed', 'observed'],
  'power_to_prevent': ['supervisor', 'authority', 'power', 'control', 'ability to stop', 'in charge'],

  // Employment elements
  'protected_class': ['race', 'color', 'sex', 'gender', 'religion', 'national origin', 'age', 'disability', 'pregnant', 'LGBTQ', 'African American', 'Hispanic', 'Asian', 'Muslim', 'Jewish', 'Christian'],
  'qualification': ['qualified', 'performed well', 'good reviews', 'met expectations', 'experienced', 'competent'],
  'harassment': ['harassed', 'hostile', 'offensive', 'comments', 'jokes', 'slurs', 'groping', 'inappropriate', 'unwelcome', 'intimidation'],
  'severe_pervasive': ['constant', 'ongoing', 'repeated', 'daily', 'frequently', 'multiple incidents', 'pattern', 'pervasive', 'severe'],
  'employer_liability': ['supervisor', 'manager', 'HR', 'complained to', 'reported to management', 'company policy'],
  'causal_connection': ['because of', 'motivated by', 'temporal proximity', 'shortly after', 'retaliatory', 'pretext'],
  'materially_adverse': ['fired', 'terminated', 'demoted', 'reduced pay', 'schedule changed', 'reassigned', 'excluded', 'negative reference'],

  // Age discrimination (ADEA)
  'age': ['age', 'older', 'too old', 'young blood', 'fresh perspective', 'retirement', 'over 40', 'generational'],
  'but_for_cause': ['because of age', 'age was the reason', 'replaced by younger', 'age-related comments'],

  // ADA elements
  'disability': ['disability', 'disabled', 'impairment', 'wheelchair', 'ADA', 'accommodation', 'medical condition', 'chronic', 'mental health'],
  'qualified_individual': ['can perform', 'essential functions', 'qualified', 'with accommodation', 'able to work'],
  'reasonable_accommodation': ['accommodation', 'modified duties', 'leave', 'assistive', 'interactive process', 'failed to accommodate'],

  // FMLA elements
  'fmla_eligibility': ['employed', 'worked for', 'hours worked', 'eligible', 'FMLA', 'leave request'],
  'qualifying_reason': ['serious health condition', 'surgery', 'hospitalized', 'chronic condition', 'pregnancy', 'birth', 'adoption', 'family member ill', 'military'],
  'employer_interference': ['denied leave', 'refused leave', 'discouraged', 'counted as absence', 'not reinstated', 'fired for taking leave'],
  'notice_to_employer': ['requested leave', 'notified employer', 'told supervisor', 'leave request', 'medical certificate'],

  // FLSA elements
  'employment_relationship': ['employed', 'worker', 'hired', 'W-2', 'payroll', 'scheduled', 'controlled'],
  'hours_worked': ['overtime', 'hours', 'worked more than', '40 hours', 'off the clock', 'unpaid'],
  'non_exempt': ['hourly', 'non-exempt', 'not salaried', 'wage worker', 'overtime eligible'],
  'failure_to_pay': ['not paid', 'unpaid', 'withheld wages', 'underpaid', 'no overtime pay', 'minimum wage'],
  'coverage': ['interstate commerce', 'annual sales', 'revenue', 'employer size'],

  // FTCA elements
  'federal_employee': ['federal', 'VA', 'military', 'IRS', 'FBI', 'ICE', 'CBP', 'postal', 'USPS', 'government employee', 'agency', 'federal hospital', 'military doctor'],
  'negligence': ['negligent', 'careless', 'failed to', 'should have', 'breached duty', 'malpractice', 'error', 'mistake'],
  'standard_of_care': ['standard of care', 'medical standard', 'accepted practice', 'reasonable physician', 'below standard'],
  'duty': ['duty', 'obligation', 'responsibility', 'owed', 'standard of care'],
  'sf_95': ['SF-95', 'administrative claim', 'filed claim', 'tort claim', 'agency denied'],

  // Wrongful death
  'death': ['death', 'died', 'killed', 'fatal', 'deceased', 'wrongful death', 'loss of life'],
  'standing_death': ['spouse', 'children', 'estate', 'next of kin', 'dependent', 'survivor'],

  // Damages elements
  'injury': ['injury', 'injured', 'hurt', 'harm', 'damage', 'suffered', 'pain', 'broken', 'fractured', 'bruise', 'contusion', 'trauma'],
  'damages': ['medical', 'hospital', 'treatment', 'lost wages', 'lost income', 'expenses', 'bills', 'costs', 'emotional distress', 'PTSD', 'anxiety', 'depression'],

  // RICO elements
  'enterprise': ['organization', 'company', 'business', 'group', 'association', 'network', 'scheme'],
  'pattern': ['pattern', 'repeated', 'ongoing', 'continuous', 'multiple', 'scheme', 'series'],
  'racketeering': ['fraud', 'bribery', 'extortion', 'mail fraud', 'wire fraud', 'money laundering'],
  'interstate_commerce': ['interstate', 'multiple states', 'across state lines', 'national', 'foreign commerce'],
  'conduct_participation': ['operated', 'managed', 'directed', 'controlled', 'participated in management'],
  'injury_business_property': ['business loss', 'financial loss', 'property damage', 'lost profits', 'economic harm'],

  // FCA (False Claims Act)
  'false_claim': ['false claim', 'fraudulent', 'billing fraud', 'overbilling', 'phantom services', 'kickback', 'false certification'],
  'scienter': ['knowingly', 'deliberately', 'reckless disregard', 'willful blindness', 'aware', 'intentional'],
  'materiality': ['material', 'significant', 'would have affected', 'payment decision', 'relied upon'],
  'government_funds': ['Medicare', 'Medicaid', 'federal contract', 'federal grant', 'government payment', 'taxpayer funds'],

  // Antitrust
  'antitrust_agreement': ['price fixing', 'bid rigging', 'market allocation', 'agreement to restrain', 'cartel', 'collusion'],
  'restraint_of_trade': ['restrain trade', 'anticompetitive', 'price fixing', 'market allocation', 'boycott', 'exclusive dealing'],
  'monopoly_power': ['monopoly', 'market dominance', 'market share', 'no competition', 'only provider', 'dominant'],
  'anticompetitive_conduct': ['predatory pricing', 'exclusive dealing', 'tying', 'refusal to deal', 'raised rivals costs'],
  'antitrust_injury': ['higher prices', 'reduced competition', 'excluded from market', 'no alternatives'],
  'relevant_market': ['market', 'industry', 'product market', 'geographic market', 'competitors'],

  // IP elements
  'valid_copyright': ['copyright', 'registered', 'original work', 'creative work', 'authored'],
  'copying': ['copied', 'reproduced', 'duplicated', 'pirated', 'plagiarized', 'used without permission'],
  'substantial_similarity': ['substantially similar', 'identical', 'same as', 'nearly identical', 'look and feel'],
  'valid_patent': ['patent', 'patented', 'patent number', 'issued patent', 'claimed invention'],
  'infringement': ['infringed', 'used without license', 'without permission', 'unauthorized use', 'copied'],
  'valid_mark': ['trademark', 'brand', 'logo', 'service mark', 'trade name', 'registered mark'],
  'likelihood_confusion': ['confusion', 'mistaken for', 'similar mark', 'confusingly similar', 'knockoff', 'counterfeit'],

  // Consumer/Financial elements
  'consumer_report': ['credit report', 'credit bureau', 'Equifax', 'Experian', 'TransUnion', 'credit score', 'reporting agency'],
  'inaccurate_info': ['inaccurate', 'wrong', 'incorrect', 'erroneous', 'false information', 'mixed file'],
  'disputed': ['disputed', 'sent dispute', 'challenged', 'requested correction', 'reinvestigation'],
  'debt_collector': ['debt collector', 'collection agency', 'called about debt', 'collection letter', 'third-party collector'],
  'consumer_debt': ['personal debt', 'credit card', 'medical bill', 'student loan', 'mortgage', 'car loan'],
  'prohibited_practice': ['threatening', 'calling repeatedly', 'told employer', 'third party', 'false amount', 'harassing calls'],
  'disclosure_violation': ['APR', 'finance charge', 'not disclosed', 'hidden fees', 'misleading terms', 'interest rate'],

  // APA / Administrative elements
  'final_agency_action': ['final decision', 'agency denied', 'final order', 'final rule', 'agency action'],
  'arbitrary_capricious': ['arbitrary', 'capricious', 'no explanation', 'ignored evidence', 'departed from policy', 'irrational'],
  'unreasonable_delay': ['delay', 'waiting', 'pending', 'no response', 'months without action', 'years pending', 'backlog'],
  'discrete_action_owed': ['required to act', 'shall', 'mandatory', 'duty to', 'must decide', 'statutory deadline'],
  'zone_of_interests': ['affected by', 'regulated by', 'protected by statute', 'within scope'],

  // Mandamus
  'clear_right': ['clear right', 'entitled to', 'nondiscretionary', 'mandatory duty'],
  'ministerial_duty': ['ministerial', 'nondiscretionary', 'shall', 'must', 'mandatory'],
  'no_adequate_alternative': ['no other remedy', 'exhausted', 'inadequate', 'no alternative'],

  // Habeas
  'in_custody': ['imprisoned', 'detained', 'incarcerated', 'confined', 'custody', 'prison', 'jail', 'detention center'],
  'proper_respondent': ['warden', 'facility', 'BOP', 'ICE', 'detention officer', 'commandant'],
  'jurisdictional_basis': ['constitutional violation', 'illegal sentence', 'jurisdictional defect', 'unlawful detention'],
  'exhaustion': ['exhausted', 'filed grievance', 'administrative remedies', 'appealed', 'internal appeal'],

  // ERISA elements
  'erisa_plan': ['benefit plan', 'health insurance', 'pension', '401k', 'retirement plan', 'ERISA', 'employee benefit'],
  'participant_beneficiary': ['participant', 'beneficiary', 'enrolled', 'covered', 'eligible'],
  'denial_of_benefits': ['denied', 'claim denied', 'benefits denied', 'not covered', 'excluded'],
  'fiduciary_breach': ['fiduciary', 'breach of duty', 'self-dealing', 'prohibited transaction', 'imprudent'],
  'equitable_relief': ['injunction', 'reformation', 'surcharge', 'equitable', 'restitution'],

  // Tax elements
  'full_payment': ['paid tax', 'full payment', 'Flora rule', 'assessment paid'],
  'administrative_claim': ['Form 1040X', 'Form 843', 'refund claim', 'administrative claim', 'IRS claim'],
  'overpayment': ['overpaid', 'refund', 'excess tax', 'erroneous assessment'],
  'levy': ['levy', 'seized assets', 'garnished', 'IRS levy', 'bank levy', 'property seized by IRS'],
  'property_interest': ['my property', 'owned', 'not taxpayer property', 'third party property', 'wrongful levy'],

  // Monell elements
  'policy': ['policy', 'custom', 'practice', 'training', 'supervision', 'pattern', 'widespread', 'deliberate indifference'],
  'municipal': ['city', 'county', 'municipality', 'local government', 'town', 'village'],
  'moving_force': ['moving force', 'because of policy', 'caused by custom', 'failure to train', 'deliberate indifference'],

  // Bivens-specific
  'federal_actor': ['federal agent', 'FBI agent', 'DEA agent', 'ICE officer', 'CBP officer', 'federal officer', 'BOP officer'],
  'not_new_context': ['recognized context', 'Bivens', 'search and seizure', 'medical care', 'discrimination'],

  // Contract elements
  'agreement': ['contract', 'agreement', 'promised', 'deal', 'terms', 'signed'],
  'breach': ['breach', 'violated', 'failed to perform', 'did not deliver', 'broke'],
};

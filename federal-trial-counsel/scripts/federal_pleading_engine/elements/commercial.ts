/**
 * Federal Pleading Engine - Commercial Elements
 *
 * Element definitions and preconditions for False Claims Act, RICO,
 * antitrust (Sherman Act), Lanham Act, copyright, and patent claims.
 */

import { ClaimElement, ClaimPrecondition } from '../schema';

export const COMMERCIAL_ELEMENTS: Record<string, ClaimElement[]> = {
  'rico_1962c': [
    {
      number: 1,
      name: 'Enterprise',
      mustAllege: 'An enterprise exists (association-in-fact or legal entity)',
      typicalEvidence: ['Organizational structure', 'Ongoing relationships', 'Common purpose'],
      pitfalls: 'Enterprise must be distinct from defendant in some circuits. Association-in-fact requires ongoing structure.',
    },
    {
      number: 2,
      name: 'Pattern of Racketeering',
      mustAllege: 'Defendant engaged in a pattern of racketeering activity (at least 2 predicate acts within 10 years showing continuity and relationship)',
      typicalEvidence: ['Evidence of each predicate act', 'Timeline', 'Connection between acts'],
      pitfalls: 'Continuity requires either closed-ended (substantial period) or open-ended (threat of continuity). Isolated fraud schemes may fail.',
    },
    {
      number: 3,
      name: 'Conduct or Participation',
      mustAllege: 'Defendant conducted or participated in the conduct of the enterprise\'s affairs through the pattern',
      typicalEvidence: ['Role in enterprise', 'Decision-making power', 'Direction of predicate acts'],
      pitfalls: 'Mere association insufficient. Must have operation or management role (Reves test).',
    },
    {
      number: 4,
      name: 'Interstate Commerce',
      mustAllege: 'Enterprise engaged in or affected interstate commerce',
      typicalEvidence: ['Multi-state operations', 'Use of interstate communications', 'Impact on commerce'],
      pitfalls: 'Low threshold but must be alleged specifically.',
    },
    {
      number: 5,
      name: 'Injury to Business or Property',
      mustAllege: 'Plaintiff suffered injury to business or property by reason of the violation',
      typicalEvidence: ['Financial losses', 'Property damage', 'Business interruption'],
      pitfalls: 'Personal injuries alone insufficient. Must be business or property injury.',
    },
    {
      number: 6,
      name: 'Proximate Causation',
      mustAllege: 'Violation was proximate cause of injury (direct relation, no independent factors)',
      typicalEvidence: ['Direct harm chain', 'No intervening causes', 'Foreseeability'],
      pitfalls: 'Derivative injuries may not be compensable. Anza v. Ideal Steel Supply Corp.',
    },
  ],

  'false_claims_act_qui_tam': [
    {
      number: 1,
      name: 'False or Fraudulent Claim',
      mustAllege: 'Defendant submitted or caused to be submitted a false or fraudulent claim for payment to the government',
      typicalEvidence: ['Invoices', 'Claims submissions', 'Certifications', 'Billing records'],
      pitfalls: 'Rule 9(b) requires who/what/when/where/how. Specificity essential.',
    },
    {
      number: 2,
      name: 'Scienter',
      mustAllege: 'Defendant acted knowingly (actual knowledge, deliberate ignorance, or reckless disregard)',
      typicalEvidence: ['Internal communications', 'Audit findings', 'Prior warnings', 'Training records'],
      pitfalls: 'Innocent mistakes not actionable. Must show knowledge standard met.',
    },
    {
      number: 3,
      name: 'Materiality',
      mustAllege: 'The false statement or claim was material to the government\'s payment decision',
      typicalEvidence: ['Contract requirements', 'Government policies', 'Evidence of what government would have done'],
      pitfalls: 'Universal Health Services v. Escobar raised materiality bar. Government continued payment may undercut.',
    },
    {
      number: 4,
      name: 'Government Funds',
      mustAllege: 'Claim was for money or property from the United States',
      typicalEvidence: ['Federal contract', 'Grant documents', 'Medicare/Medicaid billing'],
      pitfalls: 'State-only funds may not qualify. Must trace to federal money.',
    },
  ],

  'rico_1962d_conspiracy': [
    {
      number: 1,
      name: 'Underlying RICO Violation',
      mustAllege: 'A violation of § 1962(a), (b), or (c) existed or was intended',
      typicalEvidence: ['Evidence of substantive RICO elements', 'Pattern of racketeering activity'],
      pitfalls: 'Must plead underlying substantive RICO violation. Conspiracy to violate requires knowledge of scheme.',
    },
    {
      number: 2,
      name: 'Agreement to Violate',
      mustAllege: 'Defendant knowingly agreed to facilitate a scheme which includes the operation or management of a RICO enterprise through a pattern of racketeering',
      typicalEvidence: ['Communications', 'Coordinated actions', 'Shared proceeds', 'Common scheme evidence'],
      pitfalls: 'Need not agree to personally commit predicate acts. Must know of and agree to further overall objective.',
    },
    {
      number: 3,
      name: 'Injury to Business or Property',
      mustAllege: 'Plaintiff suffered injury to business or property by reason of the conspiracy',
      typicalEvidence: ['Financial losses', 'Business damages', 'Property harm'],
      pitfalls: 'Same injury requirement as substantive RICO. Personal injuries insufficient.',
    },
  ],

  'antitrust_sherman_section_1': [
    {
      number: 1,
      name: 'Agreement/Conspiracy',
      mustAllege: 'Two or more entities entered into a contract, combination, or conspiracy',
      typicalEvidence: ['Communications', 'Parallel conduct plus-factors', 'Testimony', 'Meeting records'],
      pitfalls: 'Unilateral conduct not actionable under § 1 (use § 2 instead). Parallel conduct alone insufficient without plus-factors.',
    },
    {
      number: 2,
      name: 'Unreasonable Restraint of Trade',
      mustAllege: 'The agreement unreasonably restrains trade (per se illegal or fails rule of reason analysis)',
      typicalEvidence: ['Market analysis', 'Price effects', 'Output restrictions', 'Nature of agreement'],
      pitfalls: 'Per se categories: price fixing, market allocation, bid rigging, group boycotts. All others get rule of reason.',
    },
    {
      number: 3,
      name: 'Interstate Commerce',
      mustAllege: 'The restraint affects interstate or foreign commerce',
      typicalEvidence: ['Multi-state sales', 'Interstate customers/suppliers', 'Commerce data'],
      pitfalls: 'Low threshold but must be alleged. Purely intrastate activity may not qualify.',
    },
    {
      number: 4,
      name: 'Antitrust Injury',
      mustAllege: 'Plaintiff suffered "antitrust injury" - injury of the type the antitrust laws were designed to prevent, flowing from the anticompetitive nature of the conduct',
      typicalEvidence: ['Price increases', 'Reduced output', 'Diminished quality', 'Market exclusion'],
      pitfalls: 'Must be competition injury, not just business loss. Consumer harm is paradigmatic.',
    },
    {
      number: 5,
      name: 'Standing',
      mustAllege: 'Plaintiff is a proper antitrust plaintiff (direct purchaser, competitor, or otherwise with standing)',
      typicalEvidence: ['Direct transaction with defendants', 'Market participation', 'Proximity to violation'],
      pitfalls: 'Indirect purchasers generally barred (Illinois Brick). Antitrust standing requires efficient enforcer analysis.',
    },
  ],

  'antitrust_sherman_section_2': [
    {
      number: 1,
      name: 'Monopoly Power',
      mustAllege: 'Defendant possesses monopoly power in a relevant market (ability to control prices or exclude competition)',
      typicalEvidence: ['Market share data (typically 70%+)', 'Barriers to entry', 'Pricing power analysis'],
      pitfalls: 'Must define relevant product and geographic market. High market share alone may not suffice without barriers to entry.',
    },
    {
      number: 2,
      name: 'Relevant Market',
      mustAllege: 'Definition of the relevant product market and geographic market',
      typicalEvidence: ['Cross-elasticity of demand', 'Industry reports', 'Customer substitution patterns'],
      pitfalls: 'Market definition is often the key battleground. Too narrow or too broad defeats the claim.',
    },
    {
      number: 3,
      name: 'Anticompetitive Conduct',
      mustAllege: 'Defendant engaged in exclusionary or anticompetitive conduct to obtain or maintain monopoly power (not just competed on the merits)',
      typicalEvidence: ['Predatory pricing', 'Exclusive dealing', 'Tying arrangements', 'Refusal to deal', 'Raising rivals\' costs'],
      pitfalls: 'Merely possessing monopoly power is not illegal. Must show willful acquisition/maintenance through anticompetitive means.',
    },
    {
      number: 4,
      name: 'Antitrust Injury',
      mustAllege: 'Plaintiff suffered antitrust injury flowing from the anticompetitive conduct',
      typicalEvidence: ['Higher prices paid', 'Market exclusion', 'Reduced choices', 'Innovation harm'],
      pitfalls: 'Same antitrust injury requirement as § 1. Must flow from the anticompetitive aspect of the conduct.',
    },
  ],

  'lanham_trademark_infringement': [
    {
      number: 1,
      name: 'Valid and Protectable Mark',
      mustAllege: 'Plaintiff owns a valid and protectable trademark',
      typicalEvidence: ['Federal registration', 'Use in commerce evidence', 'Distinctiveness analysis'],
      pitfalls: 'Registration creates presumption of validity. Without registration, must prove distinctiveness (especially for descriptive marks).',
    },
    {
      number: 2,
      name: 'Use in Commerce',
      mustAllege: 'Defendant used a mark in commerce in connection with goods or services',
      typicalEvidence: ['Defendant\'s products/services', 'Advertising', 'Website', 'Packaging'],
      pitfalls: 'Non-commercial use (news reporting, commentary) may be protected.',
    },
    {
      number: 3,
      name: 'Likelihood of Confusion',
      mustAllege: 'Defendant\'s use creates a likelihood of confusion as to source, sponsorship, or affiliation',
      typicalEvidence: ['Multi-factor confusion analysis', 'Consumer surveys', 'Actual confusion evidence', 'Mark similarity'],
      pitfalls: 'Courts use multi-factor test (varies by circuit). Key factors: mark similarity, goods proximity, strength of mark, actual confusion.',
    },
    {
      number: 4,
      name: 'Damages/Relief',
      mustAllege: 'Plaintiff suffered or will suffer damage from the infringement',
      typicalEvidence: ['Lost profits', 'Defendant\'s profits', 'Licensing royalty', 'Brand dilution evidence'],
      pitfalls: 'Can seek injunction, damages, defendant\'s profits, attorney fees in exceptional cases.',
    },
  ],

  'copyright_infringement': [
    {
      number: 1,
      name: 'Valid Copyright',
      mustAllege: 'Plaintiff owns a valid copyright in an original work of authorship',
      typicalEvidence: ['Copyright registration certificate', 'Date of creation', 'Authorship evidence'],
      pitfalls: 'Registration required before filing suit (or refusal to register). Registration within 3 months of publication or before infringement enables statutory damages.',
    },
    {
      number: 2,
      name: 'Copying',
      mustAllege: 'Defendant copied protected elements of the work (direct evidence or circumstantial: access + substantial similarity)',
      typicalEvidence: ['Side-by-side comparison', 'Access evidence', 'Expert analysis', 'Digital fingerprinting'],
      pitfalls: 'Independent creation is a complete defense. Must show copying, not just similarity.',
    },
    {
      number: 3,
      name: 'Protected Expression',
      mustAllege: 'The elements copied constitute protectable expression (not ideas, facts, scenes-a-faire, or merger)',
      typicalEvidence: ['Analysis distinguishing idea from expression', 'Creative choices made', 'Original elements'],
      pitfalls: 'Copyright protects expression, not ideas (idea-expression dichotomy). Functional elements not protected.',
    },
    {
      number: 4,
      name: 'Substantial Similarity',
      mustAllege: 'Copying was substantial enough that an ordinary observer would find the works substantially similar in protected expression',
      typicalEvidence: ['Expert comparison', 'Lay observer analysis', 'Quantitative and qualitative similarity'],
      pitfalls: 'De minimis copying not actionable. Must be substantial taking of protected expression.',
    },
  ],

  'patent_infringement': [
    {
      number: 1,
      name: 'Valid Patent',
      mustAllege: 'Plaintiff owns a valid, enforceable patent that has not expired',
      typicalEvidence: ['Patent certificate', 'Assignment records', 'Maintenance fee records'],
      pitfalls: 'Defendant will likely challenge validity (anticipation, obviousness, § 101 eligibility). Patent presumed valid (clear and convincing evidence to overcome).',
    },
    {
      number: 2,
      name: 'Infringement',
      mustAllege: 'Defendant makes, uses, sells, offers to sell, or imports within the US a product or process that infringes one or more claims of the patent',
      typicalEvidence: ['Claim charts mapping claims to accused product', 'Product analysis', 'Technical expert opinion'],
      pitfalls: 'Must show infringement of at least one independent claim. Claim construction (Markman) often outcome-determinative.',
    },
    {
      number: 3,
      name: 'Claim Construction',
      mustAllege: 'Under proper construction of patent claims, accused product/process meets each claim limitation (literally or under doctrine of equivalents)',
      typicalEvidence: ['Specification', 'Prosecution history', 'Expert testimony on claim scope'],
      pitfalls: 'Prosecution history estoppel may limit equivalents. Phillips v. AWH Corp. governs claim construction.',
    },
    {
      number: 4,
      name: 'Damages',
      mustAllege: 'Plaintiff suffered damages (lost profits or reasonable royalty)',
      typicalEvidence: ['Financial records', 'Market analysis', 'Licensing comparables', 'Expert damages report'],
      pitfalls: 'Must apportion damages to patented feature. Entire market value rule applies only in narrow circumstances.',
    },
  ],
};

export const COMMERCIAL_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  'false_claims_act_qui_tam': [
    {
      type: 'standing',
      requirement: 'Relator must be an "original source" of the information',
      notes: 'Public disclosure bar may prevent suit if information already public. First-to-file bar prevents duplicate relators.',
    },
  ],

  'copyright_infringement': [
    {
      type: 'standing',
      requirement: 'Copyright registration (or refusal to register) required before filing suit',
      notes: 'After Fourth Estate v. Wall-Street.com (2019): registration must be issued or refused, not just applied for.',
    },
  ],
};

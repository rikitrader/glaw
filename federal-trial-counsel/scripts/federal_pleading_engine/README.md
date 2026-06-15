# Federal Causes of Action: Elements + Pleading Engine

A comprehensive TypeScript-based engine for drafting Rule 12(b)(6)-resilient federal complaints with element-by-element analysis, plausibility hardening, and MTD risk scoring.

## Overview

This engine transforms fact packets into production-ready federal pleadings by:

1. **Elements Analysis** - Mapping facts to required legal elements for each cause of action
2. **Plausibility Hardening** - Ensuring Twombly/Iqbal compliance with specific factual allegations
3. **Risk Scoring** - Identifying Rule 12(b)(6) vulnerabilities before filing
4. **Gap Detection** - Flagging missing facts required for viable claims

## Installation

```bash
cd scripts/federal_pleading_engine
npm install
npm run build
```

## Usage

### CLI Usage

```bash
# Generate pleadings from case input
node dist/cli.js --input examples/sample_case_input.json --out out/

# Auto-suggest claims based on facts
node dist/cli.js --input case.json --suggest

# Generate specific claims only
node dist/cli.js --input case.json --claims "1983_fourth_excessive_force,1983_monell_municipal_liability"
```

### Programmatic Usage

```typescript
import { CaseInput } from './schema';
import { mapFactsToElements } from './mapper';
import { generateDraftCount } from './drafter';
import { calculateMTDRisk } from './risk';

const caseInput: CaseInput = {
  // ... case data
};

// Map facts to elements
const mapping = mapFactsToElements(caseInput, '1983_fourth_excessive_force');

// Generate draft count
const draftCount = generateDraftCount(caseInput, '1983_fourth_excessive_force', mapping);

// Calculate MTD risk
const risk = calculateMTDRisk(caseInput, '1983_fourth_excessive_force', mapping);
```

## Input Format

The engine accepts a structured JSON input (CASE_INPUT):

```json
{
  "court": {
    "district": "Middle District of Florida",
    "division": "Orlando",
    "state": "FL"
  },
  "parties": {
    "plaintiffs": [{
      "name": "John Doe",
      "citizenship": "Florida",
      "entity_type": "individual",
      "residence": "Orlando, FL"
    }],
    "defendants": [{
      "name": "City of Orlando",
      "type": "local",
      "capacity": "official",
      "citizenship": "Florida",
      "entity_type": "municipality",
      "role_title": "Municipal Corporation"
    }]
  },
  "facts": [{
    "date": "2025-06-15",
    "location": "Orlando, FL",
    "actors": ["Officer Smith", "John Doe"],
    "event": "Officer Smith used excessive force during traffic stop",
    "documents": ["body cam footage", "medical records"],
    "harm": "broken arm, contusions",
    "damages_estimate": "$250,000",
    "evidence": ["video", "photos"],
    "witnesses": ["Jane Doe", "Paramedic Jones"]
  }],
  "claims_requested": ["1983_fourth_excessive_force", "1983_monell_municipal_liability"],
  "relief_requested": ["money", "injunction", "fees", "costs"],
  "exhaustion": {
    "ftca_admin_claim_filed": false,
    "eeoc_charge_filed": false,
    "erisa_appeal_done": false,
    "agency_final_action": false
  },
  "limitations": {
    "key_dates": {
      "injury_date": "2025-06-15",
      "notice_date": "",
      "denial_date": ""
    }
  },
  "goals": {
    "settlement_target": "$500,000",
    "non_monetary_goals": ["policy change", "officer discipline"]
  }
}
```

## Output Structure

For each claim, the engine generates:

### 1. Elements Table

| # | Element | Must Allege | Typical Evidence | Pitfalls |
|---|---------|-------------|------------------|----------|
| 1 | State Actor | Person acting under color of state law | Badge, uniform, official capacity | Off-duty conduct may not qualify |
| 2 | Constitutional Violation | Specific right violated | Video, testimony | Must be clearly established |
| ... | ... | ... | ... | ... |

### 2. Preconditions / Jurisdiction

- Jurisdictional basis (28 U.S.C. § 1331 or § 1332)
- Exhaustion requirements
- Timing/limitations issues

### 3. Defenses / Immunities

- Qualified immunity analysis
- Sovereign immunity flags
- Procedural defenses

### 4. Pleading Checklist

Maps each fact to required elements with coverage assessment.

### 5. Draft Count

Complaint-ready cause of action with proper formatting.

### 6. Fact Gaps

Missing allegations that need to be developed.

### 7. MTD Risk Score

0-100 score with specific vulnerability flags and fixes.

## Supported Claims

### A. Constitutional / Civil Rights (42 U.S.C. § 1983)

| Key | Description | Heightened Pleading |
|-----|-------------|---------------------|
| `1983_first_amendment_retaliation` | Retaliation for protected speech | No |
| `1983_first_amendment_speech_restriction` | Prior restraint, viewpoint discrimination | No |
| `1983_fourth_false_arrest` | Arrest without probable cause | No |
| `1983_fourth_unlawful_search_seizure` | Warrantless search, excessive scope | No |
| `1983_fourth_excessive_force` | Force objectively unreasonable | No |
| `1983_fourteenth_procedural_due_process` | Deprivation without adequate process | No |
| `1983_fourteenth_substantive_due_process` | Conduct shocks the conscience | No |
| `1983_fourteenth_equal_protection` | Discriminatory treatment | No |
| `1983_monell_municipal_liability` | Policy/custom caused violation | No |
| `1985_conspiracy` | Conspiracy to deprive rights | No |
| `1986_failure_to_prevent` | Failure to prevent conspiracy | No |

### B. Bivens Claims (Federal Actors)

| Key | Description | Viability Note |
|-----|-------------|----------------|
| `bivens_fourth_search_seizure` | Fourth Amendment | VERIFY - Modern limits apply |
| `bivens_fifth_due_process` | Fifth Amendment | VERIFY - Rarely extended |
| `bivens_eighth_deliberate_indifference` | Eighth Amendment | VERIFY - Limited contexts |

### C. Administrative / APA

| Key | Description | Exhaustion Required |
|-----|-------------|---------------------|
| `apa_arbitrary_capricious` | Agency action abuse | Final agency action |
| `apa_unlawful_withholding_unreasonable_delay` | Agency inaction | Final agency action |
| `mandamus_compel_ministerial_duty` | Compel non-discretionary duty | N/A |
| `habeas_detention_challenge` | Challenge to detention | Varies |

### D. Employment / Civil Rights

| Key | Description | Exhaustion Required |
|-----|-------------|---------------------|
| `title_vii_disparate_treatment` | Intentional discrimination | EEOC charge |
| `title_vii_hostile_work_environment` | Severe/pervasive harassment | EEOC charge |
| `title_vii_retaliation` | Retaliation for protected activity | EEOC charge |
| `adea_age_discrimination` | Age-based discrimination (40+) | EEOC charge |
| `ada_title_i_employment_disability` | Disability discrimination | EEOC charge |
| `fmla_interference` | Denial of FMLA leave | None |
| `fmla_retaliation` | Retaliation for FMLA use | None |
| `flsa_unpaid_wages_overtime` | Wage and hour violations | None |

### E. FTCA (Federal Tort Claims)

| Key | Description | Exhaustion Required |
|-----|-------------|---------------------|
| `ftca_negligence` | Federal employee negligence | SF-95 admin claim |
| `ftca_medical_malpractice` | Federal medical negligence | SF-95 admin claim |
| `ftca_wrongful_death` | Death from federal negligence | SF-95 admin claim |

### F. Financial / Consumer

| Key | Description | Heightened Pleading |
|-----|-------------|---------------------|
| `fcra_inaccurate_reporting` | Credit report errors | No |
| `fdcpa_prohibited_practices` | Debt collection abuse | No |
| `tila_disclosure_violations` | Lending disclosure failures | No |

### G. Commercial / RICO / Antitrust

| Key | Description | Heightened Pleading |
|-----|-------------|---------------------|
| `false_claims_act_qui_tam` | Fraud on government | Yes (Rule 9(b)) |
| `rico_1962c` | Pattern of racketeering | Yes (Rule 9(b) for fraud) |
| `rico_1962d_conspiracy` | RICO conspiracy | Yes (Rule 9(b) for fraud) |
| `antitrust_sherman_section_1` | Restraint of trade | No |
| `antitrust_sherman_section_2` | Monopolization | No |
| `lanham_trademark_infringement` | Trademark violation | No |
| `copyright_infringement` | Copyright violation | No |
| `patent_infringement` | Patent violation | No |

### H. ERISA

| Key | Description | Exhaustion Required |
|-----|-------------|---------------------|
| `erisa_502a1b_benefits` | Denial of benefits | Internal appeal |
| `erisa_502a3_equitable_relief` | Equitable remedies | Internal appeal |

### I. Tax

| Key | Description | Special Rules |
|-----|-------------|---------------|
| `tax_refund_suit` | IRS refund claim | Full payment + admin claim |
| `tax_wrongful_levy` | Improper IRS levy | 9-month limit |

## Pleading Standards Applied

### FRCP Rule 8(a)

- Short and plain statement of jurisdiction
- Short and plain statement of claim showing entitlement to relief
- Demand for judgment

### Twombly/Iqbal Plausibility

- Each element supported by factual allegations
- "Who, what, when, where, how" for each material fact
- Legal conclusions disregarded
- Plausibility = more than possible, less than probable

### Rule 9(b) Heightened Pleading (Fraud)

- Specific identification of false statements
- Who made them, when, where, how
- Why the statements were false
- How plaintiff relied on them
- Scheme particulars if applicable

### Immunity Considerations

- **Qualified Immunity**: Was the right clearly established?
- **Sovereign Immunity**: FTCA waiver? Exceptions?
- **Absolute Immunity**: Judicial, prosecutorial, legislative?

## Adding a New Claim

To add a new cause of action:

### 1. Add to claim_library.ts

```typescript
export const CLAIM_LIBRARY: Record<string, ClaimMetadata> = {
  // ... existing claims ...

  new_claim_key: {
    name: "New Claim Name",
    category: "category_name",
    source: "Statutory citation",
    sourceType: "statute" | "constitutional" | "common_law",
    heightenedPleading: false,
    exhaustionRequired: false,
    exhaustionType: null,
    immunities: ["qualified", "sovereign"],
    typicalDefenses: ["defense1", "defense2"],
    jurisdiction: "federal_question" | "diversity",
    statueOfLimitations: "X years"
  }
};
```

### 2. Add Elements to elements.ts

```typescript
export const CLAIM_ELEMENTS: Record<string, ClaimElement[]> = {
  // ... existing elements ...

  new_claim_key: [
    {
      number: 1,
      name: "Element Name",
      mustAllege: "What must be specifically alleged",
      typicalEvidence: ["evidence1", "evidence2"],
      pitfalls: "Common mistakes"
    },
    // ... additional elements
  ]
};
```

### 3. Update Schema (if needed)

Add any claim-specific input fields to schema.ts.

### 4. Test

```bash
npm run build
node dist/cli.js --input test_case.json --claims "new_claim_key"
```

## MTD Risk Scoring

The risk score (0-100) flags these vulnerability categories:

| Category | Weight | Description |
|----------|--------|-------------|
| Standing | 15 | Injury-in-fact, causation, redressability |
| Immunity | 20 | Qualified/sovereign immunity exposure |
| Exhaustion | 15 | Administrative remedies not completed |
| SOL | 15 | Statute of limitations issues |
| Rule 9(b) | 10 | Fraud pleading particularity |
| Monell | 10 | Municipal liability sufficiency |
| Causation | 10 | But-for and proximate cause |
| Damages | 5 | Quantification and proof |

## Quality Standards

This engine produces output that:

- Satisfies Twombly/Iqbal plausibility
- Meets Rule 9(b) particularity where required
- Addresses immunity defenses proactively
- Identifies exhaustion requirements
- Flags statute of limitations issues
- Generates machine-parseable structured output

## Legal Disclaimer

This tool assists with drafting but does not constitute legal advice. All output should be reviewed by a licensed attorney before filing. The engine does NOT fabricate facts - it only uses facts provided in the input.

## File Structure

```
federal_pleading_engine/
├── skill.json           # Package configuration
├── README.md            # This documentation
├── schema.ts            # Input/output type definitions
├── claim_library.ts     # Claim metadata registry
├── elements.ts          # Element definitions per claim
├── mapper.ts            # Fact-to-element mapping
├── drafter.ts           # Count/complaint generation
├── risk.ts              # MTD risk scoring
├── cli.ts               # Command-line interface
└── examples/
    ├── sample_case_input.json
    └── sample_output.md
```

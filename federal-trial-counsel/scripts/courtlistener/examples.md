# CourtListener Search Examples

## Federal Litigation Research Scenarios

### 1. TRO/Preliminary Injunction Research

```typescript
// Find recent TRO cases in Middle District of Florida
const troResults = await searchCourtListener({
  query: 'temporary restraining order preliminary injunction',
  courts: ['flmd'],
  filed_after: '2023-01-01',
  sort: 'newest',
  limit: 20,
});

// Find Eleventh Circuit standards for injunctions
const injunctionStandards = await searchEleventhCircuit(
  'preliminary injunction likelihood success merits',
  { sort: 'relevance', limit: 10 }
);
```

### 2. Qualified Immunity Research

```typescript
// Research qualified immunity in § 1983 cases
const qiCases = await searchCourtListener({
  query: 'qualified immunity clearly established',
  courts: ['ca11', 'flmd', 'flnd', 'flsd'],
  filed_after: '2020-01-01',
  sort: 'newest',
  limit: 50,
});

// Find cases denying qualified immunity
const qiDenied = await searchCourtListener({
  query: 'qualified immunity denied motion to dismiss',
  courts: ['ca11'],
  sort: 'newest',
  limit: 20,
});
```

### 3. Motion to Dismiss Standards

```typescript
// 12(b)(6) standards in Eleventh Circuit
const mtdStandards = await searchCourtListener({
  query: 'motion dismiss 12(b)(6) plausibility Twombly Iqbal',
  courts: ['ca11'],
  sort: 'relevance',
  limit: 25,
});

// Forum non conveniens
const fncCases = await searchFLMD(
  'forum non conveniens motion dismiss',
  { sort: 'newest', limit: 15 }
);
```

### 4. Discovery Dispute Research

```typescript
// Sanctions for discovery abuse
const discoverySanctions = await searchCourtListener({
  query: 'discovery sanctions Rule 37 spoliation',
  courts: ['flmd', 'ca11'],
  filed_after: '2022-01-01',
  limit: 30,
});

// Protective orders
const protectiveOrders = await searchFLMD(
  'protective order confidential discovery',
  { sort: 'newest' }
);
```

### 5. Removal/Remand Research

```typescript
// Diversity jurisdiction and removal
const removalCases = await searchCourtListener({
  query: 'removal jurisdiction diversity amount controversy',
  courts: ['ca11', 'flmd'],
  sort: 'newest',
  limit: 20,
});

// Fraudulent joinder
const fraudulentJoinder = await searchEleventhCircuit(
  'fraudulent joinder removal remand',
  { limit: 15 }
);
```

### 6. Class Action Research

```typescript
// Class certification standards
const classCertification = await searchCourtListener({
  query: 'class certification Rule 23 commonality predominance',
  courts: ['ca11'],
  sort: 'relevance',
  limit: 25,
});

// CAFA jurisdiction
const cafaCases = await searchCourtListener({
  query: 'CAFA jurisdiction minimal diversity',
  courts: ['ca11', 'flmd'],
  limit: 20,
});
```

### 7. Summary Judgment Research

```typescript
// Summary judgment standards
const sjStandards = await searchCourtListener({
  query: 'summary judgment genuine dispute material fact',
  courts: ['ca11'],
  sort: 'relevance',
  limit: 20,
});

// Partial summary judgment
const partialSJ = await searchFLMD(
  'partial summary judgment',
  { filed_after: '2023-01-01', sort: 'newest' }
);
```

### 8. Expert Witness / Daubert Research

```typescript
// Daubert challenges
const daubertCases = await searchCourtListener({
  query: 'Daubert expert testimony reliability methodology',
  courts: ['ca11', 'flmd'],
  sort: 'relevance',
  limit: 30,
});

// Expert exclusion
const expertExclusion = await searchFLMD(
  'motion exclude expert Daubert',
  { sort: 'newest', limit: 20 }
);
```

### 9. Sanctions Research

```typescript
// Rule 11 sanctions
const rule11 = await searchCourtListener({
  query: 'Rule 11 sanctions frivolous',
  courts: ['ca11', 'flmd'],
  sort: 'newest',
  limit: 25,
});

// Inherent power sanctions
const inherentPower = await searchEleventhCircuit(
  'inherent power sanctions bad faith',
  { limit: 15 }
);
```

### 10. Specific Statutory Claims

```typescript
// FDCPA claims
const fdcpaCases = await searchCourtListener({
  query: 'Fair Debt Collection Practices Act FDCPA',
  courts: ['flmd', 'ca11'],
  filed_after: '2022-01-01',
  limit: 30,
});

// TCPA claims
const tcpaCases = await searchCourtListener({
  query: 'Telephone Consumer Protection Act TCPA autodialer',
  courts: ['ca11'],
  sort: 'newest',
  limit: 25,
});

// Title VII employment discrimination
const title7Cases = await searchCourtListener({
  query: 'Title VII employment discrimination retaliation',
  courts: ['ca11', 'flmd'],
  filed_after: '2023-01-01',
  limit: 30,
});
```

---

## CLI Examples

### Basic Searches

```bash
# Simple search
npx ts-node cli.ts --q "breach of contract"

# With date filter
npx ts-node cli.ts --q "fraud" --after 2023-01-01

# With court filter
npx ts-node cli.ts --q "negligence" --court flmd

# Multiple courts
npx ts-node cli.ts --q "standing" --court flmd,ca11,scotus

# Sort by newest
npx ts-node cli.ts --q "motion to compel" --sort newest --limit 30
```

### Research Workflows

```bash
# Step 1: Find relevant cases
npx ts-node cli.ts --q "preliminary injunction standard" --court ca11 --limit 20

# Step 2: Review JSON output
cat out.json | jq '.results[].title'

# Step 3: Get more results if needed
npx ts-node cli.ts --next "https://www.courtlistener.com/api/rest/v4/search/?..."
```

### Output Options

```bash
# JSON to stdout
npx ts-node cli.ts --q "discovery" --json

# Custom output file
npx ts-node cli.ts --q "sanctions" -o sanctions-research.json

# Pipe to file
npx ts-node cli.ts --q "injunction" > injunction-research.md
```

---

## Integration with Federal Trial Counsel Skill

The CourtListener module integrates with other components:

```typescript
// In case analysis workflow
import { searchCourtListener, toMarkdown } from './courtlistener/index.js';

async function researchCaselaw(issue: string, court: string): Promise<string> {
  const results = await searchCourtListener({
    query: issue,
    courts: [court, 'ca11'], // Always include circuit court
    filed_after: '2020-01-01',
    sort: 'relevance',
    limit: 15,
  });

  return toMarkdown(results);
}

// Used by:
// - TRO Motion Generator
// - Motion to Dismiss Drafter
// - Summary Judgment Brief Builder
// - Appeal Brief Research
```

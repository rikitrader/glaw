# CourtListener Search Module

A production-ready TypeScript module for searching federal case law using the [CourtListener API](https://www.courtlistener.com/help/api/).

## Overview

This module provides:
- **Structured API client** with authentication, retry/backoff, and pagination
- **Search for opinions** (published decisions) and **dockets** (case filings)
- **Flexible filtering** by court, date range, and relevance
- **Normalized output** with consistent field names
- **Markdown formatting** for human-readable results
- **CLI tool** for quick searches from the command line

## Installation

```bash
# Navigate to the module directory
cd scripts/courtlistener

# Install TypeScript (if needed)
npm install -g typescript ts-node

# No other dependencies required - uses native fetch (Node 18+)
```

## Quick Start

### API Usage

```typescript
import { searchCourtListener, toMarkdown } from './index.js';

// Basic search
const results = await searchCourtListener({
  query: 'qualified immunity',
  courts: ['flmd', 'ca11'],
  filed_after: '2020-01-01',
  sort: 'newest',
  limit: 20,
});

// Output as Markdown
console.log(toMarkdown(results));

// Or access structured data
console.log(`Found ${results.meta.count} results`);
results.results.forEach(r => {
  console.log(`${r.title} - ${r.court} - ${r.date_filed}`);
});
```

### CLI Usage

```bash
# Basic search
npx ts-node cli.ts --q "qualified immunity"

# Search Middle District of Florida
npx ts-node cli.ts --q "motion to dismiss" --court flmd --after 2023-01-01 --sort newest

# Search multiple courts
npx ts-node cli.ts --q "standing" --court flmd,ca11,scotus --limit 50

# Output JSON only
npx ts-node cli.ts --q "injunction" --json
```

## Authentication

Authentication is optional but recommended for higher rate limits.

```bash
# Set environment variable
export COURTLISTENER_API_TOKEN="your-token-here"

# Get a token at: https://www.courtlistener.com/help/api/rest/
```

## API Reference

### `searchCourtListener(input: SearchInput): Promise<SearchOutput>`

Main search function.

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `type` | 'opinions' \| 'dockets' | No | 'opinions' | Search type |
| `courts` | string[] | No | - | Court codes (e.g., ['flmd', 'ca11']) |
| `filed_after` | string | No | - | Date filter (YYYY-MM-DD) |
| `filed_before` | string | No | - | Date filter (YYYY-MM-DD) |
| `sort` | 'relevance' \| 'newest' \| 'oldest' | No | 'relevance' | Sort order |
| `limit` | number | No | 20 | Max results (1-100) |
| `page` | number | No | - | Page number |
| `next` | string | No | - | Next page URL |

**Output:**

```typescript
interface SearchOutput {
  meta: {
    query: string;
    type: 'opinions' | 'dockets';
    count: number;      // Total results available
    fetched: number;    // Results in this response
    next?: string;      // URL for next page
  };
  results: SearchResultItem[];
}

interface SearchResultItem {
  title: string;
  court: string;
  court_name?: string;
  date_filed: string;
  citation?: string;
  url?: string;
  api_url: string;
  snippet?: string;
  docket_number?: string;
  judges?: string;
  source_fields: Record<string, unknown>;
}
```

### Convenience Functions

```typescript
// Search opinions only
searchOpinions(query, options)

// Search dockets only
searchDockets(query, options)

// Search Middle District of Florida
searchFLMD(query, options)

// Search Eleventh Circuit
searchEleventhCircuit(query, options)

// Search by citation
searchByCitation('123 F.3d 456', options)
```

### Formatting Functions

```typescript
// Full Markdown output
toMarkdown(output: SearchOutput): string

// Brief summary (5 results max)
toBriefSummary(output: SearchOutput): string
```

## Court Codes

### Supreme Court
- `scotus` - Supreme Court of the United States

### Circuit Courts of Appeals
- `ca1` through `ca11` - Numbered circuits
- `cadc` - D.C. Circuit
- `cafc` - Federal Circuit

### Florida District Courts
- `flmd` - Middle District of Florida (Orlando Division)
- `flnd` - Northern District of Florida
- `flsd` - Southern District of Florida

### Other Common Districts
- `nysd`, `nyed`, `nynd`, `nywd` - New York
- `cacd`, `cand`, `casd`, `caed` - California
- `txnd`, `txsd`, `txed`, `txwd` - Texas
- `dcd` - District of Columbia

## Pagination

When more results are available, `meta.next` contains the URL for the next page:

```typescript
// First page
const page1 = await searchCourtListener({ query: 'immunity', limit: 20 });

// Next page
if (page1.meta.next) {
  const page2 = await searchCourtListener({
    query: 'immunity',
    next: page1.meta.next,
  });
}
```

## Rate Limiting

The module handles rate limiting automatically:
- Exponential backoff with jitter
- Respects `Retry-After` header
- Max 5 retries before failing
- Clear error messages when limits exhausted

For higher limits, use an API token.

## Error Handling

```typescript
import { CourtListenerError, RateLimitError, ValidationError } from './types.js';

try {
  const results = await searchCourtListener({ query: 'test' });
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Invalid input:', error.message);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limited. Retry after:', error.retryAfter, 'seconds');
  } else if (error instanceof CourtListenerError) {
    console.error('API error:', error.statusCode, error.message);
  }
}
```

## Smoke Tests

### 1. Unauthenticated Search

```bash
# Should work without token (public API)
npx ts-node cli.ts --q "test" --court flmd --limit 5
```

### 2. Authenticated Search

```bash
# Set token first
export COURTLISTENER_API_TOKEN="your-token"
npx ts-node cli.ts --q "qualified immunity" --court ca11 --after 2022-01-01 --limit 10
```

### 3. Pagination Demo

```bash
# Get first page
npx ts-node cli.ts --q "motion" --court flmd --limit 5

# Copy the "next" URL from output, then:
npx ts-node cli.ts --next "https://www.courtlistener.com/api/rest/v4/search/?..."
```

## Architecture

```
courtlistener/
├── types.ts      # Type definitions (input/output/errors)
├── client.ts     # HTTP client with auth, retry, validation
├── format.ts     # Markdown formatting
├── index.ts      # Main exports and search logic
├── cli.ts        # Command-line interface
├── skill.json    # Skill metadata
├── README.md     # This file
└── examples.md   # Usage examples
```

**Data Flow:**
1. `searchCourtListener()` validates input via `client.validateInput()`
2. Builds URL via `client.buildSearchUrl()`
3. Fetches with retry via `client.fetchWithRetry()`
4. Normalizes raw API response to consistent `SearchOutput`
5. Returns structured data or formats via `toMarkdown()`

## Credits

- **CourtListener** by [Free Law Project](https://free.law/)
- **API Documentation**: https://www.courtlistener.com/help/api/

## License

MIT

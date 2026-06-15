#!/usr/bin/env node
/**
 * CourtListener Search CLI
 * Command-line interface for searching CourtListener
 *
 * Usage:
 *   npx ts-node cli.ts --q "search text" --court flmd --after 2020-01-01 --limit 10
 *
 * Environment:
 *   COURTLISTENER_API_TOKEN - Optional API token for authenticated requests
 */

import { searchCourtListener, toMarkdown, SearchInput } from './index.js';
import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// ARGUMENT PARSING (No Dependencies)
// ============================================================================

interface CliArgs {
  query?: string;
  type?: 'opinions' | 'dockets';
  court?: string[];
  after?: string;
  before?: string;
  sort?: 'relevance' | 'newest' | 'oldest';
  limit?: number;
  page?: number;
  next?: string;
  output?: string;
  help?: boolean;
  json?: boolean;
}

function printHelp(): void {
  console.log(`
CourtListener Search CLI
========================

Search federal case law using the CourtListener API.

USAGE:
  npx ts-node cli.ts --q <query> [options]

REQUIRED:
  --q, --query <text>     Search query text

OPTIONS:
  --type <type>           Search type: opinions (default) or dockets
  --court <code>          Court code(s), comma-separated (e.g., flmd,ca11,scotus)
  --after <date>          Filter: filed on or after (YYYY-MM-DD)
  --before <date>         Filter: filed on or before (YYYY-MM-DD)
  --sort <order>          Sort: relevance (default), newest, oldest
  --limit <n>             Max results (1-100, default 20)
  --page <n>              Page number
  --next <url>            Next page URL (from previous results)
  --output, -o <file>     Output JSON file (default: out.json)
  --json                  Output JSON to stdout instead of Markdown
  --help, -h              Show this help

COURT CODES:
  Supreme Court:  scotus
  Circuits:       ca1, ca2, ..., ca11, cadc, cafc
  Florida:        flmd (Middle), flnd (Northern), flsd (Southern)

ENVIRONMENT:
  COURTLISTENER_API_TOKEN   Optional API token for authenticated requests

EXAMPLES:
  # Basic search
  npx ts-node cli.ts --q "qualified immunity"

  # Search Middle District of Florida, recent cases
  npx ts-node cli.ts --q "motion to dismiss" --court flmd --after 2023-01-01 --sort newest

  # Search Eleventh Circuit
  npx ts-node cli.ts --q "standing" --court ca11 --limit 50

  # Paginate with next URL
  npx ts-node cli.ts --next "https://www.courtlistener.com/api/rest/v4/search/?..."

  # Output JSON only
  npx ts-node cli.ts --q "injunction" --court flmd --json
`);
}

function parseArgs(args: string[]): CliArgs {
  const result: CliArgs = {};
  let i = 0;

  while (i < args.length) {
    const arg = args[i];

    switch (arg) {
      case '--q':
      case '--query':
        result.query = args[++i];
        break;

      case '--type':
        const typeVal = args[++i];
        if (typeVal === 'opinions' || typeVal === 'dockets') {
          result.type = typeVal;
        } else {
          console.error(`Invalid type: ${typeVal}. Must be 'opinions' or 'dockets'.`);
          process.exit(1);
        }
        break;

      case '--court':
        result.court = args[++i]?.split(',').map(c => c.trim());
        break;

      case '--after':
        result.after = args[++i];
        break;

      case '--before':
        result.before = args[++i];
        break;

      case '--sort':
        const sortVal = args[++i];
        if (sortVal === 'relevance' || sortVal === 'newest' || sortVal === 'oldest') {
          result.sort = sortVal;
        } else {
          console.error(`Invalid sort: ${sortVal}. Must be 'relevance', 'newest', or 'oldest'.`);
          process.exit(1);
        }
        break;

      case '--limit':
        result.limit = parseInt(args[++i], 10);
        break;

      case '--page':
        result.page = parseInt(args[++i], 10);
        break;

      case '--next':
        result.next = args[++i];
        break;

      case '--output':
      case '-o':
        result.output = args[++i];
        break;

      case '--json':
        result.json = true;
        break;

      case '--help':
      case '-h':
        result.help = true;
        break;

      default:
        if (arg.startsWith('-')) {
          console.error(`Unknown option: ${arg}`);
          process.exit(1);
        }
        // Treat as positional query if no --q provided
        if (!result.query) {
          result.query = arg;
        }
    }

    i++;
  }

  return result;
}

// ============================================================================
// MAIN
// ============================================================================

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  // Help
  if (args.help) {
    printHelp();
    process.exit(0);
  }

  // Validate required args
  if (!args.query && !args.next) {
    console.error('Error: Query is required. Use --q <query> or --next <url>.');
    console.error('Use --help for usage information.');
    process.exit(1);
  }

  // Build search input
  const input: SearchInput = {
    query: args.query || '',
    type: args.type,
    courts: args.court,
    filed_after: args.after,
    filed_before: args.before,
    sort: args.sort,
    limit: args.limit,
    page: args.page,
    next: args.next,
    include_snippets: true,
  };

  // If using --next, query can be empty placeholder
  if (args.next && !args.query) {
    input.query = 'pagination';
  }

  try {
    // Execute search
    console.error('Searching CourtListener...');
    const results = await searchCourtListener(input);

    // Output JSON file. Security posture:
    //  - Absolute paths are honored (the user opted in explicitly).
    //  - Relative paths are anchored to cwd and rejected if they escape it
    //    via `..`, so a hosted CLI can't be tricked into writing outside cwd.
    const rawOutput = args.output || 'out.json';
    const cwd = fs.realpathSync(process.cwd());
    const outputFile = path.resolve(cwd, rawOutput);
    if (!path.isAbsolute(rawOutput)) {
      const resolvedOut = path.resolve(cwd, rawOutput);
      if (!resolvedOut.startsWith(cwd + path.sep) && resolvedOut !== cwd) {
        throw new Error(`Refusing to write output outside cwd: ${rawOutput}`);
      }
    }
    const outputDir = path.dirname(outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
    console.error(`JSON saved to: ${outputFile}`);

    // Output to stdout
    if (args.json) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      console.log(toMarkdown(results));
    }

    process.exit(0);

  } catch (error) {
    console.error(`Error: ${(error as Error).message}`);
    process.exit(1);
  }
}

// Run
main();

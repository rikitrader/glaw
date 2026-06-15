/**
 * CourtListener Result Formatter
 * Formats search results as Markdown
 */

import { SearchOutput, SearchResultItem } from './types.js';

// ============================================================================
// CONSTANTS
// ============================================================================

const MAX_SNIPPET_LENGTH = 500;

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Trim snippet to max length while preserving word boundaries
 */
export function trimSnippet(snippet: string, maxLength: number = MAX_SNIPPET_LENGTH): string {
  if (!snippet || snippet.length <= maxLength) {
    return snippet || '';
  }

  // Find the last space before maxLength
  const trimmed = snippet.substring(0, maxLength);
  const lastSpace = trimmed.lastIndexOf(' ');

  if (lastSpace > maxLength * 0.8) {
    return trimmed.substring(0, lastSpace) + '...';
  }

  return trimmed + '...';
}

/**
 * Format date for display
 */
function formatDate(dateStr: string): string {
  if (!dateStr) return 'Unknown date';

  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Escape special Markdown characters
 */
function escapeMarkdown(text: string): string {
  if (!text) return '';
  return text
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .replace(/\(/g, '\\(')
    .replace(/\)/g, '\\)')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ============================================================================
// MARKDOWN FORMATTERS
// ============================================================================

/**
 * Format a single result item as Markdown
 */
function formatResultItem(item: SearchResultItem, index: number): string {
  const lines: string[] = [];

  // Title with link
  const title = escapeMarkdown(item.title || item.case_name || 'Untitled');
  if (item.url) {
    lines.push(`### ${index + 1}. [${title}](${item.url})`);
  } else {
    lines.push(`### ${index + 1}. ${title}`);
  }

  // Court and date
  const courtInfo = item.court_name || item.court || 'Unknown Court';
  const dateInfo = formatDate(item.date_filed);
  lines.push(`**Court:** ${courtInfo} | **Filed:** ${dateInfo}`);

  // Citation
  if (item.citation) {
    lines.push(`**Citation:** ${escapeMarkdown(item.citation)}`);
  }

  // Docket number
  if (item.docket_number) {
    lines.push(`**Docket:** ${escapeMarkdown(item.docket_number)}`);
  }

  // Judges
  if (item.judges) {
    lines.push(`**Judge(s):** ${escapeMarkdown(item.judges)}`);
  }

  // Status
  if (item.status) {
    lines.push(`**Status:** ${escapeMarkdown(item.status)}`);
  }

  // Snippet
  if (item.snippet) {
    const trimmedSnippet = trimSnippet(item.snippet);
    lines.push('');
    lines.push(`> ${trimmedSnippet.replace(/\n/g, '\n> ')}`);
  }

  // API URL (for reference)
  lines.push('');
  lines.push(`*API: ${item.api_url}*`);

  return lines.join('\n');
}

/**
 * Format search filters for display
 */
function formatFilters(meta: SearchOutput['meta']): string {
  const filters: string[] = [];

  if (meta.courts && meta.courts.length > 0) {
    filters.push(`Courts: ${meta.courts.join(', ')}`);
  }

  if (meta.filed_after) {
    filters.push(`Filed after: ${meta.filed_after}`);
  }

  if (meta.filed_before) {
    filters.push(`Filed before: ${meta.filed_before}`);
  }

  if (meta.sort) {
    filters.push(`Sort: ${meta.sort}`);
  }

  return filters.length > 0 ? filters.join(' | ') : 'None';
}

// ============================================================================
// MAIN EXPORT
// ============================================================================

/**
 * Convert search output to Markdown format
 */
export function toMarkdown(output: SearchOutput): string {
  const lines: string[] = [];

  // Header
  lines.push('# CourtListener Search Results');
  lines.push('');

  // Query info
  lines.push(`**Query:** "${output.meta.query}"`);
  lines.push(`**Type:** ${output.meta.type}`);
  lines.push(`**Filters:** ${formatFilters(output.meta)}`);
  lines.push(`**Total Results:** ${output.meta.count.toLocaleString()}`);
  lines.push(`**Showing:** ${output.meta.fetched} result(s)`);
  lines.push('');

  // Divider
  lines.push('---');
  lines.push('');

  // Results
  if (output.results.length === 0) {
    lines.push('*No results found.*');
  } else {
    for (let i = 0; i < output.results.length; i++) {
      lines.push(formatResultItem(output.results[i], i));
      lines.push('');
      lines.push('---');
      lines.push('');
    }
  }

  // Pagination info
  if (output.meta.next) {
    lines.push('## Pagination');
    lines.push('');
    lines.push('More results are available. To fetch the next page:');
    lines.push('');
    lines.push('```bash');
    lines.push(`# Using CLI:`);
    lines.push(`node cli.js --next "${output.meta.next}"`);
    lines.push('```');
    lines.push('');
    lines.push('```typescript');
    lines.push('// Using API:');
    lines.push(`const nextPage = await searchCourtListener({ query: "${output.meta.query}", next: "${output.meta.next}" });`);
    lines.push('```');
    lines.push('');
  }

  // Footer
  lines.push('---');
  lines.push('*Results from [CourtListener](https://www.courtlistener.com) - Free Law Project*');

  return lines.join('\n');
}

/**
 * Format a brief summary (for quick reference)
 */
export function toBriefSummary(output: SearchOutput): string {
  const lines: string[] = [];

  lines.push(`Found ${output.meta.count} results for "${output.meta.query}" (showing ${output.meta.fetched}):`);
  lines.push('');

  for (let i = 0; i < Math.min(output.results.length, 5); i++) {
    const item = output.results[i];
    const title = item.title || item.case_name || 'Untitled';
    const date = item.date_filed || 'Unknown date';
    const citation = item.citation ? ` (${item.citation})` : '';
    lines.push(`${i + 1}. ${title}${citation} - ${date}`);
  }

  if (output.results.length > 5) {
    lines.push(`... and ${output.results.length - 5} more`);
  }

  if (output.meta.next) {
    lines.push('');
    lines.push('[More results available]');
  }

  return lines.join('\n');
}

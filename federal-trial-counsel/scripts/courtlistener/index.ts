/**
 * CourtListener Search Module
 * Main entry point for the CourtListener API integration
 *
 * Usage:
 *   import { searchCourtListener, toMarkdown } from './index.js';
 *
 *   const results = await searchCourtListener({
 *     query: 'qualified immunity',
 *     courts: ['flmd', 'ca11'],
 *     filed_after: '2020-01-01',
 *     limit: 10,
 *   });
 *
 *   console.log(toMarkdown(results));
 */

import {
  SearchInput,
  SearchOutput,
  SearchResultItem,
  CourtListenerSearchResponse,
  CourtListenerOpinionResult,
  CourtListenerDocketResult,
} from './types.js';

import {
  validateInput,
  buildSearchUrl,
  fetchWithRetry,
  getCourtName,
} from './client.js';

import { toMarkdown, toBriefSummary, trimSnippet } from './format.js';

// Re-export types and formatters
export * from './types.js';
export { toMarkdown, toBriefSummary } from './format.js';
export { COURT_CODES, getCourtName } from './client.js';

// ============================================================================
// RESULT NORMALIZATION
// ============================================================================

/**
 * Normalize an opinion result from the API
 */
function normalizeOpinionResult(raw: CourtListenerOpinionResult): SearchResultItem {
  const courtCode = raw.court_id || raw.court || '';
  const clusterId = raw.cluster_id || raw.id;

  // Build human URL if possible
  let humanUrl: string | undefined;
  if (raw.absolute_url) {
    humanUrl = `https://www.courtlistener.com${raw.absolute_url}`;
  } else if (clusterId) {
    humanUrl = `https://www.courtlistener.com/opinion/${clusterId}/`;
  }

  // Extract citation
  let citation: string | undefined;
  if (raw.citation_string) {
    citation = raw.citation_string;
  } else if (raw.citation && Array.isArray(raw.citation) && raw.citation.length > 0) {
    citation = raw.citation.join(', ');
  }

  return {
    title: raw.caseName || raw.case_name || 'Untitled Opinion',
    court: courtCode,
    court_name: getCourtName(courtCode),
    date_filed: raw.dateFiled || raw.date_filed || '',
    citation,
    url: humanUrl,
    api_url: raw.cluster ? raw.cluster : `https://www.courtlistener.com/api/rest/v4/clusters/${clusterId}/`,
    snippet: raw.snippet,
    docket_number: raw.docketNumber || raw.docket_number,
    judges: raw.judge,
    case_name: raw.caseName || raw.case_name,
    status: raw.status,
    cluster_id: clusterId,
    docket_id: raw.docket_id,
    source_fields: {
      id: raw.id,
      cluster_id: raw.cluster_id,
      docket_id: raw.docket_id,
      court_id: raw.court_id,
      status: raw.status,
    },
  };
}

/**
 * Normalize a docket result from the API
 */
function normalizeDocketResult(raw: CourtListenerDocketResult): SearchResultItem {
  const courtCode = raw.court_id || raw.court || '';
  const docketId = raw.id;

  // Build human URL if possible
  let humanUrl: string | undefined;
  if (raw.absolute_url) {
    humanUrl = `https://www.courtlistener.com${raw.absolute_url}`;
  } else if (docketId) {
    humanUrl = `https://www.courtlistener.com/docket/${docketId}/`;
  }

  return {
    title: raw.caseName || raw.case_name || 'Untitled Docket',
    court: courtCode,
    court_name: getCourtName(courtCode),
    date_filed: raw.dateFiled || raw.date_filed || '',
    url: humanUrl,
    api_url: `https://www.courtlistener.com/api/rest/v4/dockets/${docketId}/`,
    docket_number: raw.docketNumber || raw.docket_number,
    judges: raw.assigned_to_str,
    case_name: raw.caseName || raw.case_name,
    docket_id: docketId,
    source_fields: {
      id: raw.id,
      court_id: raw.court_id,
      nature_of_suit: raw.nature_of_suit,
      cause: raw.cause,
    },
  };
}

/**
 * Normalize API results based on search type
 */
function normalizeResults(
  results: Array<CourtListenerOpinionResult | CourtListenerDocketResult>,
  type: 'opinions' | 'dockets'
): SearchResultItem[] {
  if (type === 'dockets') {
    return results.map(r => normalizeDocketResult(r as CourtListenerDocketResult));
  }
  return results.map(r => normalizeOpinionResult(r as CourtListenerOpinionResult));
}

// ============================================================================
// MAIN SEARCH FUNCTION
// ============================================================================

/**
 * Search CourtListener for federal case law opinions or dockets
 *
 * @param input - Search parameters
 * @returns Normalized search results with metadata
 *
 * @example
 * // Search for qualified immunity cases in Middle District of Florida
 * const results = await searchCourtListener({
 *   query: 'qualified immunity',
 *   courts: ['flmd'],
 *   filed_after: '2020-01-01',
 *   sort: 'newest',
 *   limit: 20,
 * });
 */
export async function searchCourtListener(input: SearchInput): Promise<SearchOutput> {
  // Validate input
  validateInput(input);

  // Set defaults
  const searchType = input.type || 'opinions';
  const limit = Math.min(input.limit || 20, 100);

  // Build URL and fetch
  const url = buildSearchUrl(input);
  const response = await fetchWithRetry(url);

  // Normalize results
  const rawResults = response.results || [];
  const normalizedResults = normalizeResults(rawResults, searchType);

  // Enforce limit
  const limitedResults = normalizedResults.slice(0, limit);

  // Build output
  const output: SearchOutput = {
    meta: {
      query: input.query,
      type: searchType,
      count: response.count || 0,
      fetched: limitedResults.length,
      next: response.next || undefined,
      courts: input.courts,
      filed_after: input.filed_after,
      filed_before: input.filed_before,
      sort: input.sort,
    },
    results: limitedResults,
  };

  return output;
}

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

/**
 * Search for opinions only (convenience wrapper)
 */
export async function searchOpinions(
  query: string,
  options?: Omit<SearchInput, 'query' | 'type'>
): Promise<SearchOutput> {
  return searchCourtListener({
    query,
    type: 'opinions',
    ...options,
  });
}

/**
 * Search for dockets only (convenience wrapper)
 */
export async function searchDockets(
  query: string,
  options?: Omit<SearchInput, 'query' | 'type'>
): Promise<SearchOutput> {
  return searchCourtListener({
    query,
    type: 'dockets',
    ...options,
  });
}

/**
 * Search Middle District of Florida (convenience wrapper)
 */
export async function searchFLMD(
  query: string,
  options?: Omit<SearchInput, 'query' | 'courts'>
): Promise<SearchOutput> {
  return searchCourtListener({
    query,
    courts: ['flmd'],
    ...options,
  });
}

/**
 * Search Eleventh Circuit (convenience wrapper)
 */
export async function searchEleventhCircuit(
  query: string,
  options?: Omit<SearchInput, 'query' | 'courts'>
): Promise<SearchOutput> {
  return searchCourtListener({
    query,
    courts: ['ca11'],
    ...options,
  });
}

/**
 * Search by citation
 */
export async function searchByCitation(
  citation: string,
  options?: Omit<SearchInput, 'query'>
): Promise<SearchOutput> {
  // Citations are searched as regular queries
  return searchCourtListener({
    query: `"${citation}"`,
    ...options,
  });
}

// ============================================================================
// MODULE INFO
// ============================================================================

export const MODULE_INFO = {
  name: 'CourtListener Search',
  version: '1.0.0',
  description: 'Search federal case law using the CourtListener API',
  api: {
    base: 'https://www.courtlistener.com/api/rest/v4',
    docs: 'https://www.courtlistener.com/help/api/',
  },
  supportedCourts: {
    supreme: ['scotus'],
    circuits: ['ca1', 'ca2', 'ca3', 'ca4', 'ca5', 'ca6', 'ca7', 'ca8', 'ca9', 'ca10', 'ca11', 'cadc', 'cafc'],
    florida: ['flmd', 'flnd', 'flsd'],
  },
};

/**
 * CourtListener Search Types
 * Type definitions for the CourtListener API integration
 */

// ============================================================================
// INPUT TYPES
// ============================================================================

export interface SearchInput {
  /** Search query text (required) */
  query: string;
  /** Search type: opinions or dockets */
  type?: 'opinions' | 'dockets';
  /** Court codes to filter (e.g., ['flmd', 'ca11', 'scotus']) */
  courts?: string[];
  /** Filter results filed on or after this date (YYYY-MM-DD) */
  filed_after?: string;
  /** Filter results filed on or before this date (YYYY-MM-DD) */
  filed_before?: string;
  /** Sort order */
  sort?: 'relevance' | 'newest' | 'oldest';
  /** Maximum results to return (default 20, max 100) */
  limit?: number;
  /** Include text snippets in results */
  include_snippets?: boolean;
  /** Include full opinion text when available */
  include_full_text?: boolean;
  /** Page number for pagination */
  page?: number;
  /** Next page URL from previous response */
  next?: string;
}

// ============================================================================
// OUTPUT TYPES
// ============================================================================

export interface SearchMeta {
  query: string;
  type: 'opinions' | 'dockets';
  count: number;
  fetched: number;
  next?: string;
  courts?: string[];
  filed_after?: string;
  filed_before?: string;
  sort?: string;
}

export interface SearchResultItem {
  /** Case or opinion title */
  title: string;
  /** Court code */
  court: string;
  /** Court full name */
  court_name?: string;
  /** Date filed (YYYY-MM-DD) */
  date_filed: string;
  /** Citation if available */
  citation?: string;
  /** Human-readable URL */
  url?: string;
  /** API URL for this resource */
  api_url: string;
  /** Text snippet with search highlights */
  snippet?: string;
  /** Docket number */
  docket_number?: string;
  /** Judge names */
  judges?: string;
  /** Case name parties */
  case_name?: string;
  /** Opinion type (e.g., "Published", "Unpublished") */
  status?: string;
  /** Cluster ID for opinions */
  cluster_id?: number;
  /** Docket ID */
  docket_id?: number;
  /** Minimal subset of raw API fields */
  source_fields: Record<string, unknown>;
}

export interface SearchOutput {
  meta: SearchMeta;
  results: SearchResultItem[];
}

// ============================================================================
// API RESPONSE TYPES (Minimal)
// ============================================================================

export interface CourtListenerOpinionResult {
  id?: number;
  absolute_url?: string;
  cluster_id?: number;
  cluster?: string;
  court?: string;
  court_id?: string;
  court_citation_string?: string;
  caseName?: string;
  case_name?: string;
  caseNameShort?: string;
  dateFiled?: string;
  date_filed?: string;
  docket_id?: number;
  docketNumber?: string;
  docket_number?: string;
  judge?: string;
  citation?: string[];
  citation_string?: string;
  suitNature?: string;
  snippet?: string;
  text?: string;
  status?: string;
  [key: string]: unknown;
}

export interface CourtListenerDocketResult {
  id?: number;
  absolute_url?: string;
  court?: string;
  court_id?: string;
  case_name?: string;
  caseName?: string;
  date_filed?: string;
  dateFiled?: string;
  docket_number?: string;
  docketNumber?: string;
  assigned_to_str?: string;
  referred_to_str?: string;
  nature_of_suit?: string;
  cause?: string;
  [key: string]: unknown;
}

export interface CourtListenerSearchResponse {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: Array<CourtListenerOpinionResult | CourtListenerDocketResult>;
}

// ============================================================================
// ERROR TYPES
// ============================================================================

export class CourtListenerError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public retryAfter?: number
  ) {
    super(message);
    this.name = 'CourtListenerError';
  }
}

export class RateLimitError extends CourtListenerError {
  constructor(retryAfter?: number) {
    super(`Rate limited. Retry after ${retryAfter || 'unknown'} seconds.`, 429, retryAfter);
    this.name = 'RateLimitError';
  }
}

export class ValidationError extends CourtListenerError {
  constructor(message: string) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

/**
 * CourtListener API Client
 * Handles HTTP requests, authentication, retries, backoff, and pagination
 */

import {
  SearchInput,
  CourtListenerSearchResponse,
  CourtListenerError,
  RateLimitError,
  ValidationError,
} from './types.js';

// ============================================================================
// CONSTANTS
// ============================================================================

const BASE_URL = 'https://www.courtlistener.com/api/rest/v4';
const MAX_RETRIES = 5;
const INITIAL_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 32000;

/**
 * Redact the API token from any string (URL, headers dump, error message).
 * Always call this before printing a message that might include request state.
 */
function redactToken(message: string): string {
  const token = process.env.COURTLISTENER_API_TOKEN;
  if (!token) return message;
  return message.split(token).join('[REDACTED]');
}

// ============================================================================
// VALIDATION
// ============================================================================

/**
 * Validate date format (YYYY-MM-DD)
 */
function validateDate(date: string, fieldName: string): void {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(date)) {
    throw new ValidationError(`Invalid ${fieldName} format. Expected YYYY-MM-DD, got: ${date}`);
  }
  const parsed = new Date(date);
  if (isNaN(parsed.getTime())) {
    throw new ValidationError(`Invalid ${fieldName} date: ${date}`);
  }
}

/**
 * Validate court codes (alphanumeric and underscore only)
 */
function validateCourt(court: string): void {
  const courtRegex = /^[a-zA-Z0-9_]+$/;
  if (!courtRegex.test(court)) {
    throw new ValidationError(`Invalid court code: ${court}. Only letters, numbers, and underscores allowed.`);
  }
}

/**
 * Validate next URL is a valid CourtListener API URL
 */
function validateNextUrl(url: string): void {
  const validPrefix = 'https://www.courtlistener.com/api/rest/v4/search/';
  if (!url.startsWith(validPrefix)) {
    throw new ValidationError(`Invalid next URL. Must be a CourtListener API search URL.`);
  }
}

/**
 * Validate all search input parameters
 */
export function validateInput(input: SearchInput): void {
  if (!input.query || typeof input.query !== 'string' || input.query.trim().length === 0) {
    throw new ValidationError('Query is required and must be a non-empty string.');
  }

  if (input.type && !['opinions', 'dockets'].includes(input.type)) {
    throw new ValidationError('Type must be "opinions" or "dockets".');
  }

  if (input.courts) {
    if (!Array.isArray(input.courts)) {
      throw new ValidationError('Courts must be an array of court codes.');
    }
    input.courts.forEach(validateCourt);
  }

  if (input.filed_after) {
    validateDate(input.filed_after, 'filed_after');
  }

  if (input.filed_before) {
    validateDate(input.filed_before, 'filed_before');
  }

  if (input.sort && !['relevance', 'newest', 'oldest'].includes(input.sort)) {
    throw new ValidationError('Sort must be "relevance", "newest", or "oldest".');
  }

  if (input.limit !== undefined) {
    if (typeof input.limit !== 'number' || input.limit < 1 || input.limit > 100) {
      throw new ValidationError('Limit must be a number between 1 and 100.');
    }
  }

  if (input.next) {
    validateNextUrl(input.next);
  }
}

// ============================================================================
// URL BUILDING
// ============================================================================

/**
 * Build the API URL from search input
 */
export function buildSearchUrl(input: SearchInput): string {
  // If next URL is provided, use it directly (already validated)
  if (input.next) {
    return input.next;
  }

  const params = new URLSearchParams();

  // Query
  params.set('q', input.query);

  // Type: 'o' for opinions, 'd' for dockets
  const type = input.type === 'dockets' ? 'd' : 'o';
  params.set('type', type);

  // Court filter
  if (input.courts && input.courts.length > 0) {
    params.set('court', input.courts.join(','));
  }

  // Date range
  if (input.filed_after) {
    params.set('filed_after', input.filed_after);
  }
  if (input.filed_before) {
    params.set('filed_before', input.filed_before);
  }

  // Sort order
  if (input.sort) {
    let orderBy: string;
    switch (input.sort) {
      case 'newest':
        orderBy = 'dateFiled desc';
        break;
      case 'oldest':
        orderBy = 'dateFiled asc';
        break;
      default:
        orderBy = 'score desc';
    }
    params.set('order_by', orderBy);
  }

  // Page
  if (input.page && input.page > 1) {
    params.set('page', input.page.toString());
  }

  return `${BASE_URL}/search/?${params.toString()}`;
}

// ============================================================================
// HTTP CLIENT WITH RETRY/BACKOFF
// ============================================================================

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate backoff with jitter
 */
function calculateBackoff(attempt: number): number {
  const exponential = Math.min(INITIAL_BACKOFF_MS * Math.pow(2, attempt), MAX_BACKOFF_MS);
  const jitter = Math.random() * 0.3 * exponential; // 0-30% jitter
  return Math.floor(exponential + jitter);
}

/**
 * Get auth headers if token is available
 */
function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Accept': 'application/json',
    'User-Agent': 'FederalTrialCounsel-ClaudeSkill/1.0',
  };

  const token = process.env.COURTLISTENER_API_TOKEN;
  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  return headers;
}

/**
 * Execute HTTP request with retry and exponential backoff
 */
export async function fetchWithRetry(url: string): Promise<CourtListenerSearchResponse> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: getHeaders(),
      });

      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
        if (attempt < MAX_RETRIES - 1) {
          const backoff = Math.max(retryAfter * 1000, calculateBackoff(attempt));
          console.error(`Rate limited. Waiting ${backoff}ms before retry ${attempt + 1}/${MAX_RETRIES}...`);
          await sleep(backoff);
          continue;
        }
        throw new RateLimitError(retryAfter);
      }

      // Handle server errors with retry
      if (response.status >= 500 && response.status < 600) {
        if (attempt < MAX_RETRIES - 1) {
          const backoff = calculateBackoff(attempt);
          console.error(`Server error ${response.status}. Waiting ${backoff}ms before retry ${attempt + 1}/${MAX_RETRIES}...`);
          await sleep(backoff);
          continue;
        }
        throw new CourtListenerError(`Server error: ${response.status}`, response.status);
      }

      // Handle client errors (no retry)
      if (!response.ok) {
        const body = await response.text();
        throw new CourtListenerError(
          redactToken(`API error: ${response.status} - ${body}`),
          response.status
        );
      }

      // Parse and return JSON
      const data = await response.json() as CourtListenerSearchResponse;
      return data;

    } catch (error) {
      lastError = error as Error;

      // Don't retry validation or client errors
      if (error instanceof ValidationError) {
        throw error;
      }
      if (error instanceof CourtListenerError && error.statusCode && error.statusCode < 500) {
        throw error;
      }

      // Retry network errors
      if (attempt < MAX_RETRIES - 1) {
        const backoff = calculateBackoff(attempt);
        console.error(redactToken(`Request failed: ${(error as Error).message}. Waiting ${backoff}ms before retry ${attempt + 1}/${MAX_RETRIES}...`));
        await sleep(backoff);
      }
    }
  }

  throw lastError || new CourtListenerError('Max retries exceeded');
}

// ============================================================================
// COURT CODE MAPPINGS
// ============================================================================

export const COURT_CODES: Record<string, string> = {
  // Supreme Court
  'scotus': 'Supreme Court of the United States',

  // Circuit Courts
  'ca1': 'First Circuit Court of Appeals',
  'ca2': 'Second Circuit Court of Appeals',
  'ca3': 'Third Circuit Court of Appeals',
  'ca4': 'Fourth Circuit Court of Appeals',
  'ca5': 'Fifth Circuit Court of Appeals',
  'ca6': 'Sixth Circuit Court of Appeals',
  'ca7': 'Seventh Circuit Court of Appeals',
  'ca8': 'Eighth Circuit Court of Appeals',
  'ca9': 'Ninth Circuit Court of Appeals',
  'ca10': 'Tenth Circuit Court of Appeals',
  'ca11': 'Eleventh Circuit Court of Appeals',
  'cadc': 'D.C. Circuit Court of Appeals',
  'cafc': 'Federal Circuit Court of Appeals',

  // Florida District Courts
  'flmd': 'Middle District of Florida',
  'flnd': 'Northern District of Florida',
  'flsd': 'Southern District of Florida',

  // Other common districts
  'txnd': 'Northern District of Texas',
  'txsd': 'Southern District of Texas',
  'txed': 'Eastern District of Texas',
  'txwd': 'Western District of Texas',
  'nysd': 'Southern District of New York',
  'nynd': 'Northern District of New York',
  'nyed': 'Eastern District of New York',
  'nywd': 'Western District of New York',
  'cacd': 'Central District of California',
  'cand': 'Northern District of California',
  'casd': 'Southern District of California',
  'caed': 'Eastern District of California',
  'dcd': 'District of Columbia',
};

/**
 * Get full court name from code
 */
export function getCourtName(code: string): string {
  return COURT_CODES[code.toLowerCase()] || code;
}

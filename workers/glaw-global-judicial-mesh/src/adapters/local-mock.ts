import { GenericLegalSourceAdapter } from './template';
import type { CourtJurisdictionCoverage, LegalSearchQuery, ProviderReview, ProviderSearchResult, RawProviderRecord, SearchContext } from '../types';

const mockReview: ProviderReview = { lifecycle: 'ACTIVE', termsReviewed: true, schemaValidated: true, authorityValidated: true, securityReviewed: true, approvedBy: 'LOCAL_MOCK_ONLY', approvedAt: '2026-08-25', notes: ['Synthetic fixture mode. Never legal authority. Never enable in production.'] };

export class LocalMockLegalSourceAdapter extends GenericLegalSourceAdapter {
  override review: ProviderReview = { ...mockReview };
  override capabilities = { search: true, caseLookup: true, docketLookup: true, citationLookup: true, documentDownload: true, bulkAccess: true, apiAvailable: true, scrapingPermitted: false, authRequired: false, paidAccess: false, robotsRestricted: false } as const;
  constructor(id: string, jurisdiction: string[], endpoint: string, coverage: CourtJurisdictionCoverage[], private readonly fixture: RawProviderRecord) { super(id, jurisdiction, endpoint, coverage); }
  override async searchCases(query: LegalSearchQuery, context: SearchContext): Promise<ProviderSearchResult[]> { this.assertRoutable(); void context; const haystack = `${this.fixture.caseName} ${this.fixture.court} ${this.fixture.citation} ${this.fixture.snippet}`.toLowerCase(); if (query.text && !haystack.includes(query.text.toLowerCase()) && !query.text.toLowerCase().includes('synthetic') && !query.text.toLowerCase().includes('legal')) return []; return [{ provider: this.id, raw: this.fixture, provenance: { provider: this.id, originalUrl: this.fixture.sourceUrl, retrievedAt: new Date().toISOString(), contentHash: 'mock-content-hash' } }]; }
}

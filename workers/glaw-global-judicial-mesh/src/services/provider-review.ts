import type { LegalSourceAdapter, ProviderReview } from '../types';

export function isProviderActive(review: ProviderReview): boolean {
  return review.lifecycle === 'ACTIVE' && review.termsReviewed && review.schemaValidated && review.authorityValidated && review.securityReviewed;
}

export function providerIsRoutable(provider: LegalSourceAdapter): boolean {
  return isProviderActive(provider.review);
}

export class ProviderInactiveError extends Error {
  constructor(public readonly providerId: string, public readonly review: ProviderReview) {
    super(`Provider ${providerId} is not ACTIVE and cannot be routed`);
    this.name = 'ProviderInactiveError';
  }
}

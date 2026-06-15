/**
 * Federal Pleading Engine - Claim Library (barrel)
 *
 * Aggregates category-specific claim metadata maps into the master
 * CLAIM_LIBRARY registry and re-exports the public helper API.
 */

import { ClaimMetadata, ClaimCategory, ImmunityType } from './schema';
import { CONSTITUTIONAL_CLAIMS } from './claim_library/constitutional';
import { BIVENS_CLAIMS } from './claim_library/bivens';
import { ADMINISTRATIVE_CLAIMS } from './claim_library/administrative';
import { EMPLOYMENT_CLAIMS } from './claim_library/employment';
import { TORT_GOVT_CLAIMS } from './claim_library/tort_govt';
import { FINANCIAL_CONSUMER_CLAIMS } from './claim_library/financial_consumer';
import { COMMERCIAL_CLAIMS } from './claim_library/commercial';
import { ERISA_CLAIMS } from './claim_library/erisa';
import { TAX_CLAIMS } from './claim_library/tax';

/**
 * Master claim library with metadata for each cause of action
 */
export const CLAIM_LIBRARY: Record<string, ClaimMetadata> = {
  ...CONSTITUTIONAL_CLAIMS,
  ...BIVENS_CLAIMS,
  ...ADMINISTRATIVE_CLAIMS,
  ...EMPLOYMENT_CLAIMS,
  ...TORT_GOVT_CLAIMS,
  ...FINANCIAL_CONSUMER_CLAIMS,
  ...COMMERCIAL_CLAIMS,
  ...ERISA_CLAIMS,
  ...TAX_CLAIMS,
};

/** Get all claim keys for a specific category */
export function getClaimsByCategory(category: ClaimCategory): string[] {
  return Object.entries(CLAIM_LIBRARY)
    .filter(([_, meta]) => meta.category === category)
    .map(([key, _]) => key);
}

/** Get claims that require exhaustion */
export function getClaimsRequiringExhaustion(): string[] {
  return Object.entries(CLAIM_LIBRARY)
    .filter(([_, meta]) => meta.exhaustionRequired)
    .map(([key, _]) => key);
}

/** Get claims with heightened pleading (Rule 9(b)) */
export function getHeightenedPleadingClaims(): string[] {
  return Object.entries(CLAIM_LIBRARY)
    .filter(([_, meta]) => meta.heightenedPleading)
    .map(([key, _]) => key);
}

/** Get claims with immunity concerns */
export function getClaimsWithImmunity(immunityType: ImmunityType): string[] {
  return Object.entries(CLAIM_LIBRARY)
    .filter(([_, meta]) => meta.immunities.includes(immunityType))
    .map(([key, _]) => key);
}

/** Get all claim keys */
export function getAllClaimKeys(): string[] {
  return Object.keys(CLAIM_LIBRARY);
}

/** Check if a claim key exists */
export function isValidClaimKey(key: string): boolean {
  return key in CLAIM_LIBRARY;
}

/** Get claim metadata by key */
export function getClaimMetadata(key: string): ClaimMetadata | undefined {
  return CLAIM_LIBRARY[key];
}

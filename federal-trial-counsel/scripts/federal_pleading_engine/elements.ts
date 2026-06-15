/**
 * Federal Pleading Engine - Elements Barrel
 * Thin aggregator: merges per-category maps from ./elements/<category>.ts.
 */

import { ClaimElement, ClaimPrecondition } from './schema';
import { CONSTITUTIONAL_ELEMENTS, CONSTITUTIONAL_PRECONDITIONS } from './elements/constitutional';
import { BIVENS_ELEMENTS, BIVENS_PRECONDITIONS } from './elements/bivens';
import { ADMINISTRATIVE_ELEMENTS, ADMINISTRATIVE_PRECONDITIONS } from './elements/administrative';
import { EMPLOYMENT_ELEMENTS, EMPLOYMENT_PRECONDITIONS } from './elements/employment';
import { TORT_GOVT_ELEMENTS, TORT_GOVT_PRECONDITIONS } from './elements/tort_govt';
import { FINANCIAL_CONSUMER_ELEMENTS, FINANCIAL_CONSUMER_PRECONDITIONS } from './elements/financial_consumer';
import { COMMERCIAL_ELEMENTS, COMMERCIAL_PRECONDITIONS } from './elements/commercial';
import { ERISA_ELEMENTS, ERISA_PRECONDITIONS } from './elements/erisa';
import { TAX_ELEMENTS, TAX_PRECONDITIONS } from './elements/tax';

export const CLAIM_ELEMENTS: Record<string, ClaimElement[]> = {
  ...CONSTITUTIONAL_ELEMENTS, ...BIVENS_ELEMENTS, ...ADMINISTRATIVE_ELEMENTS,
  ...EMPLOYMENT_ELEMENTS, ...TORT_GOVT_ELEMENTS, ...FINANCIAL_CONSUMER_ELEMENTS,
  ...COMMERCIAL_ELEMENTS, ...ERISA_ELEMENTS, ...TAX_ELEMENTS,
};

export const CLAIM_PRECONDITIONS: Record<string, ClaimPrecondition[]> = {
  ...CONSTITUTIONAL_PRECONDITIONS, ...BIVENS_PRECONDITIONS, ...ADMINISTRATIVE_PRECONDITIONS,
  ...EMPLOYMENT_PRECONDITIONS, ...TORT_GOVT_PRECONDITIONS, ...FINANCIAL_CONSUMER_PRECONDITIONS,
  ...COMMERCIAL_PRECONDITIONS, ...ERISA_PRECONDITIONS, ...TAX_PRECONDITIONS,
};

export function getElements(claimKey: string): ClaimElement[] | undefined {
  return CLAIM_ELEMENTS[claimKey];
}

export function getPreconditions(claimKey: string): ClaimPrecondition[] {
  return CLAIM_PRECONDITIONS[claimKey] || [];
}

export function getElementCount(claimKey: string): number {
  const elements = CLAIM_ELEMENTS[claimKey];
  return elements ? elements.length : 0;
}

export function hasElements(claimKey: string): boolean {
  return claimKey in CLAIM_ELEMENTS;
}

export function getClaimsWithElements(): string[] {
  return Object.keys(CLAIM_ELEMENTS);
}

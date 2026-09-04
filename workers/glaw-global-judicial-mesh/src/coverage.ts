import type { CourtJurisdictionCoverage } from './types';

const c = (id: string, name: string, country: string, sourceScope: CourtJurisdictionCoverage['sourceScope'], courtLevel?: string): CourtJurisdictionCoverage => ({ id, name, country, sourceScope, courtLevel });

export const COVERAGE = {
  courtlistener: [c('US-FEDERAL', 'United States federal courts', 'US', 'repository'), c('US-STATE', 'United States state courts', 'US', 'repository')],
  juriscraper: [c('US-FEDERAL', 'United States federal courts', 'US', 'aggregator'), c('US-SCOTUS', 'U.S. Supreme Court', 'US', 'aggregator', 'apex'), c('US-CA2', 'U.S. Court of Appeals for the Second Circuit', 'US', 'aggregator', 'appellate'), c('US-SDNY', 'U.S. District Court for the Southern District of New York', 'US', 'aggregator', 'trial'), c('US-STATE-SUPREME', 'U.S. state courts of last resort', 'US', 'aggregator', 'apex'), c('US-STATE-APPELLATE', 'U.S. state appellate courts', 'US', 'aggregator', 'appellate')],
  worldlii: [c('GLOBAL', 'Global legal-information institute discovery', 'GLOBAL', 'discovery')],
  commonlii: [c('COMMONWEALTH', 'Commonwealth jurisdictions', 'COMMONWEALTH', 'aggregator')],
  asianlii: [c('ASIA', 'Asian jurisdictions', 'ASIA', 'aggregator')],
  paclii: [c('PACIFIC', 'Pacific Island jurisdictions', 'PACIFIC', 'aggregator')],
  hklii: [c('HK', 'Hong Kong', 'HK', 'repository'), c('HK-CFA', 'Hong Kong Court of Final Appeal', 'HK', 'repository', 'apex'), c('HK-HC', 'Hong Kong High Court', 'HK', 'repository', 'trial'), c('HK-DC', 'Hong Kong District Court', 'HK', 'repository', 'trial')],
  kenyaLaw: [c('KE', 'Kenya', 'KE', 'official'), c('KE-SC', 'Supreme Court of Kenya', 'KE', 'official', 'apex'), c('KE-CA', 'Court of Appeal of Kenya', 'KE', 'official', 'appellate'), c('KE-HC', 'High Court of Kenya', 'KE', 'official', 'trial'), c('KE-ELC', 'Environment and Land Court of Kenya', 'KE', 'official', 'trial'), c('KE-ELRC', 'Employment and Labour Relations Court of Kenya', 'KE', 'official', 'trial')]
} as const;

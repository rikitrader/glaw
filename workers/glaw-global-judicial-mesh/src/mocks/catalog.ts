import type { RawProviderRecord } from '../types';

const mock = (provider: string, court: string, citation: string, endpoint: string): RawProviderRecord => ({ id: `mock-${provider}-${citation}`, caseName: `Synthetic ${provider} authority`, court, date: '2025-01-15', docketNumber: `MOCK-${provider.toUpperCase()}-001`, citation, sourceUrl: `mock://${provider}/${citation.replace(/[^A-Za-z0-9]+/g, '-')}`, snippet: `Synthetic fixture for ${provider}; not a real case and not legal authority.`, fullText: `Synthetic fixture for local integration testing only. Provider: ${provider}. Court coverage: ${court}. Citation fixture: ${citation}. This document must never be presented as law.`, metadata: { mock: true, dataset: 'glaw-local-judicial-fixtures-v1', endpoint } });

export const MOCK_RECORDS: Record<string, RawProviderRecord> = {
  courtlistener: mock('courtlistener', 'Synthetic U.S. federal court', 'MOCK-CL-001', 'https://www.courtlistener.com/api/rest/v4'),
  recap: mock('recap', 'Synthetic U.S. federal docket', 'MOCK-RECAP-001', 'https://www.courtlistener.com/api/rest/v4'),
  juriscraper: mock('juriscraper', 'Synthetic U.S. Court of Appeals for the Second Circuit', 'MOCK-JS-001', 'https://github.com/freelawproject/juriscraper'),
  worldlii: mock('worldlii', 'Synthetic global discovery record', 'MOCK-WORLDLII-001', 'https://www.worldlii.org'),
  commonlii: mock('commonlii', 'Synthetic Commonwealth court', 'MOCK-COMMONLII-001', 'https://www.commonlii.org'),
  asianlii: mock('asianlii', 'Synthetic Asian court', 'MOCK-ASIANLII-001', 'https://www.asianlii.org'),
  paclii: mock('paclii', 'Synthetic Pacific court', 'MOCK-PACLII-001', 'https://www.paclii.org'),
  hklii: mock('hklii', 'Synthetic Hong Kong Court of Final Appeal', 'MOCK-HKLII-001', 'https://www.hklii.hk'),
  kenyalaw: mock('kenyalaw', 'Synthetic Supreme Court of Kenya', 'MOCK-KENYALAW-001', 'https://new.kenyalaw.org'),
  canlii: mock('canlii', 'Synthetic Canadian appellate court', 'MOCK-CANLII-001', 'https://www.canlii.org'),
  eurlex: mock('eurlex', 'Synthetic European Union legal record', 'MOCK-EURLEX-001', 'https://eur-lex.europa.eu'),
  curia: mock('curia', 'Synthetic Court of Justice of the European Union', 'MOCK-CURIA-001', 'https://curia.europa.eu'),
  hudoc: mock('hudoc', 'Synthetic European Court of Human Rights record', 'MOCK-HUDOC-001', 'https://hudoc.echr.coe.int'),
  icj: mock('icj', 'Synthetic International Court of Justice record', 'MOCK-ICJ-001', 'https://www.icj-cij.org'),
  icc: mock('icc', 'Synthetic International Criminal Court record', 'MOCK-ICC-001', 'https://www.icc-cpi.int'),
  icsid: mock('icsid', 'Synthetic ICSID arbitration record', 'MOCK-ICSID-001', 'https://icsid.worldbank.org'),
  pca: mock('pca', 'Synthetic Permanent Court of Arbitration record', 'MOCK-PCA-001', 'https://pca-cpa.org'),
  itlos: mock('itlos', 'Synthetic International Tribunal for the Law of the Sea record', 'MOCK-ITLOS-001', 'https://www.itlos.org'),
  bailii: mock('bailii', 'Synthetic United Kingdom court record', 'MOCK-BAILII-001', 'https://www.bailii.org'),
  austlii: mock('austlii', 'Synthetic Australian court record', 'MOCK-AUSTLII-001', 'https://www.austlii.edu.au'),
  nzlii: mock('nzlii', 'Synthetic New Zealand court record', 'MOCK-NZLII-001', 'https://www.nzlii.org'),
  saflii: mock('saflii', 'Synthetic Southern African court record', 'MOCK-SAFLII-001', 'https://www.saflii.org')
};

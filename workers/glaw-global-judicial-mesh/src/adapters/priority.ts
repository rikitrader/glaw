import { GenericLegalSourceAdapter } from './template';
import { COVERAGE } from '../coverage';

export class JuriscraperAdapter extends GenericLegalSourceAdapter { constructor() { super('juriscraper', ['US'], 'https://github.com/freelawproject/juriscraper', [...COVERAGE.juriscraper]); } }
export class WorldLIIAdapter extends GenericLegalSourceAdapter { constructor() { super('worldlii', ['GLOBAL'], 'https://www.worldlii.org', [...COVERAGE.worldlii]); } }
export class CommonLIIAdapter extends GenericLegalSourceAdapter { constructor() { super('commonlii', ['COMMONWEALTH'], 'https://www.commonlii.org', [...COVERAGE.commonlii]); } }
export class AsianLIIAdapter extends GenericLegalSourceAdapter { constructor() { super('asianlii', ['ASIA'], 'https://www.asianlii.org', [...COVERAGE.asianlii]); } }
export class PacLIIAdapter extends GenericLegalSourceAdapter { constructor() { super('paclii', ['PACIFIC'], 'https://www.paclii.org', [...COVERAGE.paclii]); } }
export class HKLIIAdapter extends GenericLegalSourceAdapter { constructor() { super('hklii', ['HK'], 'https://www.hklii.hk', [...COVERAGE.hklii]); } }
export class KenyaLawAdapter extends GenericLegalSourceAdapter { constructor() { super('kenyalaw', ['KE'], 'https://new.kenyalaw.org', [...COVERAGE.kenyaLaw]); } }

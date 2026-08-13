import { priceAgent, usdToAtomic } from './pricing.mjs';

export const SERVICE_UNITS = ['fixed', 'hour', 'page', 'document', 'filing', 'model', 'review', 'month'];

export const GLAW_SERVICES = [
  {
    id: 'entity-formation',
    name: 'Entity Formation Package',
    category: 'corporate',
    description: 'Formation strategy, entity documents, founder actions, cap table setup, and filing checklist.',
    defaultAgentIds: ['glaw-entity-architect', 'glaw-corporate-counsel', 'glaw-83b-election'],
    unit: 'fixed',
    baseUsd: 2500,
    minimumUsd: 1800,
    riskTier: 'standard',
  },
  {
    id: 'tax-strategy-memo',
    name: 'Tax Strategy Memo',
    category: 'tax',
    description: 'Research-backed planning memo with structure alternatives, authorities, risks, and implementation steps.',
    defaultAgentIds: ['glaw-tax-strategy', 'glaw-legal-research', 'glaw-adversarial'],
    unit: 'document',
    baseUsd: 3200,
    minimumUsd: 2200,
    riskTier: 'high',
  },
  {
    id: 'irs-controversy',
    name: 'IRS Controversy Package',
    category: 'tax',
    description: 'Audit defense, collections posture, Tax Court readiness, workpaper index, and response draft.',
    defaultAgentIds: ['glaw-irs-audit', 'glaw-back-taxes', 'glaw-tax-court', 'glaw-audit-prep'],
    unit: 'filing',
    baseUsd: 5500,
    minimumUsd: 3500,
    riskTier: 'critical',
  },
  {
    id: 'contract-drafting',
    name: 'Commercial Contract Draft',
    category: 'contracts',
    description: 'Draft or rewrite a commercial agreement with redline-ready risk notes and negotiation points.',
    defaultAgentIds: ['glaw-commercial-contracts', 'glaw-contract-review', 'glaw-legal-writing'],
    unit: 'document',
    baseUsd: 1800,
    minimumUsd: 900,
    riskTier: 'standard',
  },
  {
    id: 'sec-tokenization-review',
    name: 'SEC Tokenization Review',
    category: 'regulatory',
    description: 'Tokenized securities offering analysis, exemption path, transfer controls, and launch checklist.',
    defaultAgentIds: ['glaw-tokenization-compliance', 'glaw-sec-disclosure', 'glaw-sec-enforcement'],
    unit: 'review',
    baseUsd: 7500,
    minimumUsd: 5000,
    riskTier: 'critical',
  },
  {
    id: 'litigation-motion',
    name: 'Litigation Motion Package',
    category: 'litigation',
    description: 'Motion strategy, authorities, draft brief, evidence cites, and adversarial challenge.',
    defaultAgentIds: ['glaw-motion-drafting', 'glaw-case-law-research', 'glaw-adversarial'],
    unit: 'filing',
    baseUsd: 4800,
    minimumUsd: 2800,
    riskTier: 'high',
  },
  {
    id: 'forensic-reconstruction',
    name: 'Forensic Financial Reconstruction',
    category: 'forensics',
    description: 'Source-ledger reconstruction, anomaly scan, evidence timeline, and defensible findings memo.',
    defaultAgentIds: ['glaw-forensic-reconstruction', 'glaw-financial-forensics', 'glaw-evidence-timeline'],
    unit: 'model',
    baseUsd: 6500,
    minimumUsd: 4000,
    riskTier: 'critical',
  },
  {
    id: 'audit-readiness',
    name: 'Audit Readiness Binder',
    category: 'accounting',
    description: 'PBC list, tied workpapers, control notes, reconciliations, and audit support package.',
    defaultAgentIds: ['glaw-audit-prep', 'glaw-audit', 'glaw-controller'],
    unit: 'month',
    baseUsd: 4200,
    minimumUsd: 2500,
    riskTier: 'high',
  },
  {
    id: 'valuation-409a',
    name: '409A Valuation Workup',
    category: 'valuation',
    description: '409A/IP valuation package with inputs, model, valuation memo, and adversarial review.',
    defaultAgentIds: ['glaw-valuation-409a', 'glaw-valuation-409a-architect', 'glaw-valuation-adversary'],
    unit: 'model',
    baseUsd: 6000,
    minimumUsd: 3500,
    riskTier: 'critical',
  },
  {
    id: 'fund-formation',
    name: 'Fund Formation Package',
    category: 'funds',
    description: 'Fund structure, adviser/regulatory analysis, GP/LP economics, offering docs, and launch checklist.',
    defaultAgentIds: ['glaw-pe-vc-counsel', 'glaw-fund-regulatory-council', 'glaw-structure'],
    unit: 'fixed',
    baseUsd: 12000,
    minimumUsd: 7500,
    riskTier: 'critical',
  },
  {
    id: 'privacy-compliance',
    name: 'Privacy Compliance Review',
    category: 'regulatory',
    description: 'Privacy/data protection review, control gap list, policy draft, and remediation roadmap.',
    defaultAgentIds: ['glaw-privacy-data', 'glaw-compliance', 'glaw-contract-review'],
    unit: 'review',
    baseUsd: 3000,
    minimumUsd: 1800,
    riskTier: 'high',
  },
  {
    id: 'general-counsel-retainer',
    name: 'AI General Counsel Retainer',
    category: 'retainer',
    description: 'Monthly access bundle for triage, document review, strategy memos, and chief counsel gates.',
    defaultAgentIds: ['glaw-chief-counsel', 'glaw-intake', 'glaw-legal-research', 'glaw-commercial-contracts'],
    unit: 'month',
    baseUsd: 9000,
    minimumUsd: 6000,
    riskTier: 'high',
  },
];

const RISK_MULTIPLIER = {
  low: 0.85,
  standard: 1,
  high: 1.35,
  critical: 1.75,
};

const SERVICE_UNIT_MULTIPLIER = {
  fixed: 1,
  hour: 0.12,
  page: 0.035,
  document: 1,
  filing: 1.2,
  model: 1.35,
  review: 0.8,
  month: 1,
};

const COMPLEXITY_MULTIPLIER = {
  standard: 1,
  expedited: 1.3,
  adversarial: 1.6,
  emergency: 2.1,
};

function serviceAgentRows(service, agentById) {
  return service.defaultAgentIds
    .map((id) => agentById.get(id))
    .filter(Boolean)
    .map(priceAgent);
}

export function buildServiceMatrix(agents) {
  const agentById = new Map(agents.map((agent) => [agent.id, agent]));
  const rows = GLAW_SERVICES.map((service) => {
    const agentRows = serviceAgentRows(service, agentById);
    const benchMinimumUsd = agentRows.reduce((sum, row) => sum + row.minimumUsd, 0);
    const riskMultiplier = RISK_MULTIPLIER[service.riskTier] ?? 1;
    const listUsd = Math.max(service.minimumUsd, Math.round(service.baseUsd * riskMultiplier));
    return {
      ...service,
      currency: 'USDC',
      riskMultiplier,
      listUsd,
      atomicAmount: usdToAtomic(listUsd),
      availableAgents: agentRows.map((row) => row.agentId),
      missingAgents: service.defaultAgentIds.filter((id) => !agentById.has(id)),
      benchMinimumUsd,
      unitRates: Object.fromEntries(
        SERVICE_UNITS.map((unit) => [unit, Math.max(1, Math.round(listUsd * SERVICE_UNIT_MULTIPLIER[unit]))])
      ),
    };
  });
  const categories = {};
  for (const row of rows) {
    categories[row.category] ??= { count: 0, listUsd: 0, averageListUsd: 0 };
    categories[row.category].count += 1;
    categories[row.category].listUsd += row.listUsd;
  }
  for (const category of Object.values(categories)) {
    category.averageListUsd = Math.round(category.listUsd / category.count);
  }
  return { generatedAt: new Date().toISOString(), currency: 'USDC', rows, categories };
}

export function findService(serviceId) {
  return GLAW_SERVICES.find((service) => service.id === serviceId) || null;
}

export function quoteService(service, agents, opts = {}) {
  if (!service) {
    const err = new Error('unknown_service');
    err.status = 404;
    throw err;
  }
  const matrixRow = buildServiceMatrix(agents).rows.find((row) => row.id === service.id);
  const unit = SERVICE_UNITS.includes(opts.unit) ? opts.unit : service.unit;
  const quantity = Math.max(1, Math.min(1000, Number(opts.quantity ?? 1)));
  const complexity = COMPLEXITY_MULTIPLIER[opts.complexity] ? opts.complexity : 'standard';
  const subtotal = matrixRow.unitRates[unit] * quantity;
  const totalUsd = Math.max(service.minimumUsd, Math.round(subtotal * COMPLEXITY_MULTIPLIER[complexity]));
  return {
    quoteId: `quote_${crypto.randomUUID()}`,
    service: { id: service.id, name: service.name, category: service.category },
    agent: {
      id: matrixRow.availableAgents[0] || service.defaultAgentIds[0],
      name: matrixRow.availableAgents[0] || service.defaultAgentIds[0],
      domain: service.category,
    },
    agents: matrixRow.availableAgents,
    missingAgents: matrixRow.missingAgents,
    unit,
    quantity,
    complexity,
    currency: 'USDC',
    subtotalUsd: subtotal,
    totalUsd,
    atomicAmount: usdToAtomic(totalUsd),
    matrix: matrixRow,
  };
}

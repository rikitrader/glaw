export const UNIT_TYPES = ['task', 'hour', 'page', 'document', 'filing', 'model', 'review'];

const DOMAIN_BASE_USD = {
  tax: 450,
  litigation: 525,
  regulatory: 575,
  finance: 500,
  accounting: 325,
  investigations: 475,
  platform: 300,
  documents: 225,
  general: 175,
};

const UNIT_MULTIPLIER = {
  task: 1,
  hour: 0.55,
  page: 0.08,
  document: 1.25,
  filing: 1.75,
  model: 2.5,
  review: 0.75,
};

const COMPLEXITY_MULTIPLIER = {
  standard: 1,
  expedited: 1.35,
  adversarial: 1.75,
  emergency: 2.25,
};

function riskScore(agent) {
  const s = `${agent.id} ${agent.name} ${agent.description}`.toLowerCase();
  let score = 1;
  if (/audit|assurance|court|trial|motion|appeal|filing|irs|sec|ofac|fincen|aml|regulatory/.test(s)) score += 0.35;
  if (/forensic|fraud|investigat|whistleblower|enforcement|sanction|valuation|409a/.test(s)) score += 0.3;
  if (/draft|contract|estate|employment|privacy|securities|tax/.test(s)) score += 0.15;
  return Math.min(2.25, Number(score.toFixed(2)));
}

export function priceAgent(agent) {
  const baseUsd = DOMAIN_BASE_USD[agent.domain] ?? DOMAIN_BASE_USD.general;
  const riskMultiplier = riskScore(agent);
  const minimumUsd = Math.round(baseUsd * riskMultiplier);
  return {
    agentId: agent.id,
    name: agent.name,
    domain: agent.domain,
    baseUsd,
    riskMultiplier,
    minimumUsd,
    unitRates: Object.fromEntries(
      UNIT_TYPES.map((unit) => [unit, Math.max(1, Math.round(minimumUsd * UNIT_MULTIPLIER[unit]))])
    ),
  };
}

export function buildMatrix(agents) {
  const rows = agents.map(priceAgent);
  const domains = {};
  for (const row of rows) {
    domains[row.domain] ??= { count: 0, minimumUsd: 0, averageMinimumUsd: 0 };
    domains[row.domain].count += 1;
    domains[row.domain].minimumUsd += row.minimumUsd;
  }
  for (const value of Object.values(domains)) {
    value.averageMinimumUsd = Math.round(value.minimumUsd / value.count);
  }
  return { generatedAt: new Date().toISOString(), currency: 'USDC', rows, domains };
}

export function quoteWork(agent, opts = {}) {
  if (!agent) {
    const err = new Error('unknown_agent');
    err.status = 404;
    throw err;
  }
  const unit = UNIT_TYPES.includes(opts.unit) ? opts.unit : 'task';
  const quantity = Math.max(1, Math.min(10000, Number(opts.quantity ?? 1)));
  const complexity = COMPLEXITY_MULTIPLIER[opts.complexity] ? opts.complexity : 'standard';
  const priced = priceAgent(agent);
  const subtotal = priced.unitRates[unit] * quantity;
  const totalUsd = Math.round(subtotal * COMPLEXITY_MULTIPLIER[complexity]);
  return {
    quoteId: `quote_${crypto.randomUUID()}`,
    agent: { id: agent.id, name: agent.name, domain: agent.domain },
    unit,
    quantity,
    complexity,
    currency: 'USDC',
    subtotalUsd: subtotal,
    totalUsd,
    atomicAmount: usdToAtomic(totalUsd),
    matrix: priced,
  };
}

export function usdToAtomic(usd) {
  return String(Math.round(Number(usd) * 1_000_000));
}

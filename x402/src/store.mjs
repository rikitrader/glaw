const charges = new Map();

export function createCharge({ quote, matterId, memo, baseUrl }) {
  const id = `glaw_${crypto.randomUUID()}`;
  const now = new Date().toISOString();
  const charge = {
    id,
    status: 'created',
    quote,
    matterId: matterId || null,
    memo: memo || null,
    createdAt: now,
    updatedAt: now,
    payment: null,
    payUrl: `${baseUrl.replace(/\/+$/, '')}/api/pay/${id}`,
  };
  charges.set(id, charge);
  return charge;
}

export function getCharge(id) {
  return charges.get(id) || null;
}

export function updateCharge(id, patch) {
  const existing = getCharge(id);
  if (!existing) return null;
  const next = { ...existing, ...patch, updatedAt: new Date().toISOString() };
  charges.set(id, next);
  return next;
}

export function listCharges() {
  return [...charges.values()].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

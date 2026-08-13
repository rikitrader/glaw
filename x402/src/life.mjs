import { randomId } from './crypto.mjs';

export function nextLifeState({ alive, liveNeighbors, paidThisWindow }) {
  if (paidThisWindow) return 'alive';
  if (alive && liveNeighbors < 2) return 'dormant';
  if (alive && (liveNeighbors === 2 || liveNeighbors === 3)) return 'alive';
  if (alive && liveNeighbors > 3) return 'dormant';
  if (!alive && liveNeighbors === 3) return 'alive';
  return 'dormant';
}

export function revenueShares(agentIds, amountUsd) {
  const unique = [...new Set(agentIds.filter(Boolean))];
  if (!unique.length) return [];
  if (unique.length === 1) return [{ agentId: unique[0], weight: 1, amountUsd }];
  const primary = unique[0];
  const supportWeight = 0.5 / (unique.length - 1);
  return unique.map((agentId) => {
    const weight = agentId === primary ? 0.5 : supportWeight;
    return { agentId, weight, amountUsd: Math.round(amountUsd * weight) };
  });
}

export async function ensureLifeRows(env, agentIds) {
  const now = Date.now();
  for (const agentId of new Set(agentIds.filter(Boolean))) {
    await env.DB.prepare(
      `INSERT OR IGNORE INTO agent_life (agent_id, generation, state, energy, paid_count, live_neighbor_count, updated_ms)
       VALUES (?, 0, 'dormant', 0, 0, 0, ?)`
    ).bind(agentId, now).run();
  }
}

export async function grantPaidLife(env, chargeId, agentIds, amountUsd) {
  const shares = revenueShares(agentIds, amountUsd);
  const now = Date.now();
  await ensureLifeRows(env, shares.map((s) => s.agentId));
  for (const share of shares) {
    await env.DB.prepare(
      `INSERT INTO agent_revenue_shares (id, charge_id, agent_id, weight, amount_usd, created_ms)
       VALUES (?, ?, ?, ?, ?, ?)`
    ).bind(randomId('shr'), chargeId, share.agentId, share.weight, share.amountUsd, now).run();
    await env.DB.prepare(
      `UPDATE agent_life
          SET state = 'alive',
              energy = energy + ?,
              paid_count = paid_count + 1,
              last_paid_ms = ?,
              updated_ms = ?
        WHERE agent_id = ?`
    ).bind(share.amountUsd, now, now, share.agentId).run();
    await env.DB.prepare(
      `INSERT INTO agent_life_events (id, agent_id, generation, previous_state, next_state, reason, energy_delta, created_ms)
       VALUES (?, ?, COALESCE((SELECT generation FROM agent_life WHERE agent_id = ?), 0), NULL, 'alive', 'paid_work', ?, ?)`
    ).bind(randomId('life'), share.agentId, share.agentId, share.amountUsd, now).run();
  }
  return shares;
}

export async function tickLife(env) {
  const now = Date.now();
  const rows = (await env.DB.prepare(`SELECT * FROM agent_life`).all()).results || [];
  const live = new Set(rows.filter((r) => r.state === 'alive').map((r) => r.agent_id));
  const maxGeneration = rows.reduce((n, r) => Math.max(n, Number(r.generation || 0)), 0);
  const nextGeneration = maxGeneration + 1;
  for (const row of rows) {
    const neighbors = (await env.DB.prepare(`SELECT b FROM agent_edges WHERE a = ?`).bind(row.agent_id).all()).results || [];
    const liveNeighbors = neighbors.filter((n) => live.has(n.b)).length;
    const paidThisWindow = Number(row.last_paid_ms || 0) >= now - 24 * 60 * 60 * 1000;
    const next = nextLifeState({ alive: row.state === 'alive', liveNeighbors, paidThisWindow });
    const nextEnergy = Math.max(0, Number(row.energy || 0) * 0.9);
    await env.DB.prepare(
      `UPDATE agent_life
          SET generation = ?, state = ?, energy = ?, live_neighbor_count = ?, updated_ms = ?
        WHERE agent_id = ?`
    ).bind(nextGeneration, next, nextEnergy, liveNeighbors, now, row.agent_id).run();
    if (next !== row.state) {
      await env.DB.prepare(
        `INSERT INTO agent_life_events (id, agent_id, generation, previous_state, next_state, reason, energy_delta, created_ms)
         VALUES (?, ?, ?, ?, ?, 'conway_tick', 0, ?)`
      ).bind(randomId('life'), row.agent_id, nextGeneration, row.state, next, now).run();
    }
  }
  return { generation: nextGeneration, processed: rows.length };
}

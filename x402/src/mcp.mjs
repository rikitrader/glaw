import { createCharge } from './store.mjs';
import { buildMatrix, quoteWork } from './pricing.mjs';
import { buildServiceMatrix, findService, GLAW_SERVICES, quoteService } from './services.mjs';

const SERVER_INFO = { name: 'glaw-x402', title: 'GLAW X402 Agent Billing', version: '0.1.0' };
const PROTOCOLS = ['2026-07-28', '2025-11-25', '2025-06-18'];

const ok = (id, result) => ({ jsonrpc: '2.0', id, result });
const err = (id, code, message, data) => ({ jsonrpc: '2.0', id, error: { code, message, ...(data === undefined ? {} : { data }) } });

export const MCP_TOOLS = [
  {
    name: 'glaw_list_agents',
    title: 'List GLAW Agents',
    description: 'List every local SKILL.md as a billable GLAW agent.',
    inputSchema: { type: 'object', properties: { domain: { type: 'string' } } },
  },
  {
    name: 'glaw_charge_matrix',
    title: 'GLAW Charge Matrix',
    description: 'Return the current agent pricing matrix.',
    inputSchema: { type: 'object', properties: { mode: { type: 'string', enum: ['agents', 'services', 'combined'] } } },
  },
  {
    name: 'glaw_list_services',
    title: 'List GLAW Services',
    description: 'List curated GLAW service packages and default agents.',
    inputSchema: { type: 'object', properties: { category: { type: 'string' } } },
  },
  {
    name: 'glaw_service_matrix',
    title: 'GLAW Service Matrix',
    description: 'Return the curated service pricing matrix.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'glaw_quote_work',
    title: 'Quote GLAW Work',
    description: 'Create a deterministic quote for one GLAW agent or curated service.',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string' },
        serviceId: { type: 'string' },
        unit: { type: 'string', enum: ['task', 'fixed', 'hour', 'page', 'document', 'filing', 'model', 'review', 'month'] },
        quantity: { type: 'number' },
        complexity: { type: 'string', enum: ['standard', 'expedited', 'adversarial', 'emergency'] },
      },
    },
  },
  {
    name: 'glaw_create_charge',
    title: 'Create GLAW X402 Charge',
    description: 'Create a pending charge and return its X402 payment URL.',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string' },
        serviceId: { type: 'string' },
        unit: { type: 'string' },
        quantity: { type: 'number' },
        complexity: { type: 'string' },
        matterId: { type: 'string' },
        memo: { type: 'string' },
      },
    },
  },
];

export async function handleMcpMessage({ msg, agents, baseUrl }) {
  const id = msg?.id ?? null;
  if (!msg || msg.jsonrpc !== '2.0' || typeof msg.method !== 'string') return err(id, -32600, 'Invalid Request');
  if (msg.id === undefined) return null;

  switch (msg.method) {
    case 'initialize': {
      const reqVersion = msg.params?.protocolVersion;
      return ok(id, {
        protocolVersion: PROTOCOLS.includes(reqVersion) ? reqVersion : PROTOCOLS[0],
        capabilities: { tools: { listChanged: false }, resources: {} },
        serverInfo: SERVER_INFO,
        instructions: 'Use glaw_quote_work, then glaw_create_charge. Pay the returned URL with X402 before relying on the work authorization.',
      });
    }
    case 'ping':
      return ok(id, {});
    case 'tools/list':
      return ok(id, { tools: MCP_TOOLS });
    case 'tools/call': {
      const name = msg.params?.name;
      const args = msg.params?.arguments || {};
      const byId = new Map(agents.map((agent) => [agent.id, agent]));
      try {
        let data;
        if (name === 'glaw_list_agents') {
          data = { agents: args.domain ? agents.filter((a) => a.domain === args.domain) : agents };
        } else if (name === 'glaw_charge_matrix') {
          if (args.mode === 'services') data = buildServiceMatrix(agents);
          else if (args.mode === 'combined') data = { agents: buildMatrix(agents), services: buildServiceMatrix(agents) };
          else data = buildMatrix(agents);
        } else if (name === 'glaw_list_services') {
          data = { services: args.category ? GLAW_SERVICES.filter((s) => s.category === args.category) : GLAW_SERVICES };
        } else if (name === 'glaw_service_matrix') {
          data = buildServiceMatrix(agents);
        } else if (name === 'glaw_quote_work') {
          data = args.serviceId ? quoteService(findService(args.serviceId), agents, args) : quoteWork(byId.get(args.agentId), args);
        } else if (name === 'glaw_create_charge') {
          const quote = args.serviceId ? quoteService(findService(args.serviceId), agents, args) : quoteWork(byId.get(args.agentId), args);
          data = createCharge({ quote, matterId: args.matterId, memo: args.memo, baseUrl });
        } else {
          return err(id, -32601, `Method not found: ${name}`);
        }
        return ok(id, {
          content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
          structuredContent: data,
          isError: false,
        });
      } catch (e) {
        return ok(id, { content: [{ type: 'text', text: e.message || String(e) }], isError: true });
      }
    }
    case 'resources/list':
      return ok(id, { resources: [] });
    case 'prompts/list':
      return ok(id, { prompts: [] });
    default:
      return err(id, -32601, `Method not found: ${msg.method}`);
  }
}

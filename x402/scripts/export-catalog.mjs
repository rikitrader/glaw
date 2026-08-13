import { loadAgents } from '../src/catalog.mjs';

const agents = await loadAgents();
console.log(JSON.stringify({ agents }, null, 2));

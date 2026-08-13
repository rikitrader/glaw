import process from 'node:process';
import { loadAgents } from '../src/catalog.mjs';

const baseUrl = process.env.GLAW_X402_URL || process.argv[2] || 'http://localhost:8787';
const token = process.env.GLAW_ADMIN_BOOTSTRAP_TOKEN || process.env.GLAW_ADMIN_TOKEN;

if (!token) {
  console.error('Set GLAW_ADMIN_BOOTSTRAP_TOKEN or GLAW_ADMIN_TOKEN before importing the catalog.');
  process.exit(1);
}

const agents = await loadAgents();
const res = await fetch(`${baseUrl.replace(/\/+$/, '')}/api/admin/catalog/import`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Admin-Token': token,
  },
  body: JSON.stringify({ agents }),
});
const text = await res.text();
console.log(text);
if (!res.ok) process.exit(1);

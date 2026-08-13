import fs from 'node:fs/promises';
import path from 'node:path';

export const DEFAULT_SKILL_ROOTS = [
  '/Users/ricardoprieto/.codex/skills',
  '/Users/ricardoprieto/.agents/skills',
  '/Users/ricardoprieto/.codex/skills/.system',
];

const FRONTMATTER_RE = /^---\n([\s\S]*?)\n---\n?/;

function parseFrontmatter(text) {
  const match = text.match(FRONTMATTER_RE);
  const data = {};
  if (!match) return data;
  for (const line of match[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    const raw = line.slice(idx + 1).trim();
    data[key] = raw.replace(/^['"]|['"]$/g, '');
  }
  return data;
}

async function walk(dir, out = [], seenDirs = new Set()) {
  let realDir = dir;
  try {
    realDir = await fs.realpath(dir);
  } catch {
    return out;
  }
  if (seenDirs.has(realDir)) return out;
  seenDirs.add(realDir);
  let entries = [];
  try {
    entries = await fs.readdir(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walk(full, out, seenDirs);
    } else if (entry.isSymbolicLink()) {
      let st = null;
      try {
        st = await fs.stat(full);
      } catch {
        st = null;
      }
      if (st?.isDirectory()) await walk(full, out, seenDirs);
      if (st?.isFile() && entry.name === 'SKILL.md') out.push(full);
    } else if (entry.isFile() && entry.name === 'SKILL.md') {
      out.push(full);
    }
  }
  return out;
}

function agentIdFromPath(file) {
  return path.basename(path.dirname(file)).toLowerCase().replace(/[^a-z0-9:_-]+/g, '-');
}

export function inferDomain(agent) {
  const s = `${agent.id} ${agent.name} ${agent.description}`.toLowerCase();
  const has = (pattern) => pattern.test(s);
  if (has(/\b(sec|securities|regulatory|compliance|fincen|ofac|aml)\b/)) return 'regulatory';
  if (has(/\b(litigation|court|motion|trial|appeal|appellate|docket)\b/)) return 'litigation';
  if (has(/\b(tax|taxes|irs|83b|83\(b\)|1040|1120|1065|asc 740|provision)\b/)) return 'tax';
  if (has(/\b(finance|financial|valuation|dcf|lbo|cfo|fund|treasury|409a)\b/)) return 'finance';
  if (has(/\b(accounting|ledger|audit|assurance|bookkeeping|controller|payroll|revenue|inventory|receivable|payable)\b/)) return 'accounting';
  if (has(/\b(investigation|investigations|investigator|forensic|forensics|intel|bureau|fraud|counterfraud)\b/)) return 'investigations';
  if (has(/\b(cloudflare|worker|workers|durable objects|wrangler|turnstile|mcp|sdk|api)\b/)) return 'platform';
  if (has(/\b(docx|pdf|pitch|copy|document|contract|draft|forms?)\b/)) return 'documents';
  return 'general';
}

export async function loadAgents(skillRoots = DEFAULT_SKILL_ROOTS) {
  const files = (await Promise.all(skillRoots.map((root) => walk(root)))).flat();
  const seen = new Map();
  for (const file of files) {
    const text = await fs.readFile(file, 'utf8');
    const fm = parseFrontmatter(text);
    const id = fm.name || agentIdFromPath(file);
    const description = fm.description || text.split('\n').find((line) => line.trim() && !line.startsWith('---')) || '';
    const prior = seen.get(id);
    const agent = {
      id,
      name: fm.name || id,
      description: description.trim(),
      path: file,
      domain: 'general',
    };
    agent.domain = inferDomain(agent);
    if (!prior || file.includes('/.codex/skills/')) seen.set(id, agent);
  }
  return [...seen.values()].sort((a, b) => a.id.localeCompare(b.id));
}

import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const packageRoot = resolve(new URL('..', import.meta.url).pathname);
const repoRoot = resolve(packageRoot, '../..');
const errors = [];
const readJson = (relative) => JSON.parse(readFileSync(resolve(repoRoot, relative), 'utf8'));
const requirePath = (relative) => { if (!existsSync(resolve(repoRoot, relative))) errors.push(`missing path: ${relative}`); };
const registryPath = (registry, key, label) => { const value = registry?.[key]; if (typeof value !== 'string') errors.push(`${label} has no string path`); else requirePath(value); };

for (const file of ['GLAW_DEPARTMENT_REGISTRY.json', 'GLAW_AGENT_REGISTRY.json', 'GLAW_SKILL_REGISTRY.json', 'GLAW_RAG_REGISTRY.json', 'GLAW_WORKFLOW_REGISTRY.json']) requirePath(file);
const departments = readJson('GLAW_DEPARTMENT_REGISTRY.json'); const hankeDepartment = departments.departmentPacks?.find((pack) => pack.id === 'hanke-applied-economics');
if (!hankeDepartment) errors.push('GLAW department registry lacks hanke-applied-economics'); else requirePath(hankeDepartment.path);
const agents = readJson('GLAW_AGENT_REGISTRY.json'); registryPath(agents.departmentAgents, 'manifest', 'departmentAgents');
const skills = readJson('GLAW_SKILL_REGISTRY.json'); registryPath(skills.departmentSkills, 'root', 'departmentSkills');
const rag = readJson('GLAW_RAG_REGISTRY.json'); for (const collection of rag.departmentCollections ?? []) if (collection.id.startsWith('hanke-')) requirePath(collection.path);
const workflows = readJson('GLAW_WORKFLOW_REGISTRY.json'); for (const workflow of workflows.departmentWorkflows ?? []) if (workflow.path.includes('hanke-economics')) requirePath(workflow.path);
for (const file of ['departments/hanke-economics/src/control-plane.ts', 'departments/hanke-economics/department.yaml', 'departments/hanke-economics/agents/red-team/agent-manifests.yaml', 'departments/hanke-economics/agents/blue-team/agent-manifests.yaml', 'control-plane/src/pages/api/hanke-health.ts', 'control-plane/src/pages/api/hanke-runs.ts', 'control-plane/db/migrations/0002_hanke_economics.sql', 'control-plane/db/migrations/0003_hanke_review.sql']) requirePath(file);
const report = { status: errors.length ? 'FAIL' : 'PASS', checked: 5, errors };
console.log(JSON.stringify(report, null, 2));
process.exit(errors.length ? 1 : 0);

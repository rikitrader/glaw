import { readFile, readdir } from 'node:fs/promises';

const config = await readFile(new URL('../wrangler.jsonc', import.meta.url), 'utf8');
const placeholders = [...config.matchAll(/REPLACE_ME_[A-Z0-9_]+|[A-Za-z0-9-]*placeholder[A-Za-z0-9-]*|0{32}/g)].map((match) => match[0]);
if (placeholders.length > 0) {
  console.error(`Production deployment blocked. Replace placeholders in wrangler.jsonc: ${[...new Set(placeholders)].join(', ')}`);
  process.exit(1);
}
if (/GLAW_(?:API|ADMIN_API)_KEY\s*[:=]/.test(config) || /COURTLISTENER_TOKEN\s*[:=]/.test(config)) {
  console.error('Production deployment blocked. Secrets must be configured with Wrangler secret put, not in wrangler.jsonc.');
  process.exit(1);
}
if (/"MOCK_PROVIDER_MODE"\s*:\s*"true"/.test(config) || /"ENVIRONMENT"\s*:\s*"local"/.test(config)) {
  console.error('Production deployment blocked. Local synthetic provider mode cannot be deployed.');
  process.exit(1);
}
const requiredBindings = ['"binding": "DB"', '"binding": "DOCUMENTS"', '"binding": "CACHE"', '"binding": "INGESTION_QUEUE"', '"binding": "LEGAL_VECTORS"', '"name": "ROUTER_COORDINATOR"', '"name": "JUDGE_PROFILE_COORDINATOR"', '"name": "MATTER_COORDINATOR"'];
const missingBindings = requiredBindings.filter((binding) => !config.includes(binding));
if (missingBindings.length > 0) {
  console.error(`Production deployment blocked. Missing required bindings: ${missingBindings.join(', ')}`);
  process.exit(1);
}
if (!/"vars"\s*:\s*\{[\s\S]*?"ENVIRONMENT"\s*:\s*"production"[\s\S]*?"MOCK_PROVIDER_MODE"\s*:\s*"false"/.test(config)) {
  console.error('Production deployment blocked. ENVIRONMENT must be production and MOCK_PROVIDER_MODE must be false.');
  process.exit(1);
}
if (config.includes('"GLAW_ALLOWED_ORIGINS"')) {
  console.error('Production deployment blocked. CORS origins must be configured as a Wrangler secret or environment-specific deployment variable, not committed to wrangler.jsonc.');
  process.exit(1);
}
const migrationFiles = (await readdir(new URL('../migrations/', import.meta.url))).filter((file) => /^\d+_.+\.sql$/.test(file));
if (migrationFiles.length === 0) {
  console.error('Production deployment blocked. No versioned D1 migrations were found.');
  process.exit(1);
}
const migrationNumbers = migrationFiles.map((file) => Number(file.split('_', 1)[0])).sort((a, b) => a - b);
const missingMigrations = migrationNumbers.flatMap((number, index) => index === 0 ? Array.from({ length: number - 1 }, (_, offset) => offset + 1) : Array.from({ length: number - migrationNumbers[index - 1] - 1 }, (_, offset) => migrationNumbers[index - 1] + offset + 1));
if (missingMigrations.length > 0 || !migrationFiles.some((file) => file.startsWith('0026_'))) {
  console.error(`Production deployment blocked. D1 migration chain is incomplete or prediction-review scope migration 0026 is missing: ${[...new Set(missingMigrations)].join(', ') || '0026 missing'}`);
  process.exit(1);
}
console.log('Production Wrangler configuration passed placeholder and secret checks.');

import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { HAEIS_CATALOG, validateCatalog } from '../src/control-plane.ts';

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const errors = validateCatalog((path) => existsSync(resolve(packageRoot, path)));
const report = { status: errors.length ? 'FAIL' : 'PASS', catalog_entries: HAEIS_CATALOG.length, errors };
console.log(JSON.stringify(report, null, 2));
process.exit(errors.length ? 1 : 0);

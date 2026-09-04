import { readFileSync } from 'node:fs';
import { validateIntake } from '../src/intake.ts';

const file = process.argv[2];
if (!file) {
  console.error('Usage: node scripts/validate-intake.mjs intake/<file>.json');
  process.exit(2);
}

let intake;
try {
  intake = JSON.parse(readFileSync(file, 'utf8'));
} catch (error) {
  console.error(`BLOCKED: cannot read JSON intake: ${error.message}`);
  process.exit(2);
}

const errors = validateIntake(intake);
if (errors.length) {
  console.log(JSON.stringify({ status: 'BLOCKED', intake_id: intake.intake_id ?? null, errors }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: intake.status === 'BLOCKED' ? 'BLOCKED' : 'READY_FOR_RESEARCH', intake_id: intake.intake_id, country: intake.country, question: intake.question }, null, 2));

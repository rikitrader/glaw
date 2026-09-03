import { createHash } from 'node:crypto';
import { stableStringify } from '../core/json.ts';
export interface VersionPins { gymVersion: string; datasetVersion: string; taskVersion: string; evaluatorVersion: string; toolSchemaVersion: string; seed: number; buildVersion: string; }
export function reproducibilityHash(pins: VersionPins): string { return createHash('sha256').update(stableStringify(pins)).digest('hex'); }

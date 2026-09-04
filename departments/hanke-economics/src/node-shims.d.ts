declare module 'node:crypto' {
  interface Hash { update(value: Uint8Array | string): Hash; digest(encoding: 'hex'): string; }
  export function createHash(algorithm: string): Hash;
}

declare module 'node:fs' {
  export function readFileSync(path: string, options?: unknown): any;
  export function appendFileSync(path: string, data: string, encoding?: string): void;
  export function writeFileSync(path: string, data: string, encoding?: string): void;
  export function writeFileSync(path: string, data: Uint8Array): void;
  export function mkdirSync(path: string, options?: unknown): void;
  export function statSync(path: string): { size: number };
  export function existsSync(path: string): boolean;
}

declare module 'node:path' {
  export function dirname(path: string): string;
  export function join(...parts: string[]): string;
}

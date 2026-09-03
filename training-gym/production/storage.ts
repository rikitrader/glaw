import { createHash } from 'node:crypto';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';

export interface ObjectReference { key: string; sha256: string; bytes: number; contentType?: string; }
export interface ObjectStore { put(key: string, data: Uint8Array, contentType?: string): Promise<ObjectReference>; get(key: string): Promise<Uint8Array>; exists(key: string): Promise<boolean>; }
export class MemoryObjectStore implements ObjectStore {
  private readonly objects = new Map<string, Uint8Array>();
  async put(key: string, data: Uint8Array, contentType?: string): Promise<ObjectReference> { const copy = new Uint8Array(data); this.objects.set(key, copy); return ref(key, copy, contentType); }
  async get(key: string): Promise<Uint8Array> { const data = this.objects.get(key); if (!data) throw new Error(`Object not found: ${key}`); return new Uint8Array(data); }
  async exists(key: string): Promise<boolean> { return this.objects.has(key); }
}
export class LocalObjectStore implements ObjectStore {
  private readonly root: string;
  constructor(root: string) { this.root = resolve(root); }
  async put(key: string, data: Uint8Array, contentType?: string): Promise<ObjectReference> { const path = this.safePath(key); await mkdir(dirname(path), { recursive: true }); await writeFile(path, data); return ref(key, data, contentType); }
  async get(key: string): Promise<Uint8Array> { return readFile(this.safePath(key)); }
  async exists(key: string): Promise<boolean> { try { await stat(this.safePath(key)); return true; } catch { return false; } }
  private safePath(key: string): string { const path = resolve(this.root, key); if (path !== this.root && !path.startsWith(this.root + sep)) throw new Error('Object key escapes storage root'); return path; }
}
function ref(key: string, data: Uint8Array, contentType?: string): ObjectReference { return { key, bytes: data.byteLength, ...(contentType ? { contentType } : {}), sha256: createHash('sha256').update(data).digest('hex') }; }

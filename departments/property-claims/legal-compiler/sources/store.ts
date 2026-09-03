import { createHash } from 'node:crypto';
import type { SourceSnapshot } from './snapshot.ts';
import { verifySnapshot } from './snapshot.ts';

export class SourceSnapshotStore {
  private readonly snapshots = new Map<string, SourceSnapshot>();

  put(snapshot: SourceSnapshot): void {
    if (!verifySnapshot(snapshot)) throw new Error(`source snapshot hash failed: ${snapshot.snapshotId}`);
    const previous = this.snapshots.get(snapshot.snapshotId);
    if (previous && previous.sha256 !== snapshot.sha256) throw new Error(`immutable source snapshot overwrite rejected: ${snapshot.snapshotId}`);
    this.snapshots.set(snapshot.snapshotId, snapshot);
  }

  get(snapshotId: string): SourceSnapshot | undefined { return this.snapshots.get(snapshotId); }
  all(): SourceSnapshot[] { return [...this.snapshots.values()]; }
  linkAuthority(snapshotId: string, authorityId: string): void {
    const snapshot = this.snapshots.get(snapshotId);
    if (!snapshot) throw new Error(`source snapshot not found: ${snapshotId}`);
    this.snapshots.set(snapshotId, { ...snapshot, authorityId });
  }
  static contentHash(content: string): string { return createHash('sha256').update(content, 'utf8').digest('hex'); }
}

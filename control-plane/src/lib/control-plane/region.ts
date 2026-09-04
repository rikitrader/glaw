export type RegionPolicy = { homeRegion: string; allowedRegions: string[]; deploymentMode: "saas" | "single-tenant" | "private" | "on-prem" | "air-gapped"; fencingEpoch: number };
export function assertRegionAllowed(policy: RegionPolicy, requestedRegion: string): void {
  if (!policy.allowedRegions.includes(requestedRegion)) throw new Error("requested region is outside tenant residency policy");
}
export function assertFencingEpoch(policy: RegionPolicy, observedEpoch: number): void {
  if (observedEpoch !== policy.fencingEpoch) throw new Error("stale region fencing epoch");
}

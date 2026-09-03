export type SkillManifest = { id: string; version: string; contentHash: string; signature: string; permissions: string[]; dependencies: Record<string, string> };
export function validateSkillManifest(skill: SkillManifest, trustedSignatures: Set<string>): void {
  if (!/^[a-z0-9][a-z0-9._-]+$/.test(skill.id) || !/^\d+\.\d+\.\d+$/.test(skill.version)) throw new Error("invalid skill identity");
  if (!/^[a-f0-9]{64}$/.test(skill.contentHash) || !trustedSignatures.has(skill.signature)) throw new Error("untrusted skill signature or content hash");
  if (skill.permissions.some((permission) => permission === "admin" || permission === "*")) throw new Error("skill permission is too broad");
}

export type AuditSigner = {
  keyId: string;
  algorithm: "HMAC-SHA256" | "KMS-SHA256";
  sign(payload: string): Promise<string>;
};

export type KmsSignerClient = {
  signDigest(input: { keyId: string; digestHex: string; algorithm: "SHA256" }): Promise<string>;
};

export function createLocalHmacSigner(secret: string, keyId: string): AuditSigner {
  return { keyId, algorithm: "HMAC-SHA256", sign: (payload) => hmacHex(secret, payload) };
}

/** Production adapter boundary: the KMS/HSM client owns key material. */
export async function createKmsSigner(client: KmsSignerClient, keyId: string): Promise<AuditSigner> {
  return { keyId, algorithm: "KMS-SHA256", sign: async (payload) => client.signDigest({ keyId, digestHex: await sha256Hex(payload), algorithm: "SHA256" }) };
}

async function sha256Hex(value: string): Promise<string> { const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)); return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join(""); }
async function hmacHex(secret: string, value: string): Promise<string> { if (!secret) throw new Error("local audit signing secret is not configured"); const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value)); return Array.from(new Uint8Array(signature), (b) => b.toString(16).padStart(2, "0")).join(""); }

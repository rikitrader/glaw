export async function sha256hex(value) {
  const bytes = new TextEncoder().encode(String(value));
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function randomId(prefix) {
  return `${prefix}_${crypto.randomUUID()}`;
}

export function randomSecret(prefix) {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  const token = btoa(String.fromCharCode(...bytes)).replace(/[+/=]/g, '').slice(0, 32);
  return `${prefix}_${token}`;
}

export async function signWorkToken(payload, secret) {
  if (!secret) throw new Error('work_auth_secret_required');
  const body = btoa(JSON.stringify(payload));
  const sig = await sha256hex(`${body}.${secret}`);
  return `${body}.${sig}`;
}

export async function verifyWorkToken(token, secret) {
  if (!token || !secret) return null;
  const [body, sig] = String(token).split('.');
  if (!body || !sig) return null;
  const expected = await sha256hex(`${body}.${secret}`);
  if (expected !== sig) return null;
  try {
    const payload = JSON.parse(atob(body));
    if (payload.expires_ms && Number(payload.expires_ms) <= Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

export type IdentityProviderConfig = { issuer: string; clientId: string; allowedDomains: string[]; claims: { subject: string; email: string; groups: string }; provisioning: "OIDC" | "SCIM" };
export type ProvisioningEvent = { provider: string; subject: string; email?: string; groups?: string[]; action: "PROVISION" | "UPDATE" | "DEPROVISION"; occurredAt: string };

export function validateIdentityProvider(config: IdentityProviderConfig): void {
  if (!/^https:\/\//.test(config.issuer)) throw new Error("identity issuer must use HTTPS");
  if (!config.clientId || !config.claims.subject || !config.claims.email) throw new Error("identity claims are incomplete");
  if (config.provisioning === "SCIM" && !config.claims.groups) throw new Error("SCIM group claim is required");
}

export function applyProvisioningEvent(event: ProvisioningEvent): "ACTIVE" | "DEPROVISIONED" {
  if (!event.provider || !event.subject || !event.occurredAt) throw new Error("invalid provisioning event");
  return event.action === "DEPROVISION" ? "DEPROVISIONED" : "ACTIVE";
}

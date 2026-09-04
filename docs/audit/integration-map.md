# Integration Map

## Current

MCP, X402, court/research adapters, provider adapters, Google-related optional
outputs, and Cloudflare Worker surfaces are present in source or configuration.

## Not confirmed

Production-grade first-party connectors for DMS, CRM, email, Teams/Slack,
DocuSign, court e-filing, billing, and identity providers with universal
capability, webhook, idempotency, and reconciliation contracts.

## Required connector contract

```text
capabilities · auth · permissions · rate limits · read/write operations
webhooks · health · cursor · idempotency · authoritative lookup
reconciliation · incident behavior
```

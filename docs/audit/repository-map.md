# Repository Map

## Scope

Repository: `/Users/ricardoprieto/projects/glaw-oss`  
Audit mode: read-only inspection plus documentation  
Date: 2026-08-27

## Inventory snapshot

| Area | Current evidence | Status |
|---|---|---|
| Skills | 267 `SKILL.md` files in checkout | confirmed |
| CLI/tool layer | 294 files under `bin/` | confirmed |
| Test-like files | 227 files or test paths | confirmed; needs classification |
| Core runtime | Bash + Python standard library | confirmed |
| Public intake | Cloudflare Worker + static assets + KV | confirmed |
| Control plane | Astro/React/XYFlow scaffold | confirmed; build verification pending |
| Paid-agent service | Cloudflare Worker + D1 + MCP/REST | confirmed |
| Legal Governor | local source-locked workpapers and gates | confirmed |
| Semantic retrieval | no production Vectorize pipeline evidenced | confirmed absent |
| Durable execution | no production Queue/Workflow binding evidenced | confirmed absent |

## Existing architecture artifacts

Existing root-level architecture inventories, registries, design rules, and
implementation plans are preserved. They are inputs to migration, not discarded
in favor of a rewrite.

## Audit limitation

This is a repository audit. Cloud account state, deployed resources, production
traces, active matter data, external connector credentials, and runtime traffic
were not inspected.

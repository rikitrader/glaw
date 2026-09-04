# Duplication Report

## Confirmed multiplicity

- 233 `SKILL.md` files and 179 `bin/` commands create two large catalogs with different discovery mechanisms.
- There are two Cloudflare Worker products with separate runtime/configuration surfaces.
- GLAW has local CLI execution, host adapter, MCP adapter, and Extism adapter; these are intentionally layered but need one canonical graph representation.
- Matter pipeline gates and Legal Governor gates overlap in purpose but have different state stores and command surfaces.

## Possible overlaps requiring evidence

| Candidate | Finding | Recommendation |
|---|---|---|
| `glaw`, `glaw-loop`, `glaw-daemon` | orchestration/control loop responsibilities overlap | CONSOLIDATE only at graph/control-plane model level; preserve distinct safety boundaries until tested |
| matter pipeline vs Legal Governor | both advance gated legal work | KEEP separate semantics; connect them with explicit dependency edges |
| host/MCP/Extism adapters | multiple ingress protocols | KEEP adapters; share one execution contract and registry |
| `INTAKE_KV` legal records vs local workpapers | duplicate evidence/state surfaces | IMPROVE with provenance IDs and explicit system-of-record rules |
| skill/seat catalogs vs X402 D1 catalog | catalog replication | KEEP projection; add source hash/version and reconciliation checks |

No automatic merge is justified by current evidence.

# Attributions & Third-Party Notices

GLAW is released under the [MIT License](LICENSE). It **vendors** (bundles) several
third-party components so the firm is self-contained. Each retains its original
license; this file records the provenance. Where an upstream shipped a `LICENSE`/
`NOTICE`, that file is preserved in-tree next to the vendored code.

## Bundled engine

| Component | Path | Upstream | License |
|---|---|---|---|
| **GLAW Bookkeeping Engine** (`glaw_engine`) | `lib/bookkeeping/glaw_engine/` | [sebastienrousseau/bankstatementparser](https://github.com/sebastienrousseau/bankstatementparser) (renamed `bankstatementparser` → `glaw_engine`) | **Apache-2.0** — full text at [`lib/bookkeeping/UPSTREAM-LICENSE-Apache-2.0.txt`](lib/bookkeeping/UPSTREAM-LICENSE-Apache-2.0.txt); provenance in [`lib/bookkeeping/UPSTREAM.txt`](lib/bookkeeping/UPSTREAM.txt) |

## Vendored seats with their own license

These specialist seats are third-party; their original `LICENSE` is preserved beside them:

| Seat | License | Holder |
|---|---|---|
| [`seats/glaw-contract-review`](seats/glaw-contract-review/LICENSE) | MIT | © 2026 Christopher Sheehan |
| [`seats/glaw-seo-content`](seats/glaw-seo-content/LICENSE.txt) | MIT | © 2026 AgriciDaniel |
| [`seats/glaw-seo-geo`](seats/glaw-seo-geo/LICENSE.txt) | MIT | © 2026 AgriciDaniel |

## Other vendored seats

The remaining seats under [`seats/`](seats/) — the `glaw-fs-*` finance-model suite,
`glaw-pdf`, `glaw-docx`, `glaw-company-valuation`, and the GLAW-authored legal/tax/
accounting seats — are vendored per the provenance recorded in
[`seats/UPSTREAM.md`](seats/UPSTREAM.md). Seats authored for GLAW are covered by this
repo's MIT license; any that carry their own `LICENSE`/`NOTICE` retain it in-tree.
Sanitized on vendoring: nested `.git/`, `.encrypted/`, secrets, and caches are excluded.

## Methodology & interoperating projects

- **gstack** — the skill-orchestration methodology GLAW is built on.
- [legal-redline-tools](https://github.com/evolsb/legal-redline-tools) (MIT) — real Word tracked-changes, used by the contract chain.
- [claude-legal-skill](https://github.com/evolsb/claude-legal-skill) (MIT) — interoperating contract-review brain.

If you believe an attribution here is incomplete or incorrect, please open an issue —
we will correct it promptly.

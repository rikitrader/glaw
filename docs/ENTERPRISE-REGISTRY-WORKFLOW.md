# Enterprise Artifact and Model Registry

The registry is the cross-department control plane for financial models, actuarial runs,
tax workpapers, accounting memos, legal work product, IR decks, and board materials.

```text
artifact/model created
        ↓
registered with owner, department, lane, version, sources, risk class, and SHA-256
        ↓
independent review and human approval event
        ↓
validate hash chain, file hash, lineage, and approval state
        ↓
final-packet / release gate may consume the approved version
```

`bin/glaw-registry` stores newline-delimited events. Each event contains the previous
event hash and its own hash, so edits, deletion, reordering, or unrecorded approvals
are detected. Registration is immutable: a changed artifact requires a new version and
new approval event. High- and critical-risk artifacts cannot validate as ready without
a named human reviewer, role, and rationale.

This registry complements, rather than replaces, the source ledger, artifact manifest,
lane workpaper, Chief/Council decision, accounting controls, and citation gates. It does
not sign, file, publish, transmit, or approve professional work by itself. When a matter
contains `registry.jsonl`, `glaw-final-packet` now validates the registry and includes its
hash in the final-packet artifact hash set; a declared `universal.registry_required` matter
with no registry is blocked. Existing matters without a registry remain backward-compatible
until that control is declared.

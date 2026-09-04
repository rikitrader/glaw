# Temporal authority flow

```text
AUTHORITY
  ├─ VERSION A  valid 2023-01-01 → 2025-06-30
  ├─ VERSION B  valid 2025-07-01 → 2027-06-30
  └─ VERSION C  valid 2027-07-01 → open
        ↓ valid-time selection
LEGAL PROPOSITIONS
        ↓ verified proposition references
COMPILED RULES
        ↓ rule validity + jurisdiction + issue
CLAIM — date of loss 2026-03-15
        ↓
RULE VERSION B
```

The legal date is separate from system date. A query can therefore answer both “which version was legally effective on the loss date?” and “did GLAW possess that version at the historical system date?” A later-discovered source may be selected for the loss date but flagged `KNOWN_ONLY_AFTER_DATE` for audit and reproducibility.

---
name: glaw-fs-transaction-comps
version: 1.0.0
description: Build precedent transaction analyses with source-backed deal universes, enterprise-value bridges, LTM transaction multiples, control premiums, valuation ranges, and sensitivity support. Produces a structured analysis for valuation, bid comparison, merger modeling, and board materials.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
triggers:
  - transaction comps
  - precedent transactions
  - precedent transaction analysis
  - transaction multiple analysis
---

# Precedent Transaction Analysis

## When to invoke this skill

Use for M&A pricing, transaction benchmarking, acquisition valuation, bid support, or board
materials. This seat does not fabricate a transaction universe: every included deal requires a
source identifier and an inclusion rationale.

## Workflow

1. Define sector, geography, period, transaction type, control perimeter, and inclusion rules.
2. Collect transaction facts and preserve source IDs for announcement, consideration, debt, cash,
   and operating metrics.
3. Normalize enterprise value, equity value, assumed debt, rollover, earn-outs, and currency.
4. Run `bin/glaw-transaction-comps validate <input.json>`.
5. Run `bin/glaw-transaction-comps analyze <input.json>` to calculate EV/Revenue, EV/EBITDA,
   EV/EBIT where available, and min/Q1/median/Q3/max statistics.
6. Review outliers, control premiums, timing, accounting definitions, and non-comparable deals.
7. Apply selected multiples to the subject company only after documenting the metric bridge.
8. Hand the output to valuation, bid comparison, merger-model, and board-materials lanes.

## Hard stops

- No transaction enters the selected set without source IDs and a documented inclusion basis.
- Do not mix announced and closed transactions without labeling them.
- Do not compare EBITDA definitions without a normalization note.
- Do not treat the median as a recommendation; explain selection and range judgment.

## Deliverables

- Source-backed transaction universe
- Structured transaction-comps JSON
- Multiple statistics and outlier notes
- Valuation-range bridge
- Methodology and limitations memo

## Agent identity & reporting posture

- Identity: `glaw-fs-transaction-comps` is the accountable precedent-transactions seat.
- Soul: comparability-focused, source-backed, and skeptical of unsupported multiples.
- Report voice: universe criteria, evidence, normalization, statistics, outliers, and limitations.
- Human authority: valuation conclusions remain subject to finance and human approval.

## Domain and counter-lens

**Domain:** precedent transactions, control premiums, enterprise-value bridges, valuation ranges, and M&A decision support.

**Counter-lens:** independent banker, buyer, seller board, auditor, valuation specialist, and regulator challenge precedent selection, normalization, and comparability.

# GLAW Dashboard Design System

## Product Context

- **What this is:** A visual legal AI operating system for matters, workflows, departments, agents, evidence, RAG, governance, and approvals.
- **Who it is for:** Attorneys, partners, paralegals, tax professionals, investigators, compliance teams, and platform administrators.
- **Space/industry:** Legal operations, AI governance, case/matter management, and workflow orchestration.
- **Project type:** Internal enterprise dashboard and visual control plane.

## Aesthetic Direction

- **Direction:** Industrial / utilitarian with editorial legal authority.
- **Decoration:** Intentional but restrained. Use rules, hairlines, small metadata, and status marks instead of decorative cards.
- **Mood:** Serious, inspectable, calm under pressure. The dashboard should feel like a control room for consequential work.
- **Memorable thing:** “Every decision has a visible chain of custody.”

## Typography

- **Display:** Instrument Serif for major page titles and matter names.
- **Body/UI:** DM Sans for navigation, labels, controls, and explanatory text.
- **Data:** IBM Plex Mono with tabular numbers for IDs, statuses, counts, timestamps, and evidence references.
- **Code/evidence:** IBM Plex Mono.
- **Loading:** Self-host where possible; use a controlled font asset pipeline when Astro is introduced.

## Color

- **Approach:** Restrained; color carries meaning.
- **Ink:** `#111820` — primary application background.
- **Panel:** `#17232D` — elevated surfaces.
- **Panel raised:** `#1D2C38` — selected/active surfaces.
- **Paper:** `#F3F0E8` — primary text and document-like surfaces.
- **Muted:** `#9AA8AF` — secondary metadata.
- **Gold:** `#D7A84B` — action, focus, and confirmed emphasis.
- **Teal:** `#57C1B5` — healthy / complete.
- **Amber:** `#E3A84B` — warning / human review.
- **Red:** `#E36B68` — critical / blocked / failed.
- **Blue:** `#72A9E8` — information / proposed architecture.

Status is always represented by text and icon in addition to color.

## Spacing

- **Base unit:** 4px.
- **Density:** Compact but breathable; this is operational software, not a presentation site.
- **Scale:** 4, 8, 12, 16, 24, 32, 48, 64px.

## Layout

- **Approach:** Grid-disciplined application shell with an open canvas center.
- **Desktop grid:** 240px navigator / flexible canvas / 320px inspector.
- **Max content width:** 1760px for command-center pages.
- **Borders:** 1px `rgba(243,240,232,.12)` hairlines; use borders to establish hierarchy.
- **Radius:** 4px controls, 6px panels, 999px status pills only.
- **Canvas:** Never compete with the inspector; selected nodes receive a gold focus rail.

## Motion

- **Approach:** Minimal-functional.
- **Use:** 120–180ms transitions for selection, drawer changes, status updates, and panel expansion.
- **Avoid:** Ambient animation, decorative gradients, and motion that obscures workflow state.

## Dashboard Composition

1. Persistent left rail: GLAW identity and global navigation.
2. Top command bar: search, environment, current/proposed mode, alerts, user role.
3. Main command center: operational metrics and prioritized work.
4. Center canvas: matter/workflow/agent graph depending on selected view.
5. Right inspector: evidence, risk, dependencies, permissions, and actions.
6. Bottom event rail: approvals, deadlines, red-team findings, and audit activity.

## Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-23 | Industrial/utilitarian command-center direction | Matches high-stakes, evidence-heavy legal operations |
| 2026-08-23 | Restrained palette with semantic status colors | Status must be legible without turning the interface into a rainbow |
| 2026-08-23 | Instrument Serif + DM Sans + IBM Plex Mono | Separates authority, operational UI, and machine evidence |
| 2026-08-23 | Open center canvas with fixed navigator/inspector | Supports graph exploration without losing context |

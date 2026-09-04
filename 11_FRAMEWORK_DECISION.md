# Visual Engine Decision

## Mandatory platform decision

The application framework is **Astro**. The visual editor is a selective React island using `@xyflow/react`; the rest of the application remains Astro-rendered. This is a hard constraint, not a preference.

## Candidate matrix

Scores are 1–10 architecture-fit estimates for this repository. They are based on the repository requirements and current documentation review; large-graph performance is not yet benchmarked locally.

| Framework | Dev | TS | React | Custom nodes | Nested | Swimlanes | 1k+ graph | Layout | Editing | Execution | MiniMap | Extensibility | OSS/license | A11y | Mobile | Collab | Maintain | Total/180 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| React Flow / XYFlow | 9 | 9 | 10 | 10 | 8 | 8 | 8 | 8 | 9 | 7 | 9 | 9 | 9 | 7 | 7 | 8 | 9 | 145 |
| Rete.js | 8 | 9 | 8 | 9 | 9 | 7 | 7 | 7 | 9 | 9 | 6 | 9 | 9 | 6 | 6 | 8 | 8 | 134 |
| LogicFlow | 7 | 8 | 8 | 8 | 7 | 7 | 8 | 7 | 8 | 6 | 7 | 8 | 8 | 6 | 6 | 7 | 7 | 123 |
| ELK.js + custom renderer | 6 | 9 | 8 | 10 | 9 | 10 | 9 | 10 | 6 | 4 | 2 | 10 | 10 | 5 | 5 | 7 | 6 | 126 |
| Cytoscape.js | 8 | 8 | 7 | 7 | 8 | 6 | 10 | 8 | 5 | 5 | 4 | 8 | 9 | 6 | 5 | 7 | 8 | 121 |
| Mermaid | 9 | 6 | 6 | 3 | 2 | 4 | 3 | 7 | 1 | 1 | 1 | 4 | 10 | 6 | 7 | 1 | 9 | 80 |
| D3 | 6 | 7 | 8 | 10 | 8 | 9 | 8 | 9 | 7 | 4 | 2 | 10 | 10 | 5 | 5 | 7 | 6 | 121 |
| JointJS | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 9 | 6 | 8 | 8 | 6 | 7 | 6 | 8 | 7 | 124 |
| GoJS | 8 | 8 | 8 | 10 | 9 | 9 | 9 | 9 | 9 | 7 | 9 | 9 | 2 | 8 | 7 | 8 | 8 | 136 |

The table weights React integration, custom editing, maintainability, licensing, and the existing Astro constraint. ELK.js is a layout engine, not the primary editor; use it behind XYFlow after a benchmark. GoJS is technically strong but loses on open-source suitability/licensing.

## Current documentation evidence

Context7 documentation confirms XYFlow supports custom node/edge registries, MiniMap, programmatic graph control, and viewport culling via `onlyRenderVisibleElements`. Rete documentation confirms custom React rendering and an execution engine, which is useful but increases coupling risk for this mandatory graph/execution separation. Cytoscape documentation confirms strong canvas/WebGL-oriented large-graph rendering and layouts but is less aligned with a node-editor UX.

## Decision

**Astro + `@xyflow/react` island + ELK.js layout adapter**, with a canonical graph model and Worker/D1 API. Do not migrate the whole application to React. Do not use XYFlow's graph objects as the business execution engine.

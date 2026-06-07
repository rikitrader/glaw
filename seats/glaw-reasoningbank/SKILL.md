---
name: glaw-reasoningbank
version: 1.0.0
description: Trajectory store for outcome-aware retrieval — every gate run is recorded as task→verdict→outcome→score, distilled into the learnings ledger, and (when reachable) mirrored to AgentDB/Qdrant for semantic recall. The RuFlo ReasoningBank pattern for GLAW.
allowed-tools: Read, Bash, Glob, Grep
triggers: [reasoningbank, trajectory, what worked before, recall similar matter, outcome-aware]
---

# GLAW — ReasoningBank (trajectory store + outcome-aware retrieval)

Closes the RuFlo ReasoningBank loop for GLAW: **trajectory → verdict → distillation → pattern**.
Every Chief-Counsel / consensus run is an experience; this skill records it, scores the outcome,
and makes the best past trajectories retrievable so future runs start smarter.

## When to invoke this skill
- After a gate/matter run, to **record** the trajectory + outcome (distillation).
- Before a new matter, to **recall** how similar positions were resolved (outcome-aware retrieval).

## Memory layers (durable JSONL is source of truth; vector index is an accelerator)
- **Episodic** — the run: `{type:"episode", matter, position, verdict, score, ts}`.
- **Semantic/knowledge** — distilled defects + synthesized meta-rules (the learnings ledger).
- **Procedural** — the workflow that worked: `{type:"procedure", steps:[...]}`.

## Record a trajectory (distillation)
```bash
L=~/.claude/skills/glaw/bin/glaw-learnings
# the verdict + each new defect from the run
python3 "$L" add '{"type":"episode","scope":"firm","error_class":"<position>","where":"<matter/doc>","wrong":"<verdict+top risk>","fix":"<what resolved it>","confidence":<1-10>}'
python3 ~/.claude/skills/glaw/bin/glaw-reflect --apply   # synthesize higher-level patterns
```

## Recall (outcome-aware retrieval)
1. **Always** (keyword + importance): `python3 ~/.claude/skills/glaw/bin/glaw-learnings preflight [matter]`
   — ranks by confidence, meta-rules first.
2. **Semantic (when Qdrant is up):** use the qdrant MCP (`mcp__qdrant__qdrant-find`) to recall
   GLAW memories relevant to the positions under review, even when worded differently. Start Qdrant
   with `docker run -d -p 6333:6333 qdrant/qdrant` if down.
3. **GNN ranking (when available):** `cd ~/.glaw/agentdb && npx agentdb train --db ./glaw.db`
   learns to rank which past defects matter most once enough episodes accumulate.
   NOTE: agentdb v3-alpha currently errors at the consolidation step (`this.db.save is not a
   function`) and needs ≥3 episodes per domain — treat GNN ranking as 🟡 pending the alpha fix;
   JSONL + Qdrant carry retrieval until then.

## Backend status (honest)
- ✅ JSONL ledger + reflection — live, source of truth.
- ✅ Qdrant semantic recall — live when the daemon is up (proven: differently-worded query returned the exact PLR rule).
- 🟡 AgentDB GNN training — wired, blocked on an upstream alpha bug + needs accumulated episodes.

## Workflow
1. Emit the GLAW preamble.
2. To record: gather the run's verdict + new defects → `glaw-learnings add` (episode + each defect) → `glaw-reflect --apply` → mirror to Qdrant if up.
3. To recall: `glaw-learnings preflight` + Qdrant `qdrant-find` → hand the merged digest to the requesting seat/loop.

## Gates
Never fabricate an outcome or score · record only what actually happened · UPL disclaimer on deliverables.

> ATTORNEY/CPA WORK-PRODUCT — a licensed professional must review, sign, and file. Not legal/tax advice.

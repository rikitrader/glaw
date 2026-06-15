# GLAW — development notes (scoped to this skill repo)

GLAW is a virtual corporate law firm modeled on gstack's skill-orchestration
methodology. The unit of work is a **matter** (litigation case OR corp/fund build),
not a code repo.

## Layout
```
glaw/
├── SKILL.md                 # /glaw orchestrator (Managing Partner)
├── VERSION
├── ETHOS.md                 # firm principles
├── README.md                # org chart + usage
├── bin/glaw                 # state machinery: matter lifecycle + config + docket
├── bin/glaw-preamble.sh     # shared preamble every stage emits
├── lib/firm-roster.md       # SINGLE SOURCE OF TRUTH for seat → skill routing
├── intake|strategy|structure|draft|adversarial|file|docket|matter-retro/SKILL.md
├── autocounsel/SKILL.md     # runs the review bench back-to-back (autoplan analog)
└── <12 practice-group agents>/SKILL.md
```

## Conventions every SKILL.md follows
- Frontmatter: `name`, `version`, `description`, `allowed-tools`, `triggers`.
- First content section: `## When to invoke this skill`.
- Stage skills emit the shared preamble:
  `bash bin/glaw-preamble.sh`.
- Stages route work to seats in `lib/firm-roster.md` — never freelance a position
  a seat already owns. Delegate to existing skills via the Skill tool; invoke
  `/glaw-*` agents for new seats.
- Numbered `## Workflow` with explicit AskUserQuestion gates.

## Hard gates (enforced by the orchestrator)
1. Conflicts cleared (`/glaw-ethics-conflicts`) before strategy.
2. Citations verified (`/glaw-legal-research`) before file.
3. Adversarial RED→BLUE (`/glaw-adversarial`) before file.
4. UPL disclaimer on every external deliverable.

## State
Lives under `$GLAW_HOME` (default `~/.glaw`): `config.yaml`, `matters/<slug>/`
(`matter.md`, `docket.jsonl`, `timeline.jsonl`, `.stage`), `.active`.

## NOT legal advice
GLAW produces attorney work-product drafts. It does not form an attorney-client
relationship or practice law. Keep that line load-bearing in every skill.

## Vault rule
At matter close, `/glaw-matter-retro` writes the matter's Obsidian vault
(`<matter>-vault/` sibling) per the user's universal workflow rule.

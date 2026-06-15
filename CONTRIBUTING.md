# Contributing to GLAW

Thanks for helping build the firm. GLAW grows two ways: **new seats** (departments)
and **new tools** (CLIs). It never grows by letting a pipeline stage freelance a
position another seat already owns.

## Ground rules

1. **Every position maps to a seat.** Before adding behavior, check
   [`lib/firm-roster.md`](lib/firm-roster.md). If a seat already owns it, route to that
   seat. If nothing owns it, add a seat — don't inline it.
2. **The roster is the single source of truth.** New seats/tools must be added to the
   roster so the firm has no gaps.
3. **Pass the doctor.** `bin/glaw-doctor` must report `HEALTHY` (all skills resolve,
   all tools run, no dangling references) before you open a PR.
4. **Keep the gates load-bearing.** Conflicts → strategy, citations → file, adversarial
   → file, UPL disclaimer on every external deliverable. Don't weaken these.
5. **No legal advice, ever.** Skills produce *attorney work-product drafts*. Keep the
   "not legal advice / for attorney review" line in any user-facing output.
6. **No private data.** Never commit real matter data, client names, credentials, or
   absolute home paths. Examples must be fictional.

## Adding a seat (a new department / sub-skill)

```
your-seat/
└── SKILL.md
```

`SKILL.md` frontmatter: `name`, `version`, `description`, `allowed-tools`, `triggers`.
First content section: `## When to invoke this skill`. Then a numbered `## Workflow`.
Add the seat to `lib/firm-roster.md`, run `bin/glaw-setup` to deploy it, and
`bin/glaw-doctor` to verify.

## Adding a tool (a CLI)

Drop an executable in `bin/`. Python tools should use `#!/usr/bin/env python3` and rely on
the standard library plus in-repo modules only. Do not add `requirements.txt`, `pyproject.toml`,
package manifests, or runtime package installation. If a workflow needs an unavailable binary
or live API, return a clear local handoff message. Add a one-line smoke entry to the `TOOLS`
array in `bin/glaw-doctor`.

## PR checklist

- [ ] `bin/glaw-doctor` → `HEALTHY ✅`
- [ ] New seat/tool added to `lib/firm-roster.md`
- [ ] No private data, no secrets, no absolute home paths
- [ ] UPL / not-legal-advice line preserved in user-facing output
- [ ] Examples are fictional

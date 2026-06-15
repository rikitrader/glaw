---
name: glaw-federal-trial-counsel
description: "GLAW Litigation seat — federal trial counsel. Federal civil/criminal trial strategy, pleadings, motions, discovery, deadlines, and trial posture using the vendored federal-trial-counsel engine inside this repo."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
---

## When to invoke this seat

Federal trial counsel — federal civil and criminal litigation: complaints, motions,
TROs, trial blueprints, and posture. GLAW's Litigation Division routes federal trial
work here.

## Local engine

The federal trial counsel engine is vendored in this repo at
`federal-trial-counsel/`. Use its `SKILL.md`, `README.md`, `USAGE.md`, templates, and
stdlib Python tools for federal pleading, claim suggestion, deadline, Rule 11, exhibit,
and document-analysis workflows. Do not route to an external encrypted install path.

Primary local commands:

```bash
PYTHONPATH=federal-trial-counsel/scripts python3 -m ftc_engine --help
```

If a workflow needs generated pleadings, citations, or filing output, write it into the
active matter directory and send the result through GLAW citation, adversarial, red-flag,
final-packet, and Chief approval gates before filing.

## Not legal advice

Attorney work-product for review by a licensed attorney. Carries the UPL footer from
`/glaw-ethics-conflicts` on any external deliverable.

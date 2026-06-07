# GLAW — a virtual corporate law firm (Claude Code skill suite)

GLAW is a virtual corporate law firm built as a [Claude Code](https://claude.com/claude-code)
skill suite. It opens a **matter** (a litigation case or a corp/fund build) and drives it
through intake → strategy → structure → draft → adversarial → file → docket → retro,
routing each task to a specialist seat.

## Install

```bash
pip install glaw
glaw install        # fetches the firm into ~/.claude/skills/glaw and deploys the sub-skills
glaw doctor         # health check
```

Then, inside Claude Code, use `/glaw` (or any `/glaw-*` seat).

## What's inside

- **65+ skills**: 8-stage pipeline + practice groups (corporate, securities/funds, tax,
  litigation, investigations) and an **SEC Enforcement & Investigations Division**
  (investigator, FCPA, whistleblower, expert-witness, Wells response, 10-K/10-Q risk).
- **Forms library**: a three-jurisdiction (Delaware / Florida / Texas) template bank —
  bylaws, indemnity, consents, LLC/LP agreements, equity & financing forms, fund docs —
  genericized to `[BRACKETS]` with real state-statute conversions (FBCA / TBOC).
- **Hard gates**: conflicts cleared, citations verified, adversarial RED→BLUE, and a
  UPL "attorney work-product, not legal advice" footer on every external deliverable.
- **Tooling**: `glaw-doctor` health harness, `glaw-gate` enforcement, `glaw-test`
  contract suite, and a due-diligence HTML report bridge.

## Not legal advice

GLAW produces **attorney work-product drafts**. It does not form an attorney-client
relationship or practice law. A licensed attorney in the relevant jurisdiction must
review, adapt, and sign every output.

MIT licensed. Source: https://github.com/rikitrader/glaw

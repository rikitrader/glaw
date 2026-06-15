# GLAW Installation Guide

GLAW installs as one local app with no third-party package installation.

## Requirements

- macOS or Linux shell
- `bash` or `zsh`
- `python3` from the operating system or developer tools
- Git, only for cloning and updating the repository

No `pip install`, `npm install`, virtualenv, package manager bootstrap, or Python package fetch is part of the supported install path.

Optional local binaries unlock OCR/PDF bank-statement ingestion:

```bash
brew install poppler tesseract
```

Digital PDFs can use `pdftotext` from Poppler. Scanned PDFs use Python-owned OCR orchestration over `pdftoppm` plus `tesseract`; the repo performs rendering control, OCR pass selection, row parsing, validation, and audit output.

## Fresh Install

```bash
git clone https://github.com/rikitrader/glaw ~/.claude/skills/glaw
cd ~/.claude/skills/glaw
./setup
bin/glaw-doctor
```

`./setup` deploys the orchestrator and every `/glaw-*` sub-skill into the configured skills root. It also creates local state under `~/.glaw`.

## Existing Checkout

```bash
cd ~/.claude/skills/glaw
git pull
./setup
bin/glaw-doctor
```

If you are running from a development checkout, set the skill directory explicitly:

```bash
cd /path/to/glaw
GLAW_SKILL_DIR="$PWD" ./setup
GLAW_SKILL_DIR="$PWD" bin/glaw-doctor
```

## Codex and Claude

GLAW is stored as Agent Skills markdown plus local CLIs, so the same repository can be used by Claude Code, Codex, or any compatible agent. The commands remain the same:

```text
/glaw
/glaw-contract-review
/glaw-federal-trial-counsel
/glaw-accounting
```

## Verification

Run these after install or update:

```bash
GLAW_SKILL_DIR="$PWD" bash bin/glaw-test
GLAW_SKILL_DIR="$PWD" bash bin/glaw-doctor
printf 'date,description,amount\n2026-01-01,Test deposit,100.00\n' > /tmp/glaw-sample.csv
GLAW="$PWD" bin/glaw-bank-ingest /tmp/glaw-sample.csv --format json
```

Expected result: skill contracts pass, doctor reports healthy, and bank ingest returns JSON.

Google Sheets bank data:

```bash
GLAW="$PWD" bin/glaw-bank-ingest "https://docs.google.com/spreadsheets/d/<id>/edit#gid=0" --format json
```

The sheet must be viewable by link or published/exportable as CSV.

## State Locations

| Path | Purpose |
|---|---|
| `~/.glaw` | local matter state, ledgers, audit logs, learning ledger |
| `~/.claude/skills/glaw` | default skill checkout |
| `bin/` | deterministic local commands |
| `lib/` | in-repo libraries and compatibility shims |
| `seats/` | vendored specialist seats |

Do not commit secrets, real client material, OAuth tokens, or live credentials.

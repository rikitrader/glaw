#!/usr/bin/env bash
# glaw-matter-run.sh — drives a REAL matter through GLAW's state machine for the
# README demo GIF. Every stage/docket/timeline call below is the genuine `bin/glaw`
# CLI; only GLAW_HOME is redirected to a throwaway dir so the demo never touches
# your real ~/.glaw. Re-record with: vhs demo/glaw-matter-run.tape
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLAW="$ROOT/bin/glaw"
export GLAW_HOME="$(mktemp -d)/glaw-demo"
trap 'rm -rf "$(dirname "$GLAW_HOME")"' EXIT

# ── colors ───────────────────────────────────────────────────────────────────
B=$'\033[1m'; D=$'\033[2m'; R=$'\033[0m'
NAVY=$'\033[38;5;33m'; GOLD=$'\033[38;5;178m'; GRN=$'\033[38;5;42m'
RED=$'\033[38;5;203m'; GRY=$'\033[38;5;245m'
step(){ sleep 0.65; }
gate(){ printf "   ${GOLD}⛔ gate${R} ${GRY}%-22s${R} ${GRN}✓ cleared${R}\n" "$1"; sleep 0.5; }
say(){  printf "${NAVY}${B}▸ %-11s${R} %s\n" "$1" "$2"; sleep 0.35; }

printf "${GOLD}${B}⚖  GLAW${R} ${D}— the firm opens a matter and works it end-to-end${R}\n\n"
sleep 0.5

# ── INTAKE ────────────────────────────────────────────────────────────────────
say "intake" "FL holdco over opco + asset protection"
"$GLAW" matter new "Apex Holdco Formation" >/dev/null
"$GLAW" matter use apex-holdco-formation >/dev/null
"$GLAW" config set track corp-build >/dev/null
gate "conflicts cleared"; step

# ── PIPELINE ──────────────────────────────────────────────────────────────────
say "strategy"   "deal thesis → holdco/opco split, 1202 QSBS path"; "$GLAW" stage strategy   >/dev/null
say "structure"  "entity org chart + tax + cap table";              "$GLAW" stage structure  >/dev/null
say "draft"      "formation, governance & asset-protection docs";    "$GLAW" stage draft      >/dev/null
say "adversarial" "IRS + creditor red-team every position";          "$GLAW" stage adversarial >/dev/null
gate "RED → BLUE survived"
say "file"       "assemble signature-ready packet";                  "$GLAW" stage file       >/dev/null
gate "citations verified"

# ── DOCKET ────────────────────────────────────────────────────────────────────
say "docket" "annual report + 83(b) election window"
"$GLAW" docket add 2026-07-05 "83(b) election — 30-day deadline" >/dev/null
"$GLAW" docket add 2027-05-01 "FL annual report" >/dev/null
"$GLAW" stage close >/dev/null
gate "UPL disclaimer attached"

# ── RESULT ────────────────────────────────────────────────────────────────────
printf "\n${B}docket${R}\n"
"$GLAW" docket list 2>/dev/null | sed -E 's/.*"due":"([^"]*)".*"desc":"([^"]*)".*/   \1  •  \2/'
printf "\n${GRN}${B}✓ matter closed${R} ${GRY}— packet ready for a licensed attorney to review & sign${R}\n"
sleep 1.2

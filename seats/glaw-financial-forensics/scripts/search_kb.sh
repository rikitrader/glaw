#!/usr/bin/env bash
# search_kb.sh — grounded search over the Financial Forensics knowledge base.
# Returns matching lines with source-file + line number so you can open and cite the exact
# passage. ZERO hallucination: it only surfaces text that physically exists in the KB.
#
# Usage:
#   search_kb.sh "percentage of completion"            # case-insensitive substring
#   search_kb.sh -C 3 "over-billing"                   # 3 lines of context
#   search_kb.sh -f "WIP schedule"                     # list matching FILES only
#   search_kb.sh -w peterson "job cost"                # restrict to files matching 'peterson'
set -euo pipefail

KB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../knowledge" && pwd)"
CTX=2; FILES_ONLY=0; FILTER=""

while [[ "${1:-}" == -* ]]; do
  case "$1" in
    -C) CTX="$2"; shift 2 ;;
    -f) FILES_ONLY=1; shift ;;
    -w) FILTER="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 1 ;;
  esac
done

QUERY="${*:-}"
[[ -z "$QUERY" ]] && { echo "usage: search_kb.sh [-C N] [-f] [-w word] \"query\""; exit 1; }

TARGETS=()
while IFS= read -r line; do TARGETS+=("$line"); done < <(find "$KB_DIR" -name '*.md' ! -name '_index.md' | { [[ -n "$FILTER" ]] && grep -i "$FILTER" || cat; } | sort)
[[ ${#TARGETS[@]} -eq 0 ]] && { echo "no KB files match filter '$FILTER'"; exit 1; }

if [[ "$FILES_ONLY" -eq 1 ]]; then
  grep -il -- "$QUERY" "${TARGETS[@]}" | while read -r p; do echo "  $(basename "$p")"; done
  exit 0
fi

HITS=0
for p in "${TARGETS[@]}"; do
  if grep -iq -- "$QUERY" "$p"; then
    echo "═══════════════════════════════════════════════════════════"
    echo "📄 $(basename "$p")"
    echo "───────────────────────────────────────────────────────────"
    grep -in -C "$CTX" -- "$QUERY" "$p" | head -60
    echo ""
    HITS=$((HITS+1))
  fi
done
echo "═══════════════════════════════════════════════════════════"
echo "Matched in $HITS file(s). Cite as: (KB: <file>.md — \"<quote>\")."
[[ "$HITS" -eq 0 ]] && echo "NOTE: no KB hit — do NOT fabricate. Say it's outside the KB."

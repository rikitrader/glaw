#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/bin/glaw-lane"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
"$CLI" scaffold --lane-id LANE-0001 --matter DEAL-0001 --department ma --lane transaction-terms --owner terms-seat --artifact-type terms-register > "$TMP/lane.json"
"$CLI" validate "$TMP/lane.json" | rg '"valid": true'
"$CLI" transition "$TMP/lane.json" review | rg '"status": "review"'
"$CLI" catalog | rg 'public-markets/earnings-communications'
echo "lane engine contract: ok"

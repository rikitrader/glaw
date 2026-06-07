#!/usr/bin/env bash
# ingest_pdf.sh — convert a financial PDF (bank statement, credit-card statement, tax
# return, payroll report, invoice) into faithful markdown for extraction. Uses
# opendataloader-pdf (Apache-2.0, #1 benchmark parser) so tables/columns survive.
#
# ZERO hallucination: this only mechanically extracts what is in the PDF. After it runs,
# READ the produced .md and extract transactions from the real text — never guess numbers
# off a thumbnail.
#
# Usage:
#   ingest_pdf.sh "/path/to/statement.pdf"                 # -> ./_ingest/<name>.md
#   ingest_pdf.sh "/path/to/statement.pdf" /out/dir         # custom output dir
#   ingest_pdf.sh -p PASSWORD "/path/encrypted.pdf"         # password-protected PDF
#   ingest_pdf.sh /folder/of/statements                     # whole folder
set -euo pipefail

# opendataloader-pdf needs Java 21 on PATH (per install note)
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"

PASS=""
if [[ "${1:-}" == "-p" ]]; then PASS="$2"; shift 2; fi

INPUT="${1:?usage: ingest_pdf.sh [-p password] <pdf-or-folder> [outdir]}"
OUT="${2:-$(pwd)/_ingest}"
mkdir -p "$OUT"

if ! command -v opendataloader-pdf >/dev/null 2>&1; then
  echo "ERROR: opendataloader-pdf not found. Install: uv tool install opendataloader-pdf" >&2
  exit 1
fi

echo "Ingesting: $INPUT"
echo "Output dir: $OUT"
ARGS=( "$INPUT" -o "$OUT" -f markdown --table-method cluster --threads 4 )
[[ -n "$PASS" ]] && ARGS+=( -p "$PASS" )

opendataloader-pdf "${ARGS[@]}"

echo ""
echo "=== Produced markdown ==="
find "$OUT" -name '*.md' -newer "$OUT" 2>/dev/null | sort || find "$OUT" -name '*.md' | sort
echo ""
echo "NEXT: Read the .md file(s) above and run Phase 1 extraction. Tie beginning balance +"
echo "credits - debits = ending balance before classifying (Verification Gate 1)."

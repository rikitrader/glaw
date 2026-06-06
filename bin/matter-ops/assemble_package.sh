#!/usr/bin/env bash
# Assemble a date+time-stamped FINAL PACKAGE for a matter: all documents, IRS forms,
# filled filings, agreements/contracts, dossier + FAQ + manifest, in one subfolder.
# Usage: assemble_package.sh <matter_dir> [irs_forms_dir]
set -euo pipefail
M="${1:?matter dir required}"
FORMS="${2:-/private/tmp/irs_forms}"
STAMP=$(date +%Y%m%d-%H%M%S)
PKG="$M/final-package-$STAMP"
mkdir -p "$PKG/documents" "$PKG/irs-forms" "$PKG/filings"
cp "$M"/drafts/*.md "$PKG/documents/" 2>/dev/null || true
cp "$M"/drafts/*.json "$PKG/documents/" 2>/dev/null || true
[ -d "$FORMS" ] && cp "$FORMS"/*.pdf "$PKG/irs-forms/" 2>/dev/null || true
# pull the dossier + FAQ to the top level if present
cp "$M"/drafts/29-*dossier*.md "$PKG/" 2>/dev/null || true
cp "$M"/drafts/30-*faq*.md "$PKG/" 2>/dev/null || true
# any filled forms staged in /private/tmp
cp /private/tmp/*FILLED*.pdf "$PKG/filings/" 2>/dev/null || true
{
  echo "FINAL PACKAGE — $(basename "$M")"
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')   Stamp: $STAMP"
  echo "-----------------------------------------------------------"
  echo "documents: $(ls "$PKG/documents" 2>/dev/null | wc -l | tr -d ' ') files"
  echo "irs-forms: $(ls "$PKG/irs-forms" 2>/dev/null | wc -l | tr -d ' ') PDFs"
  echo "filings:   $(ls "$PKG/filings" 2>/dev/null | wc -l | tr -d ' ') files"
  echo "-----------------------------------------------------------"
  echo "ATTORNEY/CPA WORK-PRODUCT — review, sign, file. Not legal/tax advice."
} > "$PKG/00-MANIFEST.txt"
echo "$PKG"

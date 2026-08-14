#!/usr/bin/env bash
# Deterministic portable source-ingest fixture for tests. Call after creating $TMP.
setup_premium_source_fixture() {
  local fixture_base="$1"
  export GLAW_PREMIUM_SOURCE_ROOT="$fixture_base/premium-sources"
  local fixture_bin="$fixture_base/premium-bin"
  mkdir -p "$GLAW_PREMIUM_SOURCE_ROOT/TAX CREDIT" "$GLAW_PREMIUM_SOURCE_ROOT/LLC" "$GLAW_PREMIUM_SOURCE_ROOT/SEC" "$fixture_bin"

  local relative
  for relative in \
    "TAX CREDIT/Options to Broaden the US Tax Base (May 2024 Update).pdf" \
    "TAX CREDIT/what-are-the-different-types-of-irrevocable-trusts.pdf" \
    "TAX CREDIT/fy2026h1_tab8.pdf" \
    "TAX CREDIT/F_PUB_550.pdf" \
    "LLC/FormCandOS.pdf" \
    "SEC/id257bpm.pdf"
  do
    printf 'Portable source-ingest fixture for %s\n' "$relative" > "$GLAW_PREMIUM_SOURCE_ROOT/$relative"
  done

  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'source_path="$2"' \
    'i=0' \
    'while [ "$i" -lt 40 ]; do' \
    '  printf "Extracted fixture text %s row %s with tax trust securities evidence and provenance.\\n" "$source_path" "$i"' \
    '  i=$((i + 1))' \
    'done' > "$fixture_bin/pdftotext"
  chmod +x "$fixture_bin/pdftotext"
  export PATH="$fixture_bin:$PATH"
}

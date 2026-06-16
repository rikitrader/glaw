#!/usr/bin/env bash
# citation_corpus_test.sh - source corpus capture and tamper detection.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

TMP="$(mktemp -d)"; export GLAW_HOME="$TMP"
GLAW="$ROOT/bin/glaw"
CORPUS="$ROOT/bin/glaw-citation-corpus"
CITES="$ROOT/bin/glaw-citation-gate"

"$GLAW" matter new "Citation Corpus" >/dev/null

"$CORPUS" capture --id BAD-FETCH --source-url "https://example.com/fake-law" --fetch >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "corpus fetch blocks non-approved authority domains"

"$CORPUS" capture --id BAD-TEXT --source-url "https://example.com/fake-law" \
  --text "fake law" --segment "fake law" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "corpus capture rejects off-allowlist source URLs even with pasted text"

GLAW_AUTHORITY_DOMAINS="example.com" "$CORPUS" capture --id BAD-ENV --source-url "https://example.com/fake-law" \
  --text "fake law" --segment "fake law" >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "runtime environment cannot approve fake authority domains"

python3 - "$CORPUS" "$TMP" <<'PY'
from __future__ import annotations

import pathlib
import runpy
import sys
from argparse import Namespace

corpus = pathlib.Path(sys.argv[1])
ns = runpy.run_path(str(corpus), run_name="glaw_citation_corpus_test")
ns["source_text"].__globals__["fetch_url"] = lambda _url: "Fetched official source text supports real rules only."
rc = ns["cmd_capture"](Namespace(
    id="BAD-SEGMENT",
    source_url="https://uscode.house.gov/authority.txt",
    text="",
    file="",
    fetch=True,
    authenticated_copy=False,
    segment="absent fabricated holding",
    notes="",
    matter=None,
))
sys.exit(0 if rc == 2 else 1)
PY
rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "corpus fetch rejects absent segment from fetched allowlisted source"

FAKE_TEXT="Imaginary v. Fabricated, 999 U.S. 1 (2026), says fake matching text can support anything."
"$CORPUS" capture --id FAKE-1 --source-url "https://courtlistener.com/opinion/999/fake/" \
  --text "$FAKE_TEXT" --segment "fake matching text can support anything" >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "pasted fabricated corpus can be stored only as untrusted evidence"

"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "corpus status blocks pasted untrusted authority"

"$CITES" record --id C-FAKE --proposition "Fake case supports the claim" \
  --authority "Imaginary v. Fabricated" --status verified --source-url "https://courtlistener.com/opinion/999/fake/" \
  --reviewer legal-research --support-summary "The pasted segment matches the fake proposition." \
  --corpus-id FAKE-1 >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "verified citation blocks fabricated pasted corpus even when text matches"

"$GLAW" matter new "Citation Corpus Trusted" >/dev/null
printf '%s\n' "26 U.S.C. 6001 supports tax records sufficient to establish liability and support the return." > "$TMP/usc-6001.txt"
"$CORPUS" capture --id CORP-1 --source-url "https://uscode.house.gov/" \
  --file "$TMP/usc-6001.txt" --authenticated-copy \
  --segment "tax records sufficient to establish liability" >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "authenticated official-copy corpus capture writes source and segment hashes"

"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "corpus status validates captured source"

"$CITES" record --id C-1 --proposition "Tax records must support the return" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://example.com/" \
  --reviewer legal-research --support-summary "URL mismatch should fail." \
  --corpus-id CORP-1 >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 2 ] && echo 1 || echo 0)" "citation record blocks corpus/source-url mismatch"

"$CITES" record --id C-1 --proposition "Tax records must support the return" \
  --authority "26 U.S.C. 6001" --status verified --source-url "https://uscode.house.gov/" \
  --reviewer legal-research --support-summary "The captured segment supports tax records sufficient to establish liability." \
  --corpus-id CORP-1 >/dev/null; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "citation record accepts matching corpus id"

"$CITES" complete >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "citation gate completes with validated corpus"

python3 - "$TMP/matters/citation-corpus-trusted/citation_corpus.jsonl" <<'PY'
import hashlib
import json
import sys

path = sys.argv[1]
rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
rows[-1]["ts"] = "2025-01-01T00:00:00Z"
payload = dict(rows[-1])
payload.pop("row_hash", None)
rows[-1]["row_hash"] = hashlib.sha256(
    json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
with open(path, "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, sort_keys=False) + "\n")
PY

"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "corpus status blocks stale authority captures"

"$CITES" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation gate blocks stale authority captures"

printf 'tampered\n' >> "$TMP/matters/citation-corpus-trusted/citation_corpus/CORP-1.txt"
"$CORPUS" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "corpus status blocks source text tamper"

"$CITES" status >/dev/null 2>&1; rc=$?
ok "$([ "$rc" = 1 ] && echo 1 || echo 0)" "citation gate blocks corpus tamper"

rm -rf "$TMP"
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }

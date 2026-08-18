#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export GLAW_HOME="$TMP/glaw-home"
"$ROOT/bin/glaw" matter new "Legal Governor Fixture" >/dev/null
slug="legal-governor-fixture"
"$ROOT/bin/glaw-legal-governor" scaffold --matter-slug "$slug" >/dev/null
if "$ROOT/bin/glaw-legal-governor" draft-check --matter-slug "$slug" >/dev/null; then
  echo "FAIL: missing Governor report must block drafting" >&2
  exit 1
fi
"$ROOT/bin/glaw-legal-governor" assess --matter-slug "$slug" --input "$GLAW_HOME/matters/$slug/workpapers/legal-governor-input.json" >/dev/null || true
if "$ROOT/bin/glaw-legal-governor" draft-check --matter-slug "$slug" >/dev/null; then
  echo "FAIL: incomplete Governor input must block drafting" >&2
  exit 1
fi
"$ROOT/bin/glaw-legal-governor" verify-audit --matter-slug "$slug" >/dev/null
mkdir -p "$GLAW_HOME/matters/$slug/citation_corpus"
printf 'Official authority segment.' > "$GLAW_HOME/matters/$slug/citation_corpus/src.txt"
python3 - "$GLAW_HOME/matters/$slug" <<'PY'
import hashlib, json, pathlib, sys
d=pathlib.Path(sys.argv[1])
text=(d/'citation_corpus/src.txt').read_text()
row={"id":"SRC-CORP-1","source_url":"https://www.sec.gov/test","source_path":"citation_corpus/src.txt","source_sha256":hashlib.sha256(text.encode()).hexdigest(),"segment":text,"segment_sha256":hashlib.sha256(text.encode()).hexdigest(),"trust_level":"authoritative"}
(d/'citation_corpus.jsonl').write_text(json.dumps(row)+'\n')
citation={"id":"CIT-1","status":"verified","corpus_id":"SRC-CORP-1","proposition":"test","authority":"test","support_summary":"test","reviewer":"legal-research","source_url":row["source_url"]}
(d/'citations.jsonl').write_text(json.dumps(citation)+'\n')
(d/'workpapers/rag-request.json').write_text(json.dumps({"question":"test question","jurisdiction":"test","corpus_ids":["SRC-CORP-1"],"supporting_propositions":["test"],"adverse_propositions":["test adverse"]}))
PY
context_json="$GLAW_HOME/matters/$slug/workpapers/rag-request.json"
"$ROOT/bin/glaw-legal-governor" context-build --matter-slug "$slug" --input "$context_json" > "$TMP/context.json"
context_sha=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["context_sha256"])' "$TMP/context.json")
printf 'Claude analysis' > "$TMP/claude.md"
printf 'Codex analysis' > "$TMP/codex.md"
"$ROOT/bin/glaw-legal-governor" parity-record --matter-slug "$slug" --agent claude --context-sha256 "$context_sha" --analysis "$TMP/claude.md" >/dev/null
"$ROOT/bin/glaw-legal-governor" parity-record --matter-slug "$slug" --agent codex --context-sha256 "$context_sha" --analysis "$TMP/codex.md" >/dev/null
"$ROOT/bin/glaw-legal-governor" context-check --matter-slug "$slug" >/dev/null
"$ROOT/bin/glaw-legal-governor" parity-check --matter-slug "$slug" >/dev/null
"$ROOT/bin/glaw-legal-governor" matrix --matter-slug "$slug" >/dev/null
if "$ROOT/bin/glaw-legal-governor" final-check --matter-slug "$slug" >/dev/null; then
  echo "FAIL: activated Governor matter must block final readiness without assessment" >&2
  exit 1
fi
echo "ALL PASS"

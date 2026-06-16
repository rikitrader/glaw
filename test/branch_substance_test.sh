#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

pass=0
fail(){ echo "FAIL: $1" >&2; exit 1; }
ok(){ pass=$((pass+1)); }

check_branch(){
  local branch="$1"
  local ref="$2"
  local tmpl="$3"
  local terms="$4"
  local skill="$ROOT/$branch/SKILL.md"
  local ref_path="$ROOT/$branch/references/$ref"
  local tmpl_path="$ROOT/$branch/templates/$tmpl"

  [ -s "$skill" ] || fail "$branch SKILL.md missing"
  [ -s "$ref_path" ] || fail "$branch reference missing: $ref"
  [ -s "$tmpl_path" ] || fail "$branch template missing: $tmpl"
  grep -q "references/$ref" "$skill" || fail "$branch SKILL.md does not route to reference"
  grep -q "templates/$tmpl" "$skill" || fail "$branch SKILL.md does not route to template"
  grep -q "SRC-####" "$ref_path" || fail "$branch reference lacks source discipline"
  grep -q "Sign-Off" "$ref_path" || fail "$branch reference lacks sign-off discipline"
  grep -q "UPL Footer\\|nonbinding model\\|Attorney work-product" "$tmpl_path" || fail "$branch template lacks authority boundary"
  IFS='|' read -r -a required_terms <<< "$terms"
  for term in "${required_terms[@]}"; do
    grep -qi "$term" "$ref_path" || fail "$branch reference lacks required term: $term"
  done
  ok
}

check_branch "constitutional" "scrutiny-tier-checklist.md" "constitutional-bench-memo.md" "standing|scrutiny|tailoring|state action|remedy"
check_branch "legislative" "model-law-drafting-checklist.md" "section-by-section-summary.md" "authority|definitions|fiscal|implementation|severability"
check_branch "judicial" "bench-memo-standards-guide.md" "model-opinion-skeleton.md" "standard of review|record|burden|disposition|appeal"
check_branch "admin-law" "apa-record-review-checklist.md" "administrative-record-index.md" "authority|procedure|record|finality|remedy"

echo "$pass passed"

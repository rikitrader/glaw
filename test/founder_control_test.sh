#!/usr/bin/env bash
# Deterministic founder-control invariant and voting-universe regression tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/pass.json" <<'JSON'
{
  "schema": "glaw-founder-control/v2",
  "denominator_basis": "fully_diluted_economic_ownership",
  "founder_holder": "Founder",
  "threshold_percent": "5.01",
  "vote_floor_percent": "50.1",
  "economic": [
    {"holder": "Founder", "shares": "5.01"},
    {"holder": "Investors", "shares": "94.99"}
  ],
  "voting": [
    {"holder": "Founder", "shares": "5.01", "votes_per_share": "100"},
    {"holder": "Investors", "shares": "94.99", "votes_per_share": "1"}
  ]
}
JSON

python3 - "$ROOT" "$TMP/pass.json" <<'PY'
import json, subprocess, sys
root, path = sys.argv[1:]
out = subprocess.run([root + "/bin/glaw-founder-control", path, "--sensitivity"], text=True, capture_output=True)
assert out.returncode == 0, out.stderr
data = json.loads(out.stdout)
assert data["result"]["status"] == "pass"
assert float(data["result"]["founder_voting_power_percent"]) > 84
assert len(data["sensitivity"]) == 5
PY

cat > "$TMP/fail.json" <<'JSON'
{
  "schema": "glaw-founder-control/v2",
  "denominator_basis": "fully_diluted_economic_ownership",
  "founder_holder": "Founder",
  "threshold_percent": "5.01",
  "vote_floor_percent": "50.1",
  "economic": [{"holder":"Founder","shares":"5.01"},{"holder":"Investors","shares":"94.99"}],
  "voting": [{"holder":"Founder","shares":"5.01","votes_per_share":"20"},{"holder":"Investors","shares":"94.99","votes_per_share":"1"},{"holder":"Preferred","shares":"100","votes_per_share":"10"}]
}
JSON

if python3 "$ROOT/bin/glaw-founder-control" "$TMP/fail.json" >/dev/null; then
  echo "FAIL: special voting universe should fail the founder floor" >&2
  exit 1
fi

cat > "$TMP/no-implicit-vote.json" <<'JSON'
{
  "schema": "glaw-founder-control/v2",
  "denominator_basis": "fully_diluted_economic_ownership",
  "founder_holder": "Founder",
  "economic": [{"holder":"Founder","shares":"5.01"},{"holder":"Class C","shares":"94.99"}],
  "voting": [{"holder":"Founder","shares":"5.01","votes_per_share":"100"},{"holder":"Class C","shares":"94.99"}]
}
JSON
if python3 "$ROOT/bin/glaw-founder-control" "$TMP/no-implicit-vote.json" >/dev/null; then
  echo "FAIL: voting rows must not receive an implicit one-vote default" >&2
  exit 1
fi

python3 "$ROOT/bin/glaw-premium-lanes" validate --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"] == "pass", d; assert "founder-control-assurance" in d["lanes"]'
echo "ALL PASS"

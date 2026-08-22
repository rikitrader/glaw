#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import json
from pathlib import Path

catalog = json.loads(Path('lib/lane-catalog.json').read_text())
lanes = catalog['departments']['legal-reasoning-benchmark']
names = {x['name'] for x in lanes}
assert len(lanes) == 20
for required in ('domain-intake', 'original-law-question', 'answer-set-construction',
                 'academic-reference-package', 'adversarial-law-review',
                 'ambiguity-solvability-red-team', 'environmental-energy-esg-climate'):
    assert required in names, required
for skill in ('glaw-legal-reasoning-benchmark', 'glaw-legal-reasoning-adversary'):
    text = Path('seats', skill, 'SKILL.md').read_text()
    assert 'Identity' in text and 'Soul' in text and 'Domain' in text
doc = Path('docs/LEGAL-REASONING-BENCHMARK-WORKFLOW.md')
assert doc.exists() and 'Senior-lawyer rubric' in doc.read_text()
print(f'legal reasoning benchmark contract: {len(lanes)} lanes, posture, soul, domains, workflow present')
PY

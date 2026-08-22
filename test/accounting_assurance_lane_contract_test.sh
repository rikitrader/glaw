#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import json
from pathlib import Path

catalog = json.loads(Path('lib/lane-catalog.json').read_text())
required = {
    'financial-statement-preparation', 'technical-accounting-research',
    'us-gaap-asc-codification', 'pcaob-standards', 'ifrs-isa-standards',
    'revenue-recognition', 'lease-accounting', 'consolidation-accounting',
    'transaction-accounting-ma', 'erp-sap-oracle-controls',
    'consolidation-system-close', 'audit-management-workpapers',
    'research-tool-evidence', 'external-audit-process', 'internal-audit-assurance',
    'sox-internal-controls', 'reference-financial-statements',
    'technical-accounting-memo', 'audit-workpaper-package', 'accounting-judgment-rubric'
}
actual = {lane['name'] for lane in catalog['departments']['accounting-assurance']}
missing = required - actual
assert not missing, f'missing accounting lanes: {sorted(missing)}'
doc = Path('docs/ACCOUNTING-ASSURANCE-OPERATING-WORKFLOW.md')
assert doc.exists() and 'Judgment gate' in doc.read_text()
print(f'accounting assurance contract: {len(actual)} lanes, workflow present')
PY

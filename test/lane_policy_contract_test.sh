#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 - "$ROOT" "$TMP" <<'PY'
import json, pathlib, subprocess, sys
root,tmp=map(pathlib.Path,sys.argv[1:])
catalog=json.loads((root/'lib/lane-catalog.json').read_text())
policies=json.loads((root/'lib/lane-policies.json').read_text())['policies']
assert set(catalog['departments']) == set(policies)
n=0
for dept,items in catalog['departments'].items():
    assert policies[dept]['required_gates'] and policies[dept]['workflow'] and policies[dept]['artifact_requirements']
    for item in items:
        n+=1; out=tmp/f'{n}.json'
        subprocess.run([str(root/'bin/glaw-lane'),'scaffold','--lane-id',f'POL-{n:04d}','--department',dept,'--lane',item['name'],'--owner',item['seat']],check=True,stdout=out.open('w'))
        data=json.loads(out.read_text())
        assert set(policies[dept]['required_gates']) <= set(data['required_gates'])
        subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],check=True,stdout=subprocess.DEVNULL)
        data['status']='approved'; data['gates']={k:True for k in data['gates']}; data['artifacts'][0]['status']='approved'; out.write_text(json.dumps(data))
        subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],check=True,stdout=subprocess.DEVNULL)
        data['gates'][policies[dept]['required_gates'][0]]=False; out.write_text(json.dumps(data))
        if subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],stdout=subprocess.DEVNULL).returncode == 0: raise AssertionError(f'approved policy bypass: {dept}/{item["name"]}')
print(f'lane policy contract: {n} lanes and {len(policies)} department policies pass')
PY

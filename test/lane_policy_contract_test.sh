#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 - "$ROOT" "$TMP" <<'PY'
import json, pathlib, subprocess, sys
root,tmp=map(pathlib.Path,sys.argv[1:])
catalog=json.loads((root/'lib/lane-catalog.json').read_text())
policies=json.loads((root/'lib/lane-policies.json').read_text())['policies']
available={p.name for p in (root/'bin').iterdir() if p.is_file()}
assert set(catalog['departments']) == set(policies)
n=0
for dept,items in catalog['departments'].items():
    assert policies[dept]['required_gates'] and policies[dept]['workflow'] and policies[dept]['artifact_requirements']
    assert set(policies[dept]['engine_commands']) <= available, f"missing engine command for {dept}"
    for item in items:
        n+=1; out=tmp/f'{n}.json'
        seat=root/'seats'/item['seat']/'SKILL.md'
        source=root/item['seat'].removeprefix('glaw-')/'SKILL.md'
        seat=seat if seat.exists() else source
        assert seat.exists() and f"name: {item['seat']}" in seat.read_text(), f"missing or mismatched seat: {item['seat']}"
        subprocess.run([str(root/'bin/glaw-lane'),'scaffold','--lane-id',f'POL-{n:04d}','--department',dept,'--lane',item['name'],'--owner',item['seat']],check=True,stdout=out.open('w'))
        data=json.loads(out.read_text())
        assert set(policies[dept]['required_gates']) <= set(data['required_gates'])
        assert data['engine_commands'] == policies[dept]['engine_commands']
        subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],check=True,stdout=subprocess.DEVNULL)
        data['status']='approved'; data['gates']={k:True for k in data['gates']}; [a.update(status='approved') for a in data['artifacts']]; out.write_text(json.dumps(data))
        subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],check=True,stdout=subprocess.DEVNULL)
        data['gates'][policies[dept]['required_gates'][0]]=False; out.write_text(json.dumps(data))
        if subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],stdout=subprocess.DEVNULL).returncode == 0: raise AssertionError(f'approved policy bypass: {dept}/{item["name"]}')
        data['gates'][policies[dept]['required_gates'][0]]=True; data['artifacts']=[a for a in data['artifacts'] if a['type'] != policies[dept]['artifact_requirements'][0]]; out.write_text(json.dumps(data))
        if subprocess.run([str(root/'bin/glaw-lane'),'validate',str(out)],stdout=subprocess.DEVNULL).returncode == 0: raise AssertionError(f'approved artifact bypass: {dept}/{item["name"]}')
print(f'lane policy contract: {n} lanes and {len(policies)} department policies pass')
PY

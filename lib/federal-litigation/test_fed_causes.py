#!/usr/bin/env python3
"""Self-test: federal causes index + CLI + templates + statute excerpts."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).parent
def main():
    d=json.loads((HERE/"federal-causes-index.json").read_text())
    causes=d["causes"]
    assert len(causes)>=50, len(causes)
    cats={c["cat"] for c in causes}
    for must in ("civil-rights","securities","fraud-federal","rico","antitrust","employment","consumer","ip","qui-tam-govt"):
        assert must in cats, must
    for c in causes:
        assert c.get("n") and c.get("cat") and c.get("elements") and c.get("basis"), c.get("n")
        assert isinstance(c.get("defenses"),list) and c["defenses"], c["n"]
    blob=json.dumps(causes).lower()
    for claim in ("1983","rico","10b-5","false claims","flsa","title vii","fdcpa","lanham","wire fraud","bivens","monell"):
        assert claim in blob, claim
    # CLI
    for cmd in (["list"],["category","rico"],["show","wire fraud"],["search","fraud"],["sol","4"]):
        o=subprocess.run([sys.executable,str(HERE/"fed_causes.py")]+cmd,capture_output=True,text=True)
        assert o.returncode==0 and o.stdout.strip(), cmd
    # templates: complaints carry a court caption; reference docs are checked separately below
    tdir=HERE/"templates"; tmpls=list(tdir.glob("*.md"))
    assert len(tmpls)>=8, len(tmpls)
    for t in tdir.glob("complaint-*.md"):
        x=t.read_text()
        assert ("UNITED STATES DISTRICT COURT" in x or "COURT OF FEDERAL CLAIMS" in x) and "[" in x, t.name
        assert ("NOT legal advice" in x or "work-product" in x or "UPL" in x), t.name
    # supporting templates (parity with the FL side)
    names={f.name for f in tdir.glob("*.md")}
    for must in ("federal-causes-catalog.md","answer-affirmative-defenses-federal.md","motions-pack-federal.md","discovery-federal.md","intake-federal.md","subpoena-federal.md"):
        assert must in names, must
    assert len([f for f in tdir.glob("complaint-*.md")])>=20, "complaints"
    cat=(tdir/"federal-causes-catalog.md").read_text(); assert "SHARED FEDERAL CAPTION" in cat and "RICO" in cat
    mot=(tdir/"motions-pack-federal.md").read_text()
    for m in ("Twombly","Celotex","FRE 702","Rule 11","§ 1447","9 U.S.C"):
        assert m in mot, m
    ans=(tdir/"answer-affirmative-defenses-federal.md").read_text(); assert "Rule 8(c)" in ans and "COUNTERCLAIM" in ans
    # statute excerpts
    se=(HERE/"statute-text"/"federal-excerpts.md").read_text()
    for s in ("1962","1343","1983","3729","3282"):
        assert s in se, s
    print(f"  ✓ {len(causes)} federal causes ({len(cats)} categories), CLI works, {len(tmpls)} templates captioned/footed, statute excerpts present")
    print("OK: federal causes library self-test passed")
    return 0
if __name__=="__main__": raise SystemExit(main())

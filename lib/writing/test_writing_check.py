#!/usr/bin/env python3
"""Self-test: glaw-writing-check linter (bad prose flags; clean prose ~clean; motion sections)."""
import subprocess, sys, json
from pathlib import Path
TOOL = str(Path(__file__).resolve().parents[2] / "bin" / "glaw-writing-check")
def run(text, *args):
    return subprocess.run([sys.executable, TOOL, "-", "--json", *args],
                          input=text, capture_output=True, text=True)
def main():
    bad = json.loads(run("It is important to note that clearly we believe the defendant is obviously liable.").stdout)
    assert bad["flags"] >= 4, bad["flags"]
    clean = json.loads(run("Defendant breached the contract. Smith v. Jones, 1 F.3d 2, 4 (11th Cir. 2020).").stdout)
    assert clean["flags"] <= 1, clean
    mot = json.loads(run("The argument is short.", "--motion").stdout)
    assert "missing_section" in mot["findings"] and mot["findings"]["missing_section"], "motion sections"
    fed = json.loads(run("COMES NOW Plaintiff and argues.", "--federal").stdout)
    assert fed["findings"].get("missing_element"), "federal: should flag missing elements"
    full = ("UNITED STATES DISTRICT COURT Case No. INTRODUCTION STATEMENT OF FACTS LEGAL STANDARD "
            "ARGUMENT RELIEF REQUESTED CONCLUSION Respectfully submitted")
    okfed = json.loads(run(full, "--federal").stdout)
    assert not okfed["findings"].get("missing_element"), "federal: complete filing should pass structure"
    assert run("").returncode == 0  # empty stdin
    print(f"  ✓ writing-check: bad={bad['flags']} flags, clean={clean['flags']}, motion-sections detected")
    print("OK: glaw-writing-check self-test passed")
    return 0
if __name__ == "__main__": raise SystemExit(main())

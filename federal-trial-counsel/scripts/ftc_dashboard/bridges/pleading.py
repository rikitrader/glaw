"""Bridge to the `federal_pleading_engine` TypeScript CLI.

Runs it via `npx tsx`, points it at a tempdir, reads back the three output
files (pleading_output.json, pleading_output.md, complaint_draft.md).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

_FPE_DIR = Path(__file__).resolve().parent.parent.parent / "federal_pleading_engine"


def generate(case: dict, claims: list[str] | None = None, suggest: bool = False) -> dict:
    if not _FPE_DIR.exists():
        return {"error": f"federal_pleading_engine not found at {_FPE_DIR}"}

    with tempfile.TemporaryDirectory(prefix="fpe-") as td:
        in_path = os.path.join(td, "case.json")
        out_dir = os.path.join(td, "out")
        os.makedirs(out_dir, exist_ok=True)
        with open(in_path, "w") as f:
            json.dump(case, f)

        cmd = ["npx", "-y", "tsx", "cli.ts",
               "--input", in_path, "--out", out_dir, "--format", "markdown"]
        if suggest:
            cmd.append("--suggest")
        if claims:
            cmd += ["--claims", ",".join(claims)]

        try:
            proc = subprocess.run(cmd, cwd=str(_FPE_DIR), capture_output=True,
                                  text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return {"error": "federal_pleading_engine timed out (>120s)"}

        if proc.returncode != 0:
            return {"error": f"pleading engine exited {proc.returncode}",
                    "stderr": proc.stderr.strip()[-2000:],
                    "stdout": proc.stdout.strip()[-2000:]}

        result: dict = {"stdout": proc.stdout}
        for name, key in [("pleading_output.json", "output"),
                          ("pleading_output.md", "markdown"),
                          ("complaint_draft.md", "complaint")]:
            p = os.path.join(out_dir, name)
            if os.path.exists(p):
                with open(p) as f:
                    result[key] = json.load(f) if name.endswith(".json") else f.read()
        return result


def list_claims() -> dict:
    """Ask the TS CLI for its claim inventory (independent of the Python list)."""
    if not _FPE_DIR.exists():
        return {"error": f"federal_pleading_engine not found at {_FPE_DIR}"}
    proc = subprocess.run(["npx", "-y", "tsx", "cli.ts", "--list"],
                          cwd=str(_FPE_DIR), capture_output=True, text=True, timeout=60)
    return {"stdout": proc.stdout, "stderr": proc.stderr.strip()[-2000:]}

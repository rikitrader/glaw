"""Bridge to the `courtlistener` TypeScript CLI.

Invokes it via `npx tsx` and returns parsed JSON. The CLI writes JSON to a
file by default — we use a tempfile.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

_CL_DIR = Path(__file__).resolve().parent.parent.parent / "courtlistener"


def search(query: str, court: list[str] | None = None, after: str | None = None,
           before: str | None = None, sort: str | None = None,
           limit: int = 20, search_type: str = "opinions",
           next_url: str | None = None) -> dict:
    if not _CL_DIR.exists():
        return {"error": f"CourtListener module not found at {_CL_DIR}"}

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        out_path = tf.name

    try:
        cmd = ["npx", "-y", "tsx", "cli.ts", "--q", query or "pagination",
               "--type", search_type, "--limit", str(limit), "--output", out_path,
               "--json"]
        if court:
            cmd += ["--court", ",".join(court)]
        if after:
            cmd += ["--after", after]
        if before:
            cmd += ["--before", before]
        if sort:
            cmd += ["--sort", sort]
        if next_url:
            cmd += ["--next", next_url]

        env = os.environ.copy()
        proc = subprocess.run(cmd, cwd=str(_CL_DIR), capture_output=True,
                              text=True, env=env, timeout=60)
        if proc.returncode != 0:
            return {"error": f"courtlistener CLI exited {proc.returncode}",
                    "stderr": proc.stderr.strip()[-2000:]}
        try:
            with open(out_path) as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Could not parse courtlistener output: {e}"}
    finally:
        try:
            os.unlink(out_path)
        except FileNotFoundError:
            pass

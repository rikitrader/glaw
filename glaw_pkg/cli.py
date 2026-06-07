"""GLAW installer CLI.

`pip install glaw` ships this thin installer; `glaw install` fetches the firm
(skill suite) from GitHub into ~/.claude/skills/glaw and deploys the sub-skills.
Keeping the wheel small (the firm is ~190 markdown/script files) and always
current with the published repo.
"""
import argparse
import io
import os
import shutil
import sys
import tarfile
import urllib.request

from . import __version__

REPO = "rikitrader/glaw"
DEST = os.path.expanduser("~/.claude/skills/glaw")
TARBALL = "https://github.com/{repo}/archive/refs/heads/{ref}.tar.gz"

# top-level entries in the repo that make up the firm (skills + tooling + libs)
FIRM_GLOBS = ("bin", "lib", "SKILL.md", "VERSION", "ETHOS.md", "CLAUDE.md", "README.md")


def _fetch(ref):
    url = TARBALL.format(repo=REPO, ref=ref)
    print(f"[glaw] downloading {url}")
    with urllib.request.urlopen(url) as r:  # noqa: S310 (trusted GitHub URL)
        return r.read()


def install(ref="main", force=False):
    if os.path.exists(DEST) and not force:
        print(f"[glaw] {DEST} already exists. Re-run with --force to overwrite.", file=sys.stderr)
        return 1
    data = _fetch(ref)
    tmp = DEST + ".incoming"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        members = tf.getmembers()
        root = members[0].name.split("/")[0]  # e.g. glaw-main
        tf.extractall(tmp, filter="data")
    extracted = os.path.join(tmp, root)
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
    shutil.move(extracted, DEST)
    shutil.rmtree(tmp, ignore_errors=True)
    # deploy sub-skills as top-level /glaw-* commands if the setup script is present
    setup = os.path.join(DEST, "bin", "glaw-setup")
    if os.path.exists(setup):
        os.chmod(setup, 0o755)
        os.system(f'bash {setup!r}')
    print(f"[glaw] installed the firm to {DEST}")
    print("[glaw] run `glaw doctor` to verify, then use /glaw in Claude Code.")
    return 0


def doctor():
    d = os.path.join(DEST, "bin", "glaw-doctor")
    if not os.path.exists(d):
        print("[glaw] not installed — run `glaw install` first.", file=sys.stderr)
        return 1
    return os.system(f'bash {d!r}') >> 8


def main(argv=None):
    p = argparse.ArgumentParser(prog="glaw", description="GLAW — virtual corporate law firm (Claude Code skill suite)")
    sub = p.add_subparsers(dest="cmd")
    pi = sub.add_parser("install", help="install/update the GLAW firm into ~/.claude/skills/glaw")
    pi.add_argument("--ref", default="main", help="git ref/branch/tag to install (default: main)")
    pi.add_argument("--force", action="store_true", help="overwrite an existing install")
    sub.add_parser("doctor", help="run the GLAW health check")
    sub.add_parser("version", help="print version")
    args = p.parse_args(argv)
    if args.cmd == "install":
        return install(args.ref, args.force)
    if args.cmd == "doctor":
        return doctor()
    if args.cmd == "version" or args.cmd is None:
        print(f"glaw {__version__}")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

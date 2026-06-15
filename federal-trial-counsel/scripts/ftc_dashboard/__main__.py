"""Entry point: `python3 -m ftc_dashboard [--host 127.0.0.1] [--port 8765]`."""
from __future__ import annotations

import argparse
import functools
import http.server
import threading
import time
import webbrowser
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="ftc_dashboard",
                                     description="Federal Trial Counsel static dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    static = Path(__file__).resolve().parent / "static"
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(static))
    url = f"http://{args.host}:{args.port}"
    print(f"Federal Trial Counsel static dashboard: {url}")
    print("API routes are disabled in zero-dependency mode; use the ftc CLI.")
    if not args.no_browser:
        threading.Thread(target=lambda: (time.sleep(0.8), webbrowser.open(url)), daemon=True).start()
    http.server.ThreadingHTTPServer((args.host, args.port), handler).serve_forever()


if __name__ == "__main__":
    main()

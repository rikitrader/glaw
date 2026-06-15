"""Entry point: `python3 -m ftc_dashboard [--host 127.0.0.1] [--port 8765]`."""
from __future__ import annotations

import argparse
import webbrowser
import threading
import time

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(prog="ftc_dashboard",
                                     description="Federal Trial Counsel browser dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't auto-open the browser")
    parser.add_argument("--reload", action="store_true",
                        help="Auto-reload on code changes (development)")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print(f"\n  Federal Trial Counsel Dashboard")
    print(f"  Serving at {url}")
    print(f"  Press Ctrl+C to stop.\n")

    if not args.no_browser:
        def _open() -> None:
            time.sleep(0.8)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(
        "ftc_dashboard.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

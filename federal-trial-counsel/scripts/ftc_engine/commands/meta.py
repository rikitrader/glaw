"""Meta commands: claims, info, district, monitor, setup, doctor."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from ._shared import _load_case


def cmd_claims(args):
    """List all available federal claims."""
    from ..claims import CLAIM_LIBRARY, list_categories
    for cat in list_categories():
        print(f"\n## {cat.upper().replace('_', ' ')}")
        for key, meta in CLAIM_LIBRARY.items():
            if meta.category == cat:
                flags = []
                if meta.heightened_pleading:
                    flags.append("9(b)")
                if meta.exhaustion_required:
                    flags.append(f"exhaust:{meta.exhaustion_type}")
                if meta.immunities:
                    flags.append(f"imm:{','.join(meta.immunities)}")
                flag_str = f" [{'; '.join(flags)}]" if flags else ""
                print(f"  {key:<45} {meta.name}{flag_str}")


def cmd_info(args):
    """Show detailed claim metadata."""
    from ..claims import get_claim
    meta = get_claim(args.claim)
    if not meta:
        print(f"Unknown claim: {args.claim}")
        sys.exit(1)
    print(f"Name:           {meta.name}")
    print(f"Category:       {meta.category}")
    print(f"Source:         {meta.source}")
    print(f"Jurisdiction:   {meta.jurisdiction}")
    print(f"SOL:            {meta.statute_of_limitations}")
    print(f"Heightened 9b:  {meta.heightened_pleading}")
    print(f"Exhaustion:     {meta.exhaustion_required} ({meta.exhaustion_type or 'N/A'})")
    print(f"Immunities:     {', '.join(meta.immunities) or 'None'}")
    print(f"Defenses:       {'; '.join(meta.typical_defenses[:5])}")
    if meta.viability_warning:
        print(f"WARNING:        {meta.viability_warning}")


def cmd_district(args):
    """Manage district configuration."""
    from ..districts import (
        get_district, list_districts, get_active_district, set_active_district,
        format_district_info, format_district_list,
    )

    action = args.action

    if action == "list":
        print(format_district_list())
    elif action == "current":
        ctx = get_active_district()
        print(f"Active: {ctx.config.code} — {ctx.config.name}")
        if ctx.division:
            print(f"Division: {ctx.division}")
    elif action == "set":
        if not args.code:
            print("Error: district code required for 'set'", file=sys.stderr)
            sys.exit(1)
        ctx = set_active_district(args.code, args.division)
        print(f"Active district set to: {ctx.config.code} — {ctx.config.name}")
        if ctx.division:
            print(f"Division: {ctx.division}")
    elif action == "info":
        code = args.code or get_active_district().config.code
        config = get_district(code)
        if not config:
            print(f"Unknown district: {code}", file=sys.stderr)
            sys.exit(1)
        print(format_district_info(config))
    else:
        print("Usage: ftc district [list|current|set <code>|info <code>]", file=sys.stderr)
        sys.exit(1)


def cmd_monitor(args):
    """Rule 11 duty monitor."""
    from ..rule11_monitor import generate_monitor_report, format_monitor_report
    case_data = _load_case(args.input)

    claim_keys = args.claims.split(",") if args.claims else None
    report = generate_monitor_report(case_data, claim_keys=claim_keys, mode=args.mode)

    output_text = format_monitor_report(report, verbose=args.verbose)

    if args.output:
        Path(args.output).write_text(output_text)
        print(f"Monitor report written to {args.output}")
    else:
        print(output_text)


def cmd_setup(args):
    """Configure local federal-trial-counsel state without installing packages."""

    print("=" * 70)
    print("         FEDERAL TRIAL COUNSEL — SETUP")
    print("=" * 70)

    # 1. Check Python version
    print(f"\n  Python: {sys.version.split()[0]}", end="")
    if sys.version_info >= (3, 9):
        print(" [OK]")
    else:
        print(" [WARN] Python 3.9+ recommended")

    # 2. Check local stdlib DOCX shim
    print("  docx shim: ", end="")
    try:
        import docx
        print(f"{getattr(docx, '__version__', 'local')} [OK]")
    except ImportError:
        print("not found [WARN]")

    # 3. Create config directory
    config_dir = Path.home() / ".ftc"
    config_dir.mkdir(exist_ok=True)
    print(f"  Config dir: {config_dir} [OK]")

    # 4. Write default config
    config_file = config_dir / "config.json"
    if not config_file.exists():
        config_file.write_text(json.dumps({"active_district": "mdfl", "division": "Orlando"}, indent=2))
        print(f"  Config file: created [OK]")
    else:
        print(f"  Config file: exists [OK]")

    # 5. Smoke test
    print("\n  Running smoke test...")
    try:
        from ..claims import CLAIM_LIBRARY
        from ..districts import list_districts
        print(f"  Claims loaded: {len(CLAIM_LIBRARY)} [OK]")
        print(f"  Districts loaded: {len(list_districts())} [OK]")
        print("\n  Setup complete!")
    except Exception as e:
        print(f"  Smoke test failed: {e}")

    print("=" * 70)


def cmd_doctor(args):
    """Diagnostic health check."""
    print("=" * 70)
    print("         FEDERAL TRIAL COUNSEL — DIAGNOSTICS")
    print("=" * 70)

    checks_passed = 0
    checks_total = 0

    # 1. Python version
    checks_total += 1
    py_ok = sys.version_info >= (3, 9)
    icon = "OK" if py_ok else "!!"
    print(f"  [{icon}] Python version: {sys.version.split()[0]}")
    if py_ok:
        checks_passed += 1

    # 2. local docx shim
    checks_total += 1
    try:
        import docx
        print(f"  [OK] docx shim: {getattr(docx, '__version__', 'local')}")
        checks_passed += 1
    except ImportError:
        print("  [!!] docx shim: not importable from this checkout")

    # 3. Config directory
    checks_total += 1
    config_dir = Path.home() / ".ftc"
    if config_dir.exists():
        print(f"  [OK] Config dir: {config_dir}")
        checks_passed += 1
    else:
        print(f"  [!!] Config dir: {config_dir} NOT FOUND — run 'python3 -m ftc_engine setup'")

    # 4. Active district
    checks_total += 1
    try:
        from ..districts import get_active_district
        ctx = get_active_district()
        print(f"  [OK] Active district: {ctx.config.code} — {ctx.config.name}")
        checks_passed += 1
    except Exception as e:
        print(f"  [!!] Active district: error — {e}")

    # 5. Claims library
    checks_total += 1
    try:
        from ..claims import CLAIM_LIBRARY
        print(f"  [OK] Claims library: {len(CLAIM_LIBRARY)} claims loaded")
        checks_passed += 1
    except Exception as e:
        print(f"  [!!] Claims library: error — {e}")

    # 6. Templates
    checks_total += 1
    templates_dir = Path(__file__).parent.parent.parent.parent / "assets" / "templates"
    if templates_dir.exists():
        count = sum(1 for _ in templates_dir.rglob("*.md"))
        print(f"  [OK] Templates: {count} templates found")
        checks_passed += 1
    else:
        print(f"  [..] Templates: directory not found (encrypted?)")

    # 7. Sample case
    checks_total += 1
    sample = Path(__file__).parent.parent / "sample_case.json"
    if sample.exists():
        print(f"  [OK] Sample case: {sample.name}")
        checks_passed += 1
    else:
        print(f"  [!!] Sample case: not found")

    # 8. CourtListener token
    checks_total += 1
    import os
    token = os.environ.get("COURTLISTENER_API_TOKEN")
    if token:
        print(f"  [OK] CourtListener API token: configured")
        checks_passed += 1
    else:
        print(f"  [..] CourtListener API token: not set (optional — online monitor mode)")
        checks_passed += 1  # Optional, so still passes

    print(f"\n  Result: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)

"""
Reference / metadata MCP handlers — claim library, district info, doctor.

Tools handled here:
  - ftc_claims         : list all federal claims with metadata
  - ftc_info           : detailed metadata for one claim
  - ftc_district       : info on a federal district court
  - ftc_district_list  : list all 94 federal district courts
  - ftc_doctor         : engine health check
"""
from __future__ import annotations

import os
from pathlib import Path


def handle_ftc_claims(args: dict) -> dict:
    from ..claims import CLAIM_LIBRARY, list_categories
    categories = {}
    for cat in list_categories():
        categories[cat] = [
            {"key": key, "name": meta.name, "heightened_9b": meta.heightened_pleading, "exhaustion": meta.exhaustion_required, "immunities": meta.immunities}
            for key, meta in CLAIM_LIBRARY.items() if meta.category == cat
        ]
    return {"categories": categories, "total": len(CLAIM_LIBRARY)}


def handle_ftc_info(args: dict) -> dict:
    from ..claims import get_claim
    meta = get_claim(args["claim_key"])
    if not meta:
        return {"error": f"Unknown claim: {args['claim_key']}"}
    return {
        "name": meta.name, "category": meta.category, "source": meta.source,
        "jurisdiction": meta.jurisdiction, "sol": meta.statute_of_limitations,
        "heightened_9b": meta.heightened_pleading, "exhaustion_required": meta.exhaustion_required,
        "exhaustion_type": meta.exhaustion_type, "immunities": meta.immunities,
        "typical_defenses": meta.typical_defenses, "viability_warning": meta.viability_warning,
    }


def handle_ftc_district(args: dict) -> dict:
    from ..districts import get_district, format_district_info
    config = get_district(args["code"])
    if not config:
        return {"error": f"Unknown district: {args['code']}"}
    return {"info": format_district_info(config), "code": config.code, "name": config.name}


def handle_ftc_district_list(args: dict) -> dict:
    from ..districts import list_districts
    districts = list_districts()
    return {"districts": [{"code": d.code, "name": d.name, "circuit": d.circuit} for d in districts], "total": len(districts)}


def handle_ftc_doctor(args: dict) -> dict:
    checks = []

    # Python version
    import sys as _sys
    py_ok = _sys.version_info >= (3, 9)
    checks.append({"name": "python_version", "ok": py_ok, "value": _sys.version.split()[0]})

    # python-docx
    try:
        import docx
        checks.append({"name": "python_docx", "ok": True, "value": docx.__version__})
    except ImportError:
        checks.append({"name": "python_docx", "ok": False, "value": "not installed"})

    # Config dir
    config_dir = Path.home() / ".ftc"
    checks.append({"name": "config_dir", "ok": config_dir.exists(), "value": str(config_dir)})

    # Claims
    try:
        from ..claims import CLAIM_LIBRARY
        checks.append({"name": "claims_library", "ok": True, "value": f"{len(CLAIM_LIBRARY)} claims"})
    except Exception as e:
        checks.append({"name": "claims_library", "ok": False, "value": str(e)})

    # Templates
    templates_dir = Path(__file__).parent.parent.parent.parent / "assets" / "templates"
    if templates_dir.exists():
        count = sum(1 for _ in templates_dir.rglob("*.md"))
        checks.append({"name": "templates", "ok": True, "value": f"{count} templates"})
    else:
        checks.append({"name": "templates", "ok": False, "value": "directory not found"})

    # CourtListener token
    token = os.environ.get("COURTLISTENER_API_TOKEN")
    checks.append({"name": "courtlistener_token", "ok": True, "value": "configured" if token else "not set (optional)"})

    passed = sum(1 for c in checks if c["ok"])
    return {"checks": checks, "passed": passed, "total": len(checks)}

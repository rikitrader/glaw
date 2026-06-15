#!/usr/bin/env python3
"""Zero-dependency DCF workbook validator."""
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def validate(path: str) -> dict:
    p = Path(path)
    errors, warnings, info = [], [], []
    if not p.exists():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(p) as zf:
        names = set(zf.namelist())
        if "xl/workbook.xml" not in names:
            errors.append("xl/workbook.xml missing")
        sheets = [n for n in names if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
        if not sheets:
            errors.append("no worksheet XML parts found")
        formula_count = 0
        for name in sheets:
            text = zf.read(name).decode("utf-8", errors="ignore")
            formula_count += text.count("<f")
            for marker in ("#VALUE!", "#DIV/0!", "#REF!", "#NAME?", "#NULL!", "#NUM!", "#N/A"):
                if marker in text:
                    errors.append(f"{name}: {marker}")
        info.extend([f"worksheets: {len(sheets)}", f"formulas: {formula_count}"])
        if formula_count == 0:
            warnings.append("no formulas detected")
    return {
        "file": path,
        "validation_date": datetime.now().isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_dcf.py model.xlsx", file=sys.stderr)
        return 2
    print(json.dumps(validate(sys.argv[1]), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

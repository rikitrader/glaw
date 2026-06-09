#!/usr/bin/env python3
"""Self-test: federal DOCX generator conforms; a plain DOCX does not; the CSS carries the directive."""
import sys, os, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
def main():
    try:
        import docx  # noqa
    except ImportError:
        print("SKIP: python-docx not available"); return 0
    sys.path.insert(0, str(HERE))
    import federal_docx, federal_format_check
    d = tempfile.mkdtemp(); out = os.path.join(d, "f.docx")
    federal_docx.build("UNITED STATES DISTRICT COURT\n\nI. INTRODUCTION\nPlaintiff respectfully submits.\n\nRespectfully submitted,", out)
    errs = federal_format_check.check(out)
    assert not errs, f"generated filing should conform: {errs}"
    from docx import Document
    p = os.path.join(d, "plain.docx"); Document().save(p)
    assert federal_format_check.check(p), "a plain DOCX must FAIL the federal check"
    css = (HERE.parents[1] / "lib" / "style" / "federal-filing.css").read_text()
    assert "1.25in" in css and "Times New Roman" in css and "line-height: 2.0" in css
    print("  ✓ federal render: generated→conforms, plain→fails, CSS carries TNR/double/1.25\"")
    print("OK: federal format self-test passed")
    return 0
if __name__ == "__main__": raise SystemExit(main())

"""Legacy PDF text interface retained for import compatibility."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Union

PathLike = Union[str, Path]
Engine = Literal["manual"]


class PDFExtractionError(RuntimeError):
    """Raised when PDF text extraction is requested."""


def extract_text(path: PathLike, *, engine: Engine = "manual") -> str:
    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise PDFExtractionError(f"PDF not found: {pdf_path}")
    raise PDFExtractionError(
        "This legacy PDF text interface is removed. Use bin/glaw-bank-ingest, which "
        "routes PDFs through lib/bookkeeping/pdf_extract.py and local OCR profiles."
    )

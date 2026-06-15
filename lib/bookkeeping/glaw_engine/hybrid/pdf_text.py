"""PDF text extraction disabled for absolute zero-third-party-package mode."""
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
        "PDF extraction is unavailable in absolute zero-third-party-package mode; "
        "convert the PDF to text or CSV before ingesting."
    )


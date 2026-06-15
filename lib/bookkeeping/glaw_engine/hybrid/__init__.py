# Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Legacy hybrid namespace retained for import compatibility.

Current GLAW workflows use the source-only runner plus local PDF/OCR extraction in
``lib/bookkeeping/pdf_extract.py``. Importing this namespace does not require external
packages; removed legacy entry points raise clear errors that point back to the supported
local path.
"""

from __future__ import annotations

from .llm_extractor import LLMExtractor, LLMExtractorError
from .ollama_direct import (
    OllamaDirectError,
    is_ollama_model,
    ollama_direct_completion,
)
from .orchestrator import (
    LOW_TEXT_DENSITY_THRESHOLD,
    IngestResult,
    smart_ingest,
)
from .pdf_text import PDFExtractionError, extract_text
from .scanner import ScanResult, scan_and_ingest
from .verification import (
    BalanceVerification,
    VerificationStatus,
    verify_balance,
    verify_balance_multi_currency,
)
from .vision import VisionExtractor, VisionExtractorError

__all__ = [
    "LOW_TEXT_DENSITY_THRESHOLD",
    "BalanceVerification",
    "IngestResult",
    "LLMExtractor",
    "LLMExtractorError",
    "OllamaDirectError",
    "PDFExtractionError",
    "ScanResult",
    "VerificationStatus",
    "VisionExtractor",
    "VisionExtractorError",
    "extract_text",
    "is_ollama_model",
    "ollama_direct_completion",
    "scan_and_ingest",
    "smart_ingest",
    "verify_balance_multi_currency",
    "verify_balance",
]

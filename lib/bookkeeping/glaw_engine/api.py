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

"""Legacy REST API namespace retained for import compatibility.

Supported GLAW workflows use local source-only CLIs: ``bin/glaw-bank-ingest``,
``bin/glaw-statements``, and ``bin/glaw-bookkeeping-doctor``. This module does not
start a web server and does not require a web framework.
"""

from __future__ import annotations

from typing import Any, Optional


class APIError(RuntimeError):
    """Raised when the API module can't start."""


def create_app(
    *,
    title: str = "Bank Statement Parser API",
    version: str = "0.0.8",
) -> Any:
    """Legacy factory retained for callers that import this symbol.

    Returns:
        Raises :class:`APIError` with the supported local CLI path.
    """
    raise APIError(
        "The legacy REST API is removed. Use bin/glaw-bank-ingest for local source-only ingest."
    )

def _result_to_dict(result: Any) -> dict[str, Any]:
    """Serialize an IngestResult to a JSON-safe dict."""
    return {
        "source_method": result.source_method,
        "source_format": result.source_format,
        "transaction_count": len(result.transactions),
        "transactions": [
            tx.model_dump(mode="json") for tx in result.transactions
        ],
        "verification": _verification_dict(result.verification),
        "warnings": list(result.warnings),
    }


def _verification_dict(v: Any) -> Optional[dict[str, Any]]:
    if v is None:
        return None
    return {
        "status": v.status.value,
        "opening_balance": str(v.opening_balance)
        if v.opening_balance is not None
        else None,
        "closing_balance": str(v.closing_balance)
        if v.closing_balance is not None
        else None,
        "total_credits": str(v.total_credits),
        "total_debits": str(v.total_debits),
        "discrepancy": str(v.discrepancy)
        if v.discrepancy is not None
        else None,
        "message": v.message,
    }


def main() -> None:
    """Console-script entry point for ``glaw_engine-api``."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compatibility entry point; use bin/glaw-bank-ingest instead."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (use 0.0.0.0 for container deployments)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port"
    )
    args = parser.parse_args()
    _ = args

    raise APIError("The legacy REST API server is removed. Use the local GLAW CLIs.")

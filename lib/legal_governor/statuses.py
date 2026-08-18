"""Shared Legal Governor statuses and fail-closed propagation rules."""

PASS = "PASS"
PASS_WITH_RISK = "PASS_WITH_RISK"
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
LEGAL_REVIEW_REQUIRED = "LEGAL_REVIEW_REQUIRED"
BLOCK = "BLOCK"

FINAL_STATUSES = {
    "SUPPORTED",
    "STRUCTURABLE_WITH_RISK",
    "LEGAL_REVIEW_REQUIRED",
    "BLOCKED_PENDING_COUNSEL",
}

BLOCKING_STATUSES = {RESEARCH_REQUIRED, LEGAL_REVIEW_REQUIRED, BLOCK}


def drafting_allowed(status: str) -> bool:
    """Allow only a review draft after all legal gates are clear."""
    return status in {PASS, PASS_WITH_RISK}


def public_status(status: str, *, counsel_required: bool = False) -> str:
    if status == BLOCK:
        return "BLOCKED_PENDING_COUNSEL"
    if status in {RESEARCH_REQUIRED, LEGAL_REVIEW_REQUIRED} or counsel_required:
        return "LEGAL_REVIEW_REQUIRED"
    if status == PASS_WITH_RISK:
        return "STRUCTURABLE_WITH_RISK"
    return "SUPPORTED"

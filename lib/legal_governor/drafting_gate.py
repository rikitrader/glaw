"""Downstream drafting gate; it cannot clear upstream legal failures."""

from .statuses import BLOCKING_STATUSES, drafting_allowed


def evaluate(report: dict) -> dict:
    statuses = report.get("component_statuses", {})
    blocking = [name for name, status in statuses.items() if status in BLOCKING_STATUSES]
    allowed = not blocking and drafting_allowed(report.get("internal_status", ""))
    return {
        "status": "PASS" if allowed else "BLOCK",
        "drafting_enabled": allowed,
        "drafting_status": "DRAFT_FOR_COUNSEL_REVIEW" if allowed else "BLOCKED_PENDING_COUNSEL",
        "blocking_components": blocking,
    }

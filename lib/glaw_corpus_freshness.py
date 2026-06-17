"""Shared citation-corpus freshness checks (zero-dependency, stdlib only).

Single source of truth for the corpus-capture staleness ceiling used by the
file gate (``bin/glaw-gate``), the citation gate (``bin/glaw-citation-gate``),
and the corpus tool (``bin/glaw-citation-corpus``). Each caller keeps its own
thin wrapper for its exact failure-message wording; the timestamp parsing,
age computation, and ceiling live here so they cannot drift apart.
"""
from datetime import datetime, timezone

DEFAULT_MAX_AGE_DAYS = 180


def parse_ts(value):
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None."""
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def row_age_days(row):
    """Age of a corpus row in whole days, or None if its ``ts`` is unusable."""
    parsed = parse_ts(str(row.get("ts", "")))
    if not parsed:
        return None
    return (datetime.now(timezone.utc) - parsed).days


def freshness_failure(row, label, *, max_age_days=DEFAULT_MAX_AGE_DAYS, style="prefix"):
    """Return a staleness failure message, or "" if the row is fresh enough.

    ``style="prefix"`` renders ``"<label>: corpus capture ..."`` (file gate and
    corpus tool); ``style="corpus"`` renders ``"corpus <label> capture ..."``
    (citation gate). The wording is preserved verbatim from the original
    per-file implementations.
    """
    age = row_age_days(row)
    if age is None:
        if style == "corpus":
            return f"corpus {label} capture timestamp is missing or invalid"
        return f"{label}: corpus capture timestamp is missing or invalid"
    if age > max_age_days:
        if style == "corpus":
            return f"corpus {label} capture is stale ({age} days old; max {max_age_days})"
        return f"{label}: corpus capture is stale ({age} days old; max {max_age_days})"
    return ""

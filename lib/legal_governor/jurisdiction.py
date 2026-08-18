"""Jurisdiction and forum gate; missing jurisdiction is never inferred."""

REQUIRED = ("governing_law", "forum", "court", "claim_or_task", "choice_of_law_basis")


def validate(record: dict) -> list[str]:
    failures = []
    if not isinstance(record, dict):
        return ["jurisdiction record must be an object"]
    for key in REQUIRED:
        value = record.get(key)
        if value in (None, "", [], {}):
            failures.append(f"jurisdiction.{key} is missing")
    if record.get("forum") and record.get("court") == "unknown":
        failures.append("jurisdiction.court is unknown")
    return failures

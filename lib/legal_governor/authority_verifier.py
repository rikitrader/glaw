"""Source-locked authority validation. This module never fabricates citations."""

REQUIRED = ("proposition", "authority", "jurisdiction", "court", "date", "precedential_status", "rule", "source_url")


def validate(records: list) -> list[str]:
    failures = []
    if not isinstance(records, list) or not records:
        return ["material authority records are missing"]
    for index, row in enumerate(records, start=1):
        if not isinstance(row, dict):
            failures.append(f"authority[{index}] must be an object")
            continue
        for key in REQUIRED:
            if row.get(key) in (None, "", [], {}):
                failures.append(f"authority[{index}].{key} is missing")
        if row.get("precedential_status") == "UNVERIFIED":
            failures.append(f"authority[{index}] is unverified")
    return failures

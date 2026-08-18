"""Citation and quotation provenance gate."""


def validate(records: list) -> list[str]:
    failures = []
    for index, row in enumerate(records or [], start=1):
        if not isinstance(row, dict):
            failures.append(f"citation[{index}] must be an object")
            continue
        for key in ("source_url", "retrieved_at", "proposition", "quotation_status"):
            if row.get(key) in (None, "", [], {}):
                failures.append(f"citation[{index}].{key} is missing")
        if row.get("quotation_status") == "unverified":
            failures.append(f"citation[{index}] quotation is unverified")
    return failures

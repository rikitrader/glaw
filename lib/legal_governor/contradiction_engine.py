"""Cross-document contradiction checks for governing instruments."""


def validate(rows: list) -> list[str]:
    failures = []
    if rows is None:
        return ["conflict matrix is missing"]
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            failures.append(f"conflict[{index}] must be an object")
            continue
        for key in ("document_a", "document_b", "provision_a", "provision_b", "controls", "cure"):
            if row.get(key) in (None, "", [], {}):
                failures.append(f"conflict[{index}].{key} is missing")
    return failures

"""Independent support/adverse authority gate."""


def validate(supporting: list, adverse: list) -> list[str]:
    failures = []
    if not supporting:
        failures.append("supporting authority is missing")
    if not adverse:
        failures.append("independent adverse-authority search is missing")
    for index, row in enumerate(adverse or [], start=1):
        if not isinstance(row, dict) or not row.get("disposition") or not row.get("distinguish_or_rebuttal"):
            failures.append(f"adverse[{index}] requires disposition and distinguish_or_rebuttal")
    return failures

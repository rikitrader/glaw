"""Mandatory-law gate; contracts and client objectives are lower authority."""


def validate(record: dict) -> list[str]:
    failures = []
    if not isinstance(record, dict):
        return ["mandatory_law record must be an object"]
    if record.get("status") not in {"verified", "pass"}:
        failures.append("mandatory-law status is not verified")
    authorities = record.get("authorities")
    if not isinstance(authorities, list) or not authorities:
        failures.append("mandatory-law authorities are missing")
    if record.get("unwaivable_rights") is None:
        failures.append("mandatory-law unwaivable-rights analysis is missing")
    return failures

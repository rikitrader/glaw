"""Required independent adversarial lenses."""

REQUIRED_ROLES = {
    "opposing_shareholder", "minority_investor", "board_member", "creditor",
    "bankruptcy_trustee", "regulator", "plaintiff", "defendant",
    "hostile_acquirer", "court_or_receiver",
}


def validate(record: dict) -> list[str]:
    if not isinstance(record, dict):
        return ["red_team record is missing"]
    roles = set(record.get("completed_roles") or [])
    missing = sorted(REQUIRED_ROLES - roles)
    failures = [f"red-team role not completed: {role}" for role in missing]
    if record.get("surviving_attacks") is None:
        failures.append("red-team surviving_attacks is missing")
    return failures

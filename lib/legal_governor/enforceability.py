"""Contract enforceability and remedy checklist."""

REQUIRED = ("authority", "capacity", "consideration", "definiteness", "formation", "public_policy", "illegality", "equitable_defenses", "remedies")


def validate(record: dict) -> list[str]:
    if not isinstance(record, dict):
        return ["enforceability record is missing"]
    return [f"enforceability.{key} is missing" for key in REQUIRED if record.get(key) in (None, "", [], {})]

"""Shared immunity / exhaustion trigger detection.

Both `risk.py` (numeric MTD scoring) and `rule11_monitor.py` (free-form
viability report) used to carry their own copies of "which defendants trigger
which immunity" predicates. They drifted — qualified-immunity detection used
slightly different rules in each file.

This module centralizes the trigger logic so the two output layers stay in
sync. Callers still format their own output (risk factors vs. viability
issues); they just ask here: "is this immunity exposed in this case?"
"""
from __future__ import annotations

from typing import Iterable


def _is_individual_capacity_officer(defendant: dict) -> bool:
    """True if the defendant is an officer sued in individual capacity.

    Qualified immunity attaches to officers sued in their individual capacity.
    `capacity` may be "individual", "official", "both", or unset. When unset we
    assume individual exposure is possible (default-deny for QI defense).
    """
    if defendant.get("type") != "officer":
        return False
    cap = defendant.get("capacity")
    return cap in (None, "", "individual", "both")


def qualified_immunity_defendants(defendants: Iterable[dict]) -> list[dict]:
    return [d for d in defendants if _is_individual_capacity_officer(d)]


def sovereign_immunity_defendants(defendants: Iterable[dict]) -> list[dict]:
    return [d for d in defendants if d.get("type") == "federal"]


def eleventh_amendment_defendants(defendants: Iterable[dict]) -> list[dict]:
    return [d for d in defendants if d.get("type") == "state"]


def triggered_immunities(meta, defendants: Iterable[dict]) -> dict[str, list[dict]]:
    """Return a mapping of immunity_name -> defendants that trigger it.

    Only returns entries when the claim metadata declares the immunity AND at
    least one defendant is exposed to it.
    """
    defs = list(defendants)
    out: dict[str, list[dict]] = {}
    immunities = getattr(meta, "immunities", []) or []
    if "qualified" in immunities:
        hits = qualified_immunity_defendants(defs)
        if hits:
            out["qualified"] = hits
    if "sovereign" in immunities:
        hits = sovereign_immunity_defendants(defs)
        if hits:
            out["sovereign"] = hits
    if "eleventh_amendment" in immunities:
        hits = eleventh_amendment_defendants(defs)
        if hits:
            out["eleventh_amendment"] = hits
    return out

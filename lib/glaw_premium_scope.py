"""Premium client-lane scope detection for GLAW matters."""
from __future__ import annotations

import re
from typing import Any

PREMIUM_KEYS = (
    "premium_lanes",
    "premium_lane_tags",
    "premium_tags",
    "client_lanes",
    "client_lane_tags",
    "lane_tags",
)

LANE_IDS = {
    "fortune500-enterprise",
    "tax-system",
    "founder-unicorn",
    "founder-governance",
    "founder-control-stack",
    "founder-control-assurance",
    "uhnw-family-office",
}

NEGATIVE_TAGS = {
    "none",
    "no",
    "false",
    "0",
    "ordinary",
    "standard",
    "not-required",
    "not required",
    "no-premium",
    "no premium",
}

ALIASES = {
    "fortune500": "fortune500-enterprise",
    "fortune 500": "fortune500-enterprise",
    "fortune-500": "fortune500-enterprise",
    "enterprise": "fortune500-enterprise",
    "public company": "fortune500-enterprise",
    "public-company": "fortune500-enterprise",
    "public-ready": "fortune500-enterprise",
    "sec reporting": "fortune500-enterprise",
    "tax": "tax-system",
    "tax-system": "tax-system",
    "tax system": "tax-system",
    "irs": "tax-system",
    "tax credits": "tax-system",
    "tax-credit": "tax-system",
    "credits": "tax-system",
    "founder": "founder-unicorn",
    "founder-unicorn": "founder-unicorn",
    "entrepreneur": "founder-unicorn",
    "unicorn": "founder-unicorn",
    "investor": "founder-unicorn",
    "capital raise": "founder-unicorn",
    "capital-raise": "founder-unicorn",
    "qsbs": "founder-unicorn",
    "1202": "founder-unicorn",
    "83b": "founder-unicorn",
    "83(b)": "founder-unicorn",
    "founder governance": "founder-governance",
    "founder-governance": "founder-governance",
    "founder control": "founder-control-stack",
    "founder-control": "founder-control-stack",
    "founder-control-stack": "founder-control-stack",
    "dual class": "founder-control-stack",
    "dual-class": "founder-control-stack",
    "super voting": "founder-control-stack",
    "super-voting": "founder-control-stack",
    "class b": "founder-control-stack",
    "class b stock": "founder-control-stack",
    "meta-style": "founder-control-stack",
    "meta style": "founder-control-stack",
    "founder charter": "founder-control-stack",
    "founder control assurance": "founder-control-assurance",
    "control assurance": "founder-control-assurance",
    "control certificate": "founder-control-assurance",
    "voting universe": "founder-control-assurance",
    "dilution assurance": "founder-control-assurance",
    "moelis": "founder-governance",
    "122(18)": "founder-governance",
    "dgcl 122(18)": "founder-governance",
    "reserved matters": "founder-governance",
    "founder consent": "founder-governance",
    "consent rights": "founder-governance",
    "uhnw": "uhnw-family-office",
    "uhnw-family-office": "uhnw-family-office",
    "family office": "uhnw-family-office",
    "family-office": "uhnw-family-office",
    "trust": "uhnw-family-office",
    "trusts": "uhnw-family-office",
    "dynasty": "uhnw-family-office",
    "investment llc": "uhnw-family-office",
    "estate": "uhnw-family-office",
}


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[_/]+", "-", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _items(value: Any) -> list[str]:
    if value in (None, "", [], {}):
        return []
    if isinstance(value, bool):
        return ["true" if value else "false"]
    if isinstance(value, (list, tuple, set)):
        rows: list[str] = []
        for item in value:
            rows.extend(_items(item))
        return rows
    if isinstance(value, dict):
        rows = []
        for key, item in value.items():
            if isinstance(item, bool):
                if item:
                    rows.append(str(key))
                continue
            if item not in (None, "", [], {}):
                rows.append(str(key))
                rows.extend(_items(item))
        return rows
    text = str(value)
    parts = re.split(r"[,;|]+", text)
    return [part.strip() for part in parts if part.strip()]


def normalize_lane_tag(value: Any) -> str:
    tag = _norm(value)
    if not tag:
        return ""
    if tag in LANE_IDS:
        return tag
    return ALIASES.get(tag, "")


def premium_lane_requirement(intake: dict[str, Any] | None) -> dict[str, Any]:
    intake = intake if isinstance(intake, dict) else {}
    containers = [intake]
    for key in ("universal", "track_specific"):
        value = intake.get(key)
        if isinstance(value, dict):
            containers.append(value)

    raw_tags: list[str] = []
    source_fields: list[str] = []
    for container_index, container in enumerate(containers):
        prefix = "" if container_index == 0 else ("universal." if container_index == 1 else "track_specific.")
        for key in PREMIUM_KEYS:
            if key not in container:
                continue
            values = _items(container.get(key))
            raw_tags.extend(values)
            source_fields.append(f"{prefix}{key}")

    normalized = sorted({normalize_lane_tag(tag) for tag in raw_tags if normalize_lane_tag(tag)})
    negative = bool(raw_tags) and all(_norm(tag) in NEGATIVE_TAGS for tag in raw_tags)
    required = bool(normalized) and not negative
    return {
        "required": required,
        "required_lanes": normalized if required else [],
        "raw_tags": raw_tags,
        "source_fields": source_fields,
        "basis": "explicit_intake_premium_lanes" if required else ("explicit_no_premium_lanes" if negative else "not_tagged"),
    }

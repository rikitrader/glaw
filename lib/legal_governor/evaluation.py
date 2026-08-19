"""Material-error metrics and exact binomial confidence bounds."""
from __future__ import annotations

import math


def wilson_interval(errors: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 1.0)
    p = errors / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return (max(0.0, center - radius), min(1.0, center + radius))


def summarize(rows: list[dict]) -> dict:
    passes = [row for row in rows if row.get("decision") == "PASS"]
    errors = [row for row in passes if row.get("material_error") is True]
    total = len(passes)
    low, high = wilson_interval(len(errors), total)
    return {
        "pass_outputs": total,
        "material_errors_among_pass": len(errors),
        "observed_material_error_rate": len(errors) / total if total else None,
        "wilson_95_ci": {"lower": low, "upper": high},
        "target": 0.03,
        "acceptance": bool(total and high < 0.03),
        "abstention_rate": (len(rows) - total) / len(rows) if rows else None,
    }


def validate_gold_label(row: dict) -> list[str]:
    required = ("id", "domain", "question", "ground_truth_decision", "reviewer", "review_date", "authority")
    return [f"gold.{key} is missing" for key in required if row.get(key) in (None, "", [], {})]


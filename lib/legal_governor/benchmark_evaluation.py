"""Benchmark run validation and coverage-aware material-error evaluation."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from legal_governor import benchmark
from legal_governor.evaluation import wilson_interval


MIN_PASS_OUTPUTS = 2000
MIN_OVERALL_COVERAGE = 0.20
MIN_DOMAIN_COVERAGE = 0.10


def _released(root: Path) -> dict[str, dict]:
    return {row.get("id"): row for row in benchmark.read_jsonl(benchmark.paths(root)["items"]) if row.get("status") == "RELEASED"}


def _summary(rows: list[dict]) -> dict:
    passes = [row for row in rows if row.get("machine_decision") == "PASS"]
    errors = [row for row in passes if row.get("material_error") is True]
    low, high = wilson_interval(len(errors), len(passes))
    return {
        "evaluated": len(rows),
        "pass_outputs": len(passes),
        "material_errors_among_pass": len(errors),
        "observed_material_error_rate": len(errors) / len(passes) if passes else None,
        "wilson_95_ci": {"lower": low, "upper": high},
        "target_upper_bound": 0.03,
        "upper_bound_below_target": bool(passes and high < 0.03),
    }


def evaluate(root: Path, results: list[dict]) -> dict:
    released = _released(root)
    failures = []
    usable = []
    for row in results:
        bid = row.get("benchmark_id")
        item = released.get(bid)
        if not item:
            failures.append(f"result references unreleased benchmark item: {bid}")
            continue
        if row.get("machine_decision") not in benchmark.DECISIONS:
            failures.append(f"{bid} has invalid machine_decision")
            continue
        if not isinstance(row.get("material_error"), bool):
            failures.append(f"{bid} material_error must be boolean")
            continue
        if row.get("split") and row.get("split") != item.get("split"):
            failures.append(f"{bid} result split does not match benchmark split")
            continue
        usable.append({**row, "domain": item.get("domain"), "trap_types": item.get("trap_types", [])})
    if len({row.get("benchmark_id") for row in usable}) != len(usable):
        failures.append("duplicate benchmark results are not allowed")
    overall = _summary(usable)
    domain_results = {}
    released_by_domain = Counter(item.get("domain") for item in released.values())
    for domain, expected in benchmark.DOMAINS:
        rows = [row for row in usable if row.get("domain") == domain]
        summary = _summary(rows)
        summary["released_items"] = released_by_domain[domain]
        summary["coverage"] = len(rows) / released_by_domain[domain] if released_by_domain[domain] else 0.0
        domain_results[domain] = summary
        if rows and summary["coverage"] < MIN_DOMAIN_COVERAGE:
            failures.append(f"{domain} coverage below {MIN_DOMAIN_COVERAGE:.0%}")
    challenge_results = [row for row in usable if row.get("trap_types")]
    challenge_summary = _summary(challenge_results)
    if usable and len(usable) / len(released) < MIN_OVERALL_COVERAGE:
        failures.append(f"overall coverage below {MIN_OVERALL_COVERAGE:.0%}")
    if overall["pass_outputs"] < MIN_PASS_OUTPUTS:
        failures.append(f"PASS outputs below minimum {MIN_PASS_OUTPUTS}")
    if overall["wilson_95_ci"]["upper"] >= 0.03:
        failures.append("95% Wilson upper bound is not below 3%")
    return {
        "status": "PASS" if not failures else "REVIEW_REQUIRED",
        "failures": sorted(set(failures)),
        "overall": overall,
        "by_domain": domain_results,
        "challenge": challenge_summary,
        "released_items": len(released),
        "evaluated_items": len(usable),
    }


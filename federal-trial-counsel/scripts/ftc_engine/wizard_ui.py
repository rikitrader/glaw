"""
Wizard UI primitives — interactive CLI prompt helpers and formatting utilities.

Pure presentation layer: text input, numbered choice menus, multi-select toggles,
yes/no confirmations, date parsing, section banners, and aligned tables.

These helpers are used by every step handler in wizard_steps.py.
"""
from __future__ import annotations

from typing import Optional


# ── Input helpers ───────────────────────────────────────────────────────────

def _prompt(label: str, *, required: bool = False, default: str = "",
            description: str = "") -> str:
    """Prompt user for a single text value."""
    parts = [f"  {label}"]
    if description:
        parts[0] += f" ({description})"
    if default:
        parts[0] += f" [{default}]"
    if not required:
        parts[0] += " (blank to skip)"
    parts[0] += ": "

    while True:
        val = input(parts[0]).strip()
        if not val and default:
            return default
        if not val and required:
            print("    → This field is required.")
            continue
        return val


def _prompt_choice(label: str, choices: list[str], *,
                   description: str = "", default: int = 1) -> str:
    """Prompt user to pick one option from a numbered list."""
    if description:
        print(f"\n  {label} — {description}")
    else:
        print(f"\n  {label}:")
    for i, ch in enumerate(choices, 1):
        marker = "*" if i == default else " "
        print(f"    {marker}{i}. {ch}")
    while True:
        raw = input(f"  Choice [{default}]: ").strip()
        if not raw:
            return choices[default - 1]
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        print(f"    → Enter 1-{len(choices)}")


def _prompt_multi_choice(label: str, choices: list[str], *,
                         preselected: Optional[list[int]] = None) -> list[str]:
    """Prompt user to select multiple items (toggle on/off)."""
    selected = set(preselected or [])
    print(f"\n  {label}:")
    for i, ch in enumerate(choices, 1):
        mark = "X" if i in selected else " "
        print(f"    [{mark}] {i}. {ch}")
    print("  Enter numbers to toggle, 'a' for all, 'done' to confirm:")
    while True:
        raw = input("  > ").strip().lower()
        if raw == "done":
            return [choices[i - 1] for i in sorted(selected)]
        if raw == "a":
            selected = set(range(1, len(choices) + 1))
        elif raw.isdigit() and 1 <= int(raw) <= len(choices):
            n = int(raw)
            selected.symmetric_difference_update({n})
        else:
            print(f"    → Enter 1-{len(choices)}, 'a', or 'done'")
        # Reprint
        for i, ch in enumerate(choices, 1):
            mark = "X" if i in selected else " "
            print(f"    [{mark}] {i}. {ch}")


def _prompt_yes_no(label: str, *, default: bool = False) -> bool:
    """Prompt yes/no question."""
    hint = "Y/n" if default else "y/N"
    raw = input(f"  {label} [{hint}]: ").strip().lower()
    if not raw:
        return default
    return raw.startswith("y")


def _prompt_date(label: str, *, required: bool = False) -> str:
    """Prompt for a date in YYYY-MM-DD format."""
    while True:
        raw = input(f"  {label} (YYYY-MM-DD): ").strip()
        if not raw and not required:
            return ""
        if not raw and required:
            print("    → Date is required.")
            continue
        # Basic validation
        parts = raw.split("-")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            return raw
        print("    → Format: YYYY-MM-DD")


def _print_header(text: str) -> None:
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a simple aligned table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print("  " + fmt.format(*headers))
    print("  " + "  ".join("-" * w for w in widths))
    for row in rows:
        padded = [str(row[i]) if i < len(row) else "" for i in range(len(headers))]
        print("  " + fmt.format(*padded))

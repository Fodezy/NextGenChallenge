"""Task 3: cut daily performance history to a range (rule R5). Pure functions, no I/O.

Windows are inclusive and counted back from `today`: 1D = today - 1 day, 1M = today - 1 month,
YTD = 1 January this year, 1Y = today - 1 year, All = everything. Month and year steps clamp to
the last day of a shorter month (31 March - 1M = 28 February).
"""

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

VALID_RANGES = ("1D", "1M", "YTD", "1Y", "All")

Point = dict[str, Any]


def is_valid_range(value: str) -> bool:
    """Exact, case-sensitive match: "ytd" is invalid, never a silent fallback."""
    return value in VALID_RANGES


def range_start(range_: str, today: date) -> date | None:
    """First date included for `range_`, or None for All."""
    match range_:
        case "1D":
            return today - timedelta(days=1)
        case "1M":
            return _months_back(today, 1)
        case "YTD":
            return date(today.year, 1, 1)
        case "1Y":
            return _months_back(today, 12)
        case "All":
            return None
    raise ValueError(f"Unknown range {range_!r}")


def filter_by_range(points: list[Point], range_: str, today: date) -> list[Point]:
    """Points on or after the range start, oldest first. Never pads missing days."""
    ordered = sorted(points, key=lambda p: p["date"])
    start = range_start(range_, today)
    if start is None:
        return ordered
    return [p for p in ordered if date.fromisoformat(p["date"]) >= start]


def _months_back(day: date, months: int) -> date:
    year, month0 = divmod(day.year * 12 + day.month - 1 - months, 12)
    month = month0 + 1
    return date(year, month, min(day.day, monthrange(year, month)[1]))

"""Rule R5: history ranges, inclusive, counted back from today. Pure function, no HTTP."""

from datetime import date, timedelta

import pytest

from app.services.history_filter import filter_by_range, is_valid_range

TODAY = date(2026, 10, 3)


def make_points(end: date, count: int) -> list[dict]:
    """Daily points ending on `end`, like backend/fixtures/generate-history.mjs."""
    return [
        {"date": (end - timedelta(days=count - 1 - i)).isoformat(), "marketValue": 1000.0 + i}
        for i in range(count)
    ]


P9001 = make_points(TODAY, 401)  # 2025-08-29 .. 2026-10-03
P9002 = make_points(TODAY, 60)


def dates(points: list[dict]) -> list[str]:
    return [p["date"] for p in points]


def test_all_returns_every_point() -> None:
    assert filter_by_range(P9001, "All", TODAY) == P9001


def test_1d_is_yesterday_and_today() -> None:
    assert dates(filter_by_range(P9001, "1D", TODAY)) == ["2026-10-02", "2026-10-03"]


def test_1m_starts_one_month_back_inclusive() -> None:
    result = filter_by_range(P9001, "1M", TODAY)
    assert result[0]["date"] == "2026-09-03"
    assert len(result) == 31


def test_ytd_starts_january_first_not_first_data_point() -> None:
    result = filter_by_range(P9001, "YTD", TODAY)
    assert result[0]["date"] == "2026-01-01"
    assert len(result) == 276
    assert not any(d.startswith("2025") for d in dates(result))


def test_1y_starts_one_year_back_inclusive() -> None:
    result = filter_by_range(P9001, "1Y", TODAY)
    assert result[0]["date"] == "2025-10-03"
    assert len(result) == 366


def test_short_history_returns_what_exists_without_padding() -> None:
    assert filter_by_range(P9002, "1Y", TODAY) == P9002


def test_empty_history_returns_empty_list() -> None:
    assert filter_by_range([], "1Y", TODAY) == []


def test_1m_from_month_end_clamps_to_shorter_month() -> None:
    points = make_points(date(2026, 3, 31), 60)
    assert filter_by_range(points, "1M", date(2026, 3, 31))[0]["date"] == "2026-02-28"


def test_1y_from_leap_day_clamps_to_february_28() -> None:
    points = make_points(date(2028, 2, 29), 400)
    assert filter_by_range(points, "1Y", date(2028, 2, 29))[0]["date"] == "2027-02-28"


def test_unsorted_input_comes_back_oldest_first() -> None:
    shuffled = [P9002[5], P9002[0], P9002[59], P9002[30]]
    assert dates(filter_by_range(shuffled, "All", TODAY)) == sorted(dates(shuffled))


@pytest.mark.parametrize("range_", ["1D", "1M"])
def test_history_entirely_before_window_returns_empty(range_: str) -> None:
    stale = make_points(date(2026, 9, 1), 30)
    assert filter_by_range(stale, range_, TODAY) == []


@pytest.mark.parametrize("value", ["1D", "1M", "YTD", "1Y", "All"])
def test_valid_ranges(value: str) -> None:
    assert is_valid_range(value)


@pytest.mark.parametrize("value", ["2Y", "ytd", "all", "", " 1D"])
def test_invalid_ranges(value: str) -> None:
    assert not is_valid_range(value)

"""GET /portfolios/{id}/performance-history (Task 3, rule R5) through HTTP.

History and today are fixed so counts don't depend on when the fixture was generated.
"""

from collections.abc import Iterator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.data import repository
from app.main import app
from app.routers import history

TODAY = date(2026, 10, 3)
AUTH = {"Authorization": "Bearer superday-demo-token"}


def make_points(end: date, count: int) -> list[dict]:
    return [
        {"date": (end - timedelta(days=count - 1 - i)).isoformat(), "marketValue": 1000.0 + i}
        for i in range(count)
    ]


FAKE_HISTORY = {
    "P-9001": make_points(TODAY, 401),
    "P-9002": make_points(TODAY, 60),
    "P-SINGLE": make_points(date(2026, 9, 1), 30),  # stale: ends a month before TODAY
    "P-EMPTY": [],
}


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(
        repository, "performance_history", lambda pid: list(FAKE_HISTORY.get(pid, []))
    )
    app.dependency_overrides[history.get_today] = lambda: TODAY
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(history.get_today, None)


def get(api: TestClient, portfolio_id: str, **params: str):
    return api.get(f"/portfolios/{portfolio_id}/performance-history", params=params, headers=AUTH)


def test_default_range_is_all_with_camelcase_points_oldest_first(api: TestClient) -> None:
    res = get(api, "P-9001")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 401
    assert body[0] == {"date": "2025-08-29", "marketValue": 1000.0}
    assert [p["date"] for p in body] == sorted(p["date"] for p in body)


def test_ytd_starts_january_first(api: TestClient) -> None:
    body = get(api, "P-9001", range="YTD").json()
    assert body[0]["date"] == "2026-01-01"


def test_1y_on_short_history_returns_all_60_days(api: TestClient) -> None:
    res = get(api, "P-9002", range="1Y")
    assert res.status_code == 200
    assert len(res.json()) == 60


def test_empty_portfolio_returns_empty_list(api: TestClient) -> None:
    res = get(api, "P-EMPTY")
    assert res.status_code == 200
    assert res.json() == []


def test_no_points_in_window_returns_empty_list(api: TestClient) -> None:
    res = get(api, "P-SINGLE", range="1D")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.parametrize("value", ["2Y", "ytd", ""])
def test_invalid_range_is_400(api: TestClient, value: str) -> None:
    res = get(api, "P-9001", range=value)
    assert res.status_code == 400
    body = res.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "invalid_range"


def test_unknown_portfolio_is_404(api: TestClient) -> None:
    res = get(api, "UNKNOWN")
    assert res.status_code == 404
    assert res.json()["error"] == "not_found"


def test_invalid_range_checked_before_portfolio_lookup(api: TestClient) -> None:
    res = get(api, "UNKNOWN", range="2Y")
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_range"

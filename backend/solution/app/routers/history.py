"""GET /portfolios/{id}/performance-history (Task 3). Owner: partner B.

Order of checks: range (400 invalid_range), then portfolio (404 not_found), then filter.
"""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query

from app.data import repository
from app.errors import ApiError
from app.schemas import HistoryPoint
from app.services import history_filter

router = APIRouter(tags=["history"])


def get_today() -> date:
    """Today in UTC (the history fixture uses UTC dates). Overridden in tests."""
    return datetime.now(UTC).date()


@router.get("/portfolios/{portfolio_id}/performance-history", response_model=list[HistoryPoint])
async def performance_history(
    portfolio_id: str,
    range_: str = Query("All", alias="range", description="1D, 1M, YTD, 1Y or All"),
    today: date = Depends(get_today),
) -> list[HistoryPoint]:
    if not history_filter.is_valid_range(range_):
        allowed = ", ".join(history_filter.VALID_RANGES)
        raise ApiError(400, "invalid_range", f"range must be one of {allowed}; got {range_!r}")
    if repository.get_portfolio(portfolio_id) is None:
        raise ApiError(404, "not_found", f"Portfolio {portfolio_id} not found")

    points = history_filter.filter_by_range(
        repository.performance_history(portfolio_id), range_, today
    )
    return [HistoryPoint(date=p["date"], market_value=round(p["marketValue"], 2)) for p in points]

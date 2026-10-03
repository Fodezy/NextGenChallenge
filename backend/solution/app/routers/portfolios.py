"""Task 1 · GET /portfolios/{id}: portfolio metadata from the CRM (owner: me)."""

from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas import ErrorResponse, PortfolioMetadata, PortfolioResponse
from app.services.crm_client import fetch_raw, get_crm_http
from app.services.crm_mapper import map_portfolio

router = APIRouter(tags=["portfolios"])

_MONEY_FIELDS = ("total_market_value", "day_change_amount")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def to_response(meta: PortfolioMetadata, *, stale: bool, cached_at: str) -> PortfolioResponse:
    """Money rounded to cents here, at the edge; percentages stay unrounded (BRIEF.md §7)."""
    data = meta.model_dump()
    for field in _MONEY_FIELDS:
        if data[field] is not None:
            data[field] = round(data[field], 2)
    return PortfolioResponse(**data, stale=stale, cached_at=cached_at)


@router.get(
    "/portfolios/{portfolio_id}",
    response_model=PortfolioResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def get_portfolio(
    portfolio_id: str, http: httpx.AsyncClient = Depends(get_crm_http)
) -> PortfolioResponse:
    raw = await fetch_raw(http, portfolio_id, deadline_s=get_settings().crm_timeout_seconds)
    fetched_at = _now_iso()
    return to_response(map_portfolio(raw, portfolio_id), stale=False, cached_at=fetched_at)

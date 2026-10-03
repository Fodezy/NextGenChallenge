"""Tasks 1 and 9 · GET /portfolios/{id}: CRM metadata behind a TTL cache (owner: me)."""

import logging
from datetime import UTC, datetime
from functools import lru_cache

import httpx
from fastapi import APIRouter, Depends

from app.config import get_settings
from app.schemas import ErrorResponse, PortfolioMetadata, PortfolioResponse
from app.services.cache import TtlCache
from app.services.crm_client import fetch_raw, get_crm_http
from app.services.crm_errors import CrmNotFoundError, CrmUnavailableError
from app.services.crm_mapper import map_portfolio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["portfolios"])

_MONEY_FIELDS = ("total_market_value", "day_change_amount")


@lru_cache
def get_portfolio_cache() -> TtlCache:
    """FastAPI dependency: one cache for the app's lifetime; tests override it."""
    return TtlCache(ttl_seconds=get_settings().cache_ttl_seconds)


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


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
    portfolio_id: str,
    http: httpx.AsyncClient = Depends(get_crm_http),
    cache: TtlCache = Depends(get_portfolio_cache),
) -> PortfolioResponse:
    """Fresh copy → no CRM call. Else ask the CRM: success replaces the copy (A7); a failure
    falls back to any older copy as stale, or 503 with none; a 404 removes the copy (A12)."""
    fresh = cache.get_fresh(portfolio_id)
    if fresh is not None:
        return to_response(fresh.value, stale=False, cached_at=_iso(fresh.stored_at))

    try:
        raw = await fetch_raw(http, portfolio_id, deadline_s=get_settings().crm_timeout_seconds)
        meta = map_portfolio(raw, portfolio_id)
    except CrmNotFoundError:
        cache.delete(portfolio_id)
        raise
    except CrmUnavailableError as exc:
        fallback = cache.get_any(portfolio_id)
        if fallback is None:
            raise
        logger.warning("Serving stale %s from %s: %s", portfolio_id, fallback.stored_at, exc)
        return to_response(fallback.value, stale=True, cached_at=_iso(fallback.stored_at))

    entry = cache.set(portfolio_id, meta)
    return to_response(meta, stale=False, cached_at=_iso(entry.stored_at))

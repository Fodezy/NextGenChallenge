"""Calls the mock CRM (BRIEF.md R2): one GET, a hard deadline, every failure a clear error."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import quote

import httpx

from app.config import get_settings
from app.services.crm_errors import CrmNotFoundError, CrmUnavailableError

_shared: httpx.AsyncClient | None = None


async def get_crm_http() -> AsyncIterator[httpx.AsyncClient]:
    """FastAPI dependency; tests override it with a client on an httpx.MockTransport.

    One client for the app's lifetime: building a client per request costs ~200 ms (SSL
    context, no connection reuse).
    """
    global _shared
    if _shared is None:
        settings = get_settings()
        _shared = httpx.AsyncClient(
            base_url=settings.crm_base_url, timeout=settings.crm_timeout_seconds
        )
    yield _shared


async def close_crm_http() -> None:
    global _shared
    if _shared is not None:
        await _shared.aclose()
        _shared = None


async def fetch_raw(http: httpx.AsyncClient, portfolio_id: str, *, deadline_s: float) -> Any:
    """Return the CRM's JSON body for one portfolio.

    httpx's timeout is per phase (connect, each read), so a CRM that drips bytes could outlast
    it; asyncio.timeout caps the whole call.
    """
    path = f"/crm/portfolios/{quote(portfolio_id, safe='')}"
    try:
        async with asyncio.timeout(deadline_s):
            response = await http.get(path)
    except TimeoutError as exc:
        raise CrmUnavailableError(f"CRM did not answer within {deadline_s:g} s") from exc
    except httpx.HTTPError as exc:
        raise CrmUnavailableError(f"CRM request failed ({type(exc).__name__})") from exc

    if response.status_code == 404:
        raise CrmNotFoundError(portfolio_id)
    if response.status_code != 200:
        raise CrmUnavailableError(f"CRM returned HTTP {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise CrmUnavailableError("CRM returned a non-JSON response") from exc

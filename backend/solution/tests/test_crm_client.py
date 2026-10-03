"""Task 1 · R2: call the CRM, never hang, turn every failure into a clear error."""

import asyncio
import time

import httpx
import pytest

from app.services.crm_client import fetch_raw
from app.services.crm_errors import CrmNotFoundError, CrmUnavailableError
from tests.crm_fakes import crm_payload, fake_http, ok_handler, slow_handler, status_handler


async def _fetch(handler, portfolio_id: str = "P-9001", deadline_s: float = 2.0):
    async with fake_http(handler) as http:
        return await fetch_raw(http, portfolio_id, deadline_s=deadline_s)


def test_200_returns_the_raw_body():
    assert asyncio.run(_fetch(ok_handler())) == crm_payload("P-9001")


def test_calls_crm_portfolio_path_without_mode_query():
    seen: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=crm_payload("P-9001"))

    asyncio.run(_fetch(handle))

    assert seen[0].method == "GET"
    assert seen[0].url.path == "/crm/portfolios/P-9001"
    assert seen[0].url.query == b""


def test_id_is_url_encoded_in_the_path():
    seen: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(404, json={})

    with pytest.raises(CrmNotFoundError):
        asyncio.run(_fetch(handle, "a/b c"))

    assert seen[0].url.raw_path == b"/crm/portfolios/a%2Fb%20c"


def test_crm_404_raises_not_found():
    with pytest.raises(CrmNotFoundError):
        asyncio.run(_fetch(ok_handler(), "P-NOPE"))


@pytest.mark.parametrize("status", [500, 502, 503, 504, 400])
def test_crm_error_status_raises_unavailable(status):
    with pytest.raises(CrmUnavailableError):
        asyncio.run(_fetch(status_handler(status)))


def test_connection_refused_raises_unavailable():
    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(CrmUnavailableError):
        asyncio.run(_fetch(handle))


def test_slow_crm_gives_up_at_the_deadline():
    started = time.perf_counter()

    with pytest.raises(CrmUnavailableError):
        asyncio.run(_fetch(slow_handler(10), deadline_s=0.2))

    assert time.perf_counter() - started < 1.0


def test_non_json_200_raises_unavailable():
    def handle(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>maintenance</html>")

    with pytest.raises(CrmUnavailableError):
        asyncio.run(_fetch(handle))

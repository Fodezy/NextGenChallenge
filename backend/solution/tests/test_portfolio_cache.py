"""Task 9 · R8, A7: GET /portfolios/{id} with the cache, a counting fake CRM and a fake clock."""

import asyncio
import time
from collections.abc import Iterator
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.routers.portfolios import get_portfolio_cache
from app.services.cache import TtlCache
from app.services.crm_client import get_crm_http
from tests.crm_fakes import crm_payload, fake_http
from tests.fake_clock import FakeClock

T0 = "2026-10-03T10:00:00.000Z"


class SwitchableCrm:
    """A fake CRM whose behaviour tests switch between calls, counting every call."""

    def __init__(self) -> None:
        self.mode = "ok"
        self.calls = 0
        self.amount = 48930

    async def handle(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        portfolio_id = request.url.path.rsplit("/", 1)[-1]
        if self.mode == "error":
            return httpx.Response(503, json={"error": "legacy_unavailable", "message": "down"})
        if self.mode == "slow":
            await asyncio.sleep(10)
            return httpx.Response(504, json={})
        if self.mode == "garbage":
            return httpx.Response(200, json={"unexpected": True})
        if self.mode == "notfound" or portfolio_id not in ("P-9001", "P-9002"):
            return httpx.Response(404, json={"error": "unknown_account", "message": "none"})
        body = crm_payload(portfolio_id)
        for account in body["client_record"]["accounts"]:
            if account["acct_ref"] == "P-9001":
                account["curr_val"]["amt"] = self.amount
        return httpx.Response(200, json=body)


@pytest.fixture
def env() -> SimpleNamespace:
    clock = FakeClock()
    crm = SwitchableCrm()
    cache = TtlCache(ttl_seconds=30, clock=clock)

    async def http_override():
        async with fake_http(crm.handle) as http:
            yield http

    app = create_app()
    app.dependency_overrides[get_crm_http] = http_override
    app.dependency_overrides[get_portfolio_cache] = lambda: cache
    return SimpleNamespace(client=TestClient(app), clock=clock, crm=crm)


@pytest.fixture
def short_deadline(monkeypatch) -> Iterator[None]:
    monkeypatch.setenv("CRM_TIMEOUT_SECONDS", "0.2")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _get(env, portfolio_id: str = "P-9001"):
    return env.client.get(f"/portfolios/{portfolio_id}")


def test_two_requests_within_the_ttl_call_the_crm_once(env):
    first = _get(env)
    env.clock.advance(29)
    second = _get(env)

    assert env.crm.calls == 1
    assert first.status_code == second.status_code == 200
    assert second.json()["stale"] is False
    assert second.json()["cachedAt"] == first.json()["cachedAt"] == T0


def test_after_the_ttl_a_working_crm_is_called_again_and_cached_at_moves(env):
    _get(env)
    env.clock.advance(31)
    env.crm.amount = 50000

    res = _get(env)

    assert env.crm.calls == 2
    assert res.json()["stale"] is False
    assert res.json()["cachedAt"] == "2026-10-03T10:00:31.000Z"
    assert res.json()["totalMarketValue"] == 50000


def test_after_the_ttl_a_crm_outage_serves_the_cached_copy_as_stale(env):
    fresh = _get(env).json()
    env.clock.advance(31)
    env.crm.mode = "error"

    res = _get(env)

    assert res.status_code == 200
    body = res.json()
    assert body["stale"] is True
    assert body["cachedAt"] == T0
    assert {k: v for k, v in body.items() if k != "stale"} == {
        k: v for k, v in fresh.items() if k != "stale"
    }


def test_after_the_ttl_a_slow_crm_serves_stale_within_the_deadline(env, short_deadline):
    _get(env)
    env.clock.advance(31)
    env.crm.mode = "slow"
    started = time.perf_counter()

    res = _get(env)

    assert res.status_code == 200
    assert res.json()["stale"] is True
    assert time.perf_counter() - started < 1.5


def test_after_the_ttl_an_unreadable_crm_response_serves_stale(env):
    _get(env)
    env.clock.advance(31)
    env.crm.mode = "garbage"

    res = _get(env)

    assert res.status_code == 200
    assert res.json()["stale"] is True


def test_cold_cache_and_crm_failure_returns_503(env):
    env.crm.mode = "error"

    res = _get(env)

    assert res.status_code == 503
    assert res.json() == {"error": "crm_unavailable", "message": res.json()["message"]}


def test_recovery_after_stale_replaces_the_copy_and_clears_stale(env):
    _get(env)
    env.clock.advance(31)
    env.crm.mode = "error"
    assert _get(env).json()["stale"] is True

    env.crm.mode = "ok"
    env.crm.amount = 51000
    recovered = _get(env).json()
    assert recovered["stale"] is False
    assert recovered["cachedAt"] == "2026-10-03T10:00:31.000Z"

    env.clock.advance(31)
    env.crm.mode = "error"
    later = _get(env).json()
    assert later["stale"] is True
    assert later["cachedAt"] == "2026-10-03T10:00:31.000Z"
    assert later["totalMarketValue"] == 51000


def test_one_portfolios_copy_is_never_served_for_another(env):
    _get(env, "P-9001")
    env.crm.mode = "error"

    res = _get(env, "P-9002")

    assert res.status_code == 503
    assert res.json()["error"] == "crm_unavailable"


def test_crm_404_is_not_cached_and_removes_an_old_copy(env):
    _get(env)
    env.clock.advance(31)
    env.crm.mode = "notfound"
    assert _get(env).status_code == 404

    env.crm.mode = "error"
    res = _get(env)

    assert res.status_code == 503
    assert env.crm.calls == 3


def test_unknown_id_is_not_cached(env):
    assert _get(env, "P-NOPE").status_code == 404
    assert _get(env, "P-NOPE").status_code == 404

    assert env.crm.calls == 2


def test_production_cache_dependency_uses_the_configured_ttl():
    cache = get_portfolio_cache()

    assert isinstance(cache, TtlCache)
    assert cache.ttl_seconds == get_settings().cache_ttl_seconds
    assert get_portfolio_cache() is cache

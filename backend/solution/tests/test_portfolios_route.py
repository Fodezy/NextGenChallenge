"""Task 1 · GET /portfolios/{id}: the endpoint end to end, against a fake CRM."""

import time
from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.routers.portfolios import get_portfolio_cache
from app.services.cache import TtlCache
from app.services.crm_client import get_crm_http
from tests.crm_fakes import RETRIEVED_AT, fake_http, ok_handler, slow_handler, status_handler

FIELDS = {
    "portfolioId",
    "clientId",
    "label",
    "currency",
    "totalMarketValue",
    "dayChangeAmount",
    "dayChangePercent",
    "totalReturnSinceInception",
    "asOf",
    "stale",
    "cachedAt",
}


@pytest.fixture
def crm():
    """Set crm(handler) to choose how the fake CRM answers; the app gets a fresh client per call."""
    state = {"handler": ok_handler()}

    async def override():
        async with fake_http(state["handler"]) as http:
            yield http

    app = create_app()
    app.dependency_overrides[get_crm_http] = override
    # Task 1 tests every request against the CRM: an empty cache per request, so no test sees
    # another's cached copy. Caching itself is tested in test_portfolio_cache.py.
    app.dependency_overrides[get_portfolio_cache] = lambda: TtlCache(ttl_seconds=30)

    def use(handler) -> TestClient:
        state["handler"] = handler
        return TestClient(app)

    return use


@pytest.fixture
def short_deadline(monkeypatch) -> Iterator[None]:
    monkeypatch.setenv("CRM_TIMEOUT_SECONDS", "0.2")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_200_returns_camelcase_body_with_stale_false_and_cached_at(crm):
    res = crm(ok_handler()).get("/portfolios/P-9001")

    assert res.status_code == 200
    body = res.json()
    assert set(body) == FIELDS
    assert body["portfolioId"] == "P-9001"
    assert body["label"] == "Taxable Brokerage"
    assert body["totalMarketValue"] == 48930
    assert body["asOf"] == RETRIEVED_AT
    assert body["stale"] is False
    assert datetime.fromisoformat(body["cachedAt"]).tzinfo is not None


def test_nested_crm_shape_gives_the_same_body(crm):
    ok = crm(ok_handler()).get("/portfolios/P-9001").json()
    nested = crm(ok_handler("nested")).get("/portfolios/P-9001").json()

    for key in FIELDS - {"cachedAt"}:
        assert nested[key] == ok[key], key


def test_missing_crm_fields_return_200_with_nulls(crm):
    res = crm(ok_handler("missing")).get("/portfolios/P-9001")

    assert res.status_code == 200
    assert res.json()["totalMarketValue"] is None
    assert res.json()["label"] is None


def test_unknown_id_returns_404_flat_error(crm):
    res = crm(ok_handler()).get("/portfolios/P-NOPE")

    assert res.status_code == 404
    assert res.json()["error"] == "not_found"
    assert set(res.json()) == {"error", "message"}


def test_crm_outage_returns_503_flat_error(crm):
    res = crm(status_handler(503)).get("/portfolios/P-9001")

    assert res.status_code == 503
    assert res.json()["error"] == "crm_unavailable"
    assert set(res.json()) == {"error", "message"}


def test_slow_crm_returns_503_within_the_deadline(crm, short_deadline):
    client = crm(slow_handler(10))
    started = time.perf_counter()

    res = client.get("/portfolios/P-9001")

    assert res.status_code == 503
    assert res.json()["error"] == "crm_unavailable"
    assert time.perf_counter() - started < 1.5

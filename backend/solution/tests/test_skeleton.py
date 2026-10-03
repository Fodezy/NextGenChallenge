from pathlib import Path

import pytest
from fastapi import Query
from fastapi.testclient import TestClient

from app.data import repository
from app.main import create_app


def test_health_ok(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_unknown_route_is_flat_404(client: TestClient) -> None:
    res = client.get("/does-not-exist")
    assert res.status_code == 404
    body = res.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "not_found"


def test_wrong_method_is_flat_405(client: TestClient) -> None:
    res = client.post("/health")
    assert res.status_code == 405
    assert res.json()["error"] == "method_not_allowed"


def test_validation_error_is_flat_400() -> None:
    app = create_app()

    @app.get("/test-validation")
    async def _route(n: int = Query()) -> dict[str, int]:
        return {"n": n}

    with TestClient(app) as c:
        res = c.get("/test-validation", params={"n": "abc"})
    assert res.status_code == 400
    body = res.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "invalid_request"
    assert "detail" not in body


def test_unhandled_exception_is_flat_500() -> None:
    app = create_app()

    @app.get("/test-crash")
    async def _route() -> None:
        raise RuntimeError("secret internals")

    with TestClient(app, raise_server_exceptions=False) as c:
        res = c.get("/test-crash")
    assert res.status_code == 500
    assert res.json() == {"error": "internal_error", "message": "Internal server error"}


def test_repository_loads_p9001() -> None:
    portfolio = repository.get_portfolio("P-9001")
    assert portfolio is not None
    assert portfolio["clientId"] == "abc123"
    holdings = repository.list_holdings("P-9001")
    assert len(holdings) == 3
    assert [h["ticker"] for h in holdings] == ["AAPL", "BND", "ZERO"]
    assert repository.get_portfolio("UNKNOWN") is None
    assert repository.cad_to_usd() == 0.73


def test_history_missing_file_returns_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(repository, "HISTORY_PATH", tmp_path / "missing.json")
    repository.reload()
    try:
        assert repository.performance_history("P-9001") == []
    finally:
        monkeypatch.undo()
        repository.reload()

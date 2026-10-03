"""Task 2 HTTP contract, separate from pure calculation tests."""

import pytest
from fastapi.testclient import TestClient

from app.data import repository

AUTH = {"Authorization": "Bearer superday-demo-token"}


def test_valid_portfolio_has_complete_camelcase_numbers(client: TestClient) -> None:
    response = client.get("/portfolios/P-9001/holdings", headers=AUTH)
    assert response.status_code == 200
    rows = response.json()
    assert [row["ticker"] for row in rows] == ["AAPL", "BND", "ZERO"]
    assert rows[0] == {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "assetClass": "Equity",
        "quantity": 120,
        "costBasisPerShare": 200,
        "price": 227.5,
        "previousClosePrice": 225,
        "marketValue": 27300,
        "weightPercent": pytest.approx(27300 / 48930),
        "unrealizedGainLoss": 3300,
        "dayChangeAmount": 300,
        "dayChangePercent": pytest.approx(2.5 / 225),
    }
    assert rows[1]["unrealizedGainLoss"] == -570
    assert rows[1]["dayChangeAmount"] == -270
    assert all(
        isinstance(value, (int, float))
        for key, value in rows[0].items()
        if key not in {"ticker", "name", "assetClass"}
    )


def test_empty_portfolio_returns_empty_array(client: TestClient) -> None:
    response = client.get("/portfolios/P-EMPTY/holdings", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == []


def test_closed_position_has_zero_calculated_fields(client: TestClient) -> None:
    closed = client.get("/portfolios/P-9001/holdings", headers=AUTH).json()[2]
    for field in (
        "marketValue",
        "weightPercent",
        "unrealizedGainLoss",
        "dayChangeAmount",
        "dayChangePercent",
    ):
        assert closed[field] == 0


def test_zero_previous_close_returns_null_percentage(client: TestClient) -> None:
    response = client.get("/portfolios/P-9002/holdings", headers=AUTH)
    assert response.status_code == 200
    row = response.json()[0]
    assert row["dayChangePercent"] is None
    assert row["dayChangeAmount"] == 500
    assert row["weightPercent"] == 1


def test_unknown_portfolio_returns_flat_404(client: TestClient) -> None:
    response = client.get("/portfolios/UNKNOWN/holdings", headers=AUTH)
    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "message": "Portfolio UNKNOWN not found"}


def test_refresh_recalculates_from_latest_rows(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    rows = repository.list_holdings("P-SINGLE")
    rows[0].update(quantity=3, price=0.105, previousClosePrice=0.1, costBasisPerShare=0.08)
    monkeypatch.setattr(repository, "list_holdings", lambda _: rows)
    response = client.get("/portfolios/P-SINGLE/holdings", headers=AUTH)
    assert response.status_code == 200
    row = response.json()[0]
    assert row["marketValue"] == 0.32
    assert row["unrealizedGainLoss"] == 0.08
    assert row["dayChangeAmount"] == 0.02
    assert row["dayChangePercent"] == pytest.approx(0.05)
    rows[0]["quantity"] = 6
    assert (
        client.get("/portfolios/P-SINGLE/holdings", headers=AUTH).json()[0]["marketValue"] == 0.63
    )

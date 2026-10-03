"""GET /portfolios/{id}/allocation (Task 5, rule R6) through HTTP, on the real seed data."""

import pytest
from fastapi.testclient import TestClient

AUTH = {"Authorization": "Bearer superday-demo-token"}


def get(client: TestClient, portfolio_id: str):
    return client.get(f"/portfolios/{portfolio_id}/allocation", headers=AUTH)


def test_p9001_returns_two_classes_in_camel_case(client: TestClient) -> None:
    response = get(client, "P-9001")

    assert response.status_code == 200
    body = response.json()
    assert [e["assetClass"] for e in body] == ["Equity", "Fixed Income"]
    assert body[0]["value"] == 27300.00
    assert body[0]["percent"] == pytest.approx(0.557940, abs=1e-6)
    assert body[1]["value"] == 21630.00
    assert body[1]["percent"] == pytest.approx(0.442060, abs=1e-6)
    assert set(body[0]) == {"assetClass", "value", "percent"}


def test_p_single_is_one_entry_with_percent_one(client: TestClient) -> None:
    response = get(client, "P-SINGLE")

    assert response.status_code == 200
    assert response.json() == [{"assetClass": "Equity", "value": 2275.00, "percent": 1.0}]


def test_p_empty_is_200_with_empty_list_not_404(client: TestClient) -> None:
    response = get(client, "P-EMPTY")

    assert response.status_code == 200
    assert response.json() == []


def test_p9002_new_security_is_valued_at_quantity_times_price(client: TestClient) -> None:
    # NEW: 10 x 50, previous close 0 must not affect allocation
    response = get(client, "P-9002")

    assert response.json() == [{"assetClass": "Equity", "value": 500.00, "percent": 1.0}]


def test_unknown_portfolio_is_404_with_flat_error(client: TestClient) -> None:
    response = get(client, "P-NOPE")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
    assert "message" in response.json()


def _row(asset_class: str, quantity: float, price: float) -> dict:
    return {
        "assetClass": asset_class,
        "quantity": quantity,
        "costBasisPerShare": price,
        "price": price,
        "previousClosePrice": price,
    }


def test_value_is_rounded_to_two_decimals_in_the_response(client: TestClient, monkeypatch) -> None:
    from app.data import repository

    monkeypatch.setattr(
        repository,
        "list_holdings",
        lambda pid: [
            _row("Equity", 3, 33.333),
            _row("Fixed Income", 1, 10),
        ],
    )

    body = get(client, "P-9001").json()

    assert body[0]["value"] == 100.0  # 99.999 -> 2 dp
    assert body[0]["percent"] == pytest.approx(99.999 / 109.999, abs=1e-9)  # percent unrounded

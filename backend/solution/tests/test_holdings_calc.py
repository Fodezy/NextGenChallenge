"""Task 2: examples from BRIEF.md R3/R4, independent of HTTP."""

from copy import deepcopy
from decimal import Decimal

from app.data import repository
from app.services.holdings_calc import calculate_holdings


def test_aapl_values_and_weight() -> None:
    rows = calculate_holdings(repository.list_holdings("P-9001"))
    apple = rows[0]
    assert apple["marketValue"] == Decimal("27300")
    assert apple["unrealizedGainLoss"] == Decimal("3300")
    assert apple["dayChangeAmount"] == Decimal("300")
    assert apple["dayChangePercent"] == Decimal("2.5") / Decimal("225")
    assert apple["weightPercent"] == Decimal("27300") / Decimal("48930")


def test_bond_negative_values_and_weight() -> None:
    bond = calculate_holdings(repository.list_holdings("P-9001"))[1]
    assert bond["marketValue"] == Decimal("21630")
    assert bond["unrealizedGainLoss"] == Decimal("-570")
    assert bond["dayChangeAmount"] == Decimal("-270")
    assert bond["dayChangePercent"] == Decimal("-0.9") / Decimal("73")
    assert bond["weightPercent"] == Decimal("21630") / Decimal("48930")


def test_closed_position_all_calculated_fields_zero() -> None:
    closed = calculate_holdings(repository.list_holdings("P-9001"))[2]
    for key in (
        "marketValue",
        "weightPercent",
        "unrealizedGainLoss",
        "dayChangeAmount",
        "dayChangePercent",
    ):
        assert closed[key] == Decimal("0")


def test_zero_previous_close_keeps_amount_and_unknown_percent() -> None:
    new = calculate_holdings(repository.list_holdings("P-9002"))[0]
    assert new["marketValue"] == Decimal("500")
    assert new["unrealizedGainLoss"] == Decimal("100")
    assert new["dayChangeAmount"] == Decimal("500")
    assert new["dayChangePercent"] is None
    assert new["weightPercent"] == Decimal("1")


def test_empty_portfolio() -> None:
    assert calculate_holdings([]) == []


def test_zero_total_has_zero_weights() -> None:
    rows = repository.list_holdings("P-9001")
    for row in rows:
        row["quantity"] = 0
    calculated = calculate_holdings(rows)
    assert all(row["weightPercent"] == 0 for row in calculated)


def test_preserves_input_and_does_not_round_money_early() -> None:
    rows = repository.list_holdings("P-SINGLE")
    rows[0].update(quantity=3, price=0.105, previousClosePrice=0.1, costBasisPerShare=0.08)
    original = deepcopy(rows)
    result = calculate_holdings(rows)
    assert rows == original
    assert result[0]["ticker"] == "AAPL"
    assert result[0]["marketValue"] == Decimal("0.315")
    assert result[0]["dayChangeAmount"] == Decimal("0.015")
    assert result[0]["unrealizedGainLoss"] == Decimal("0.075")

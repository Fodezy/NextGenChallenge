"""Rule R6: allocation by asset class. Pure function, no HTTP.

`allocate(holdings)` takes seed-shaped holdings and values them with partner A's
`calculate_holdings` (Task 2). It returns [{"assetClass", "value", "percent"}] in first-appearance
order, as unrounded Decimals; rounding to 2 dp happens when the response is built. A13-A16.
"""

import pytest

from app.services.allocation import allocate as _allocate


def allocate(holdings: list[dict]) -> list[dict]:
    """Decimals to floats so results compare with pytest.approx."""
    return [
        {"assetClass": r["assetClass"], "value": float(r["value"]), "percent": float(r["percent"])}
        for r in _allocate(holdings)
    ]


def holding(asset_class: str, quantity: float, price: float, ticker: str = "T") -> dict:
    return {
        "ticker": ticker,
        "assetClass": asset_class,
        "quantity": quantity,
        "costBasisPerShare": price,
        "price": price,
        "previousClosePrice": price,
    }


# P-9001 from seed.json: AAPL 120 x 227.50, BND 300 x 72.10, ZERO 0 x 12
P9001 = [
    holding("Equity", 120, 227.5, "AAPL"),
    holding("Fixed Income", 300, 72.1, "BND"),
    holding("Equity", 0, 12, "ZERO"),
]


def test_multi_class_values_and_percents_match_the_spec_example() -> None:
    result = allocate(P9001)

    assert [r["assetClass"] for r in result] == ["Equity", "Fixed Income"]
    assert result[0]["value"] == pytest.approx(27300.00)
    assert result[0]["percent"] == pytest.approx(0.557940, abs=1e-6)
    assert result[1]["value"] == pytest.approx(21630.00)
    assert result[1]["percent"] == pytest.approx(0.442060, abs=1e-6)


def test_holdings_in_the_same_class_are_summed_into_one_entry() -> None:
    result = allocate([holding("Equity", 10, 100), holding("Equity", 5, 20)])

    assert len(result) == 1
    assert result[0]["value"] == pytest.approx(1100.00)


def test_percents_add_up_to_one() -> None:
    result = allocate(P9001)

    assert sum(r["percent"] for r in result) == pytest.approx(1.0)


def test_single_asset_class_is_one_entry_with_percent_one() -> None:
    # P-SINGLE: AAPL 10 x 227.50
    result = allocate([holding("Equity", 10, 227.5, "AAPL")])

    assert result == [{"assetClass": "Equity", "value": pytest.approx(2275.00), "percent": 1.0}]


def test_no_holdings_returns_empty_list() -> None:
    assert allocate([]) == []


def test_zero_quantity_row_stays_in_its_class_with_value_zero() -> None:
    """A5: ZERO is kept in P-9001's Equity; a class made only of zero rows still appears."""
    only_zero = allocate([holding("Equity", 0, 12, "ZERO"), holding("Cash", 100, 1)])

    by_class = {r["assetClass"]: r for r in only_zero}
    assert by_class["Equity"]["value"] == 0
    assert by_class["Equity"]["percent"] == 0
    assert by_class["Cash"]["percent"] == pytest.approx(1.0)


def test_total_zero_gives_zero_percents_not_a_division_error() -> None:
    """A15: holdings exist but everything is worth 0."""
    result = allocate([holding("Equity", 0, 12), holding("Fixed Income", 0, 72)])

    assert [(r["assetClass"], r["value"], r["percent"]) for r in result] == [
        ("Equity", 0, 0),
        ("Fixed Income", 0, 0),
    ]


def test_only_classes_present_are_returned() -> None:
    """A14: no zero-filled Cash / Alternatives entries."""
    result = allocate(P9001)

    assert {r["assetClass"] for r in result} == {"Equity", "Fixed Income"}


def test_asset_classes_differing_only_by_case_are_separate_entries() -> None:
    """A16: exact, case-sensitive match. No normalising, so bad data stays visible."""
    result = allocate([holding("Equity", 1, 100), holding("equity", 1, 50)])

    assert [r["assetClass"] for r in result] == ["Equity", "equity"]
    assert [r["value"] for r in result] == [100, 50]


def test_order_is_first_appearance_not_sorted_by_value() -> None:
    result = allocate([holding("Cash", 1, 10), holding("Equity", 1, 1000), holding("Cash", 1, 5)])

    assert [r["assetClass"] for r in result] == ["Cash", "Equity"]


def test_percent_is_not_rounded() -> None:
    result = allocate([holding("Equity", 1, 1), holding("Fixed Income", 2, 1)])

    assert result[0]["percent"] == pytest.approx(1 / 3, abs=1e-12)


def test_does_not_mutate_its_input() -> None:
    holdings = [dict(h) for h in P9001]

    allocate(holdings)

    assert holdings == P9001

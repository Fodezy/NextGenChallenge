"""Task 5: allocation by asset class (BRIEF.md R6).

Values come from Task 2's `calculate_holdings`. Money stays Decimal and unrounded here; the router
rounds when it builds the response. Percentages are fractions (0.5579 = 55.79%).
"""

from collections.abc import Sequence
from decimal import Decimal

from app.data.repository import Record
from app.services.holdings_calc import calculate_holdings


def allocate(holdings: Sequence[Record]) -> list[Record]:
    """One entry per asset class present, in first-appearance order.

    The asset class is an exact, case-sensitive match (A16). `percent` is value / portfolio total,
    or 0 when the total is 0 (A15).
    """
    zero = Decimal("0")
    values: dict[str, Decimal] = {}
    for row in calculate_holdings(holdings):
        values[row["assetClass"]] = values.get(row["assetClass"], zero) + row["marketValue"]

    total = sum(values.values(), zero)
    return [
        {"assetClass": asset_class, "value": value, "percent": value / total if total else zero}
        for asset_class, value in values.items()
    ]

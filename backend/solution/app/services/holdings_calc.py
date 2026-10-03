"""Task 2: pure holding calculations (BRIEF.md R3 and R4).

Use Decimal arithmetic; money is rounded only when building the API response.
Percentages are fractions, not percentage points. Inputs are never modified.
"""

from collections.abc import Sequence
from copy import deepcopy
from decimal import Decimal

from app.data.repository import Record


def calculate_holdings(holdings: Sequence[Record]) -> list[Record]:
    """Calculate market value, weight, gain/loss, and day change in two passes."""
    result = deepcopy(list(holdings))
    zero = Decimal("0")
    for row in result:
        quantity = Decimal(str(row["quantity"]))
        price = Decimal(str(row["price"]))
        cost = Decimal(str(row["costBasisPerShare"]))
        previous_close = Decimal(str(row["previousClosePrice"]))
        row["marketValue"] = quantity * price
        row["unrealizedGainLoss"] = (price - cost) * quantity
        row["dayChangeAmount"] = (price - previous_close) * quantity
        if quantity == zero:
            row["dayChangePercent"] = zero
        elif previous_close == zero:
            row["dayChangePercent"] = None
        else:
            row["dayChangePercent"] = (price - previous_close) / previous_close

    total = sum((row["marketValue"] for row in result), zero)
    for row in result:
        row["weightPercent"] = row["marketValue"] / total if total != zero else zero
    return result

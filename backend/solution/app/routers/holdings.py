"""Task 2: holdings from local seed data, valued at request time."""

from decimal import Decimal

from fastapi import APIRouter

from app.data import repository
from app.errors import ApiError
from app.schemas import ErrorResponse, HoldingResponse
from app.services.holdings_calc import calculate_holdings

router = APIRouter(tags=["holdings"])
_MONEY_FIELDS = (
    "costBasisPerShare",
    "price",
    "previousClosePrice",
    "marketValue",
    "unrealizedGainLoss",
    "dayChangeAmount",
)


def to_response(row: repository.Record) -> HoldingResponse:
    """Round money only at the response boundary; keep fractional percentages."""
    data = dict(row)
    for field in _MONEY_FIELDS:
        data[field] = float(round(Decimal(str(data[field])), 2))
    return HoldingResponse.model_validate(data)


@router.get(
    "/portfolios/{portfolio_id}/holdings",
    response_model=list[HoldingResponse],
    responses={404: {"model": ErrorResponse}},
)
async def get_holdings(portfolio_id: str) -> list[HoldingResponse]:
    if repository.get_portfolio(portfolio_id) is None:
        raise ApiError(404, "not_found", f"Portfolio {portfolio_id} not found")
    rows = calculate_holdings(repository.list_holdings(portfolio_id))
    return [to_response(row) for row in rows]

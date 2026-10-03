"""Task 5: GET /portfolios/{id}/allocation, from local seed data."""

from fastapi import APIRouter

from app.data import repository
from app.errors import ApiError
from app.schemas import AllocationEntry, ErrorResponse
from app.services.allocation import allocate

router = APIRouter(tags=["allocation"])


@router.get(
    "/portfolios/{portfolio_id}/allocation",
    response_model=list[AllocationEntry],
    responses={404: {"model": ErrorResponse}},
)
async def get_allocation(portfolio_id: str) -> list[AllocationEntry]:
    if repository.get_portfolio(portfolio_id) is None:
        raise ApiError(404, "not_found", f"Portfolio {portfolio_id} not found")
    return [
        AllocationEntry(
            asset_class=entry["assetClass"],
            value=float(round(entry["value"], 2)),
            percent=float(entry["percent"]),
        )
        for entry in allocate(repository.list_holdings(portfolio_id))
    ]

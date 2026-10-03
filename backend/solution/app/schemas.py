"""Shared Pydantic models. Owners add their response models here.

Extend CamelModel: fields are snake_case in Python and camelCase in JSON. FastAPI serialises
response_model output by alias, so `market_value` goes out as `marketValue`.
"""

import datetime as dt

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ErrorResponse(BaseModel):
    """Every error body: {"error": "<code>", "message": "<text>"}."""

    error: str
    message: str


class HealthResponse(BaseModel):
    status: str


class HistoryPoint(CamelModel):
    """One daily snapshot in GET /portfolios/{id}/performance-history (Task 3)."""

    date: dt.date
    market_value: float


# Task 1 · GET /portfolios/{id} (owner: me). Values the CRM leaves out are None, never 0 (A3).
class PortfolioMetadata(CamelModel):
    portfolio_id: str
    client_id: str | None
    label: str | None
    currency: str | None
    total_market_value: float | None
    day_change_amount: float | None
    day_change_percent: float | None
    total_return_since_inception: float | None
    as_of: str | None


class PortfolioResponse(PortfolioMetadata):
    stale: bool
    cached_at: str


class HoldingResponse(CamelModel):
    """Task 2: position metadata and server-calculated valuation."""

    ticker: str
    name: str
    asset_class: str
    quantity: float
    cost_basis_per_share: float
    price: float
    previous_close_price: float
    market_value: float
    weight_percent: float
    unrealized_gain_loss: float
    day_change_amount: float
    day_change_percent: float | None

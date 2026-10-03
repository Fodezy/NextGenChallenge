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

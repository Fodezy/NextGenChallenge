"""FastAPI app: error handlers, router registration, /health.

Shared file: owners add ONE line per router in create_app(), nothing else.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.data import repository
from app.errors import register_error_handlers
from app.routers import history
from app.schemas import ErrorResponse, HealthResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    repository.load()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Portfolio API",
        lifespan=lifespan,
        responses={"default": {"model": ErrorResponse}},
    )
    register_error_handlers(app)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # Routers: one line each (import at the top), e.g.
    # app.include_router(portfolios.router)
    # app.include_router(holdings.router)
    app.include_router(history.router)
    # app.include_router(allocation.router)

    return app


app = create_app()

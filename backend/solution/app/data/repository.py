"""In-memory read access to backend/fixtures/seed.json and performance-history.json.

Data is loaded once (at app startup, or on first use) and returned as plain dicts with the
seed's camelCase keys. Results are copies, so callers may mutate them freely.
"""

import copy
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# backend/solution/app/data/repository.py -> backend/fixtures (independent of the CWD)
FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures"
SEED_PATH = FIXTURES_DIR / "seed.json"
HISTORY_PATH = FIXTURES_DIR / "performance-history.json"

Record = dict[str, Any]


@lru_cache(maxsize=1)
def _seed() -> dict[str, Any]:
    with SEED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _history() -> dict[str, list[Record]]:
    """{portfolioId: [{"date": "YYYY-MM-DD", "marketValue": float}, ...]} or {} if missing."""
    if not HISTORY_PATH.exists():
        logger.warning(
            "%s missing, history is empty. Run: node backend/fixtures/generate-history.mjs",
            HISTORY_PATH.name,
        )
        return {}
    with HISTORY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load() -> None:
    """Load both files now (called from the app lifespan)."""
    _seed()
    _history()


def reload() -> None:
    """Drop cached data, e.g. after regenerating the history file or in tests."""
    _seed.cache_clear()
    _history.cache_clear()


def _find(collection: str, key: str, value: str) -> Record | None:
    for item in _seed()[collection]:
        if item[key] == value:
            return copy.deepcopy(item)
    return None


def get_client(client_id: str) -> Record | None:
    return _find("clients", "clientId", client_id)


def get_portfolio(portfolio_id: str) -> Record | None:
    return _find("portfolios", "portfolioId", portfolio_id)


def list_portfolios_for_client(client_id: str) -> list[Record]:
    return [copy.deepcopy(p) for p in _seed()["portfolios"] if p["clientId"] == client_id]


def list_holdings(portfolio_id: str) -> list[Record]:
    """Raw seed holdings (quantity, costBasisPerShare, price, previousClosePrice, ...)."""
    return [copy.deepcopy(h) for h in _seed()["holdings"] if h["portfolioId"] == portfolio_id]


def get_holding_detail(ticker: str) -> Record | None:
    return _find("holdingDetails", "ticker", ticker)


def list_transactions(holding_id: str) -> list[Record]:
    return [copy.deepcopy(t) for t in _seed()["transactions"] if t["holdingId"] == holding_id]


def cad_to_usd() -> float:
    return float(_seed()["CADtoUSD"])


def performance_history(portfolio_id: str) -> list[Record]:
    """[{"date": "YYYY-MM-DD", "marketValue": float}], oldest first; [] if unknown or no file."""
    return copy.deepcopy(_history().get(portfolio_id, []))

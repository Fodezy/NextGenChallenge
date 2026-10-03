"""Settings from environment variables, with defaults for local development."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    port: int
    crm_base_url: str
    crm_timeout_seconds: float
    api_token: str
    cache_ttl_seconds: float


@lru_cache
def get_settings() -> Settings:
    return Settings(
        port=int(os.getenv("PORT", "3000")),
        crm_base_url=os.getenv("CRM_BASE_URL", "http://127.0.0.1:4002").rstrip("/"),
        crm_timeout_seconds=float(os.getenv("CRM_TIMEOUT_SECONDS", "2.0")),
        api_token=os.getenv("API_TOKEN", "superday-demo-token"),
        cache_ttl_seconds=float(os.getenv("CACHE_TTL_SECONDS", "30")),
    )

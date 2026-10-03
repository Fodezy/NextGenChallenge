"""Task 9 · R8: an in-memory TTL cache keyed by portfolio id. Pure: time comes from `clock`.

Copies are never evicted for age: an expired copy is the stale fallback when the CRM is down
(A12). One clock drives both freshness and the stored timestamp (`cachedAt`), so tests control
both without sleeping.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class CacheEntry:
    value: Any
    stored_at: datetime


class TtlCache:
    def __init__(self, ttl_seconds: float, clock: Callable[[], datetime] = utc_now) -> None:
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: dict[str, CacheEntry] = {}

    def get_fresh(self, key: str) -> CacheEntry | None:
        """The copy for `key` if it is younger than the TTL, else None."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        age = (self._clock() - entry.stored_at).total_seconds()
        return entry if age < self.ttl_seconds else None

    def get_any(self, key: str) -> CacheEntry | None:
        """The copy for `key` however old it is (the stale fallback)."""
        return self._entries.get(key)

    def set(self, key: str, value: Any) -> CacheEntry:
        """Store `value`, replacing any older copy; its age starts from now."""
        entry = CacheEntry(value=value, stored_at=self._clock())
        self._entries[key] = entry
        return entry

    def delete(self, key: str) -> None:
        self._entries.pop(key, None)

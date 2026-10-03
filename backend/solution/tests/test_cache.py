"""Task 9 · R8: the TTL cache on its own (pure, fake clock)."""

from datetime import timedelta

from app.services.cache import TtlCache
from tests.fake_clock import START, FakeClock


def _cache() -> tuple[TtlCache, FakeClock]:
    clock = FakeClock()
    return TtlCache(ttl_seconds=30, clock=clock), clock


def test_copy_is_fresh_while_under_the_ttl():
    cache, clock = _cache()
    cache.set("P-9001", "v1")
    clock.advance(29.999)

    entry = cache.get_fresh("P-9001")

    assert entry is not None
    assert entry.value == "v1"
    assert entry.stored_at == START


def test_copy_is_expired_at_exactly_the_ttl():
    cache, clock = _cache()
    cache.set("P-9001", "v1")
    clock.advance(30)

    assert cache.get_fresh("P-9001") is None


def test_expired_copy_is_still_available_as_a_fallback():
    cache, clock = _cache()
    cache.set("P-9001", "v1")
    clock.advance(3600)

    entry = cache.get_any("P-9001")

    assert entry is not None
    assert entry.value == "v1"
    assert entry.stored_at == START


def test_copies_are_per_id():
    cache, _ = _cache()
    cache.set("P-9001", "v1")

    assert cache.get_fresh("P-9002") is None
    assert cache.get_any("P-9002") is None


def test_saving_again_replaces_the_copy_and_resets_its_age():
    cache, clock = _cache()
    cache.set("P-9001", "v1")
    clock.advance(25)
    cache.set("P-9001", "v2")
    clock.advance(25)

    entry = cache.get_fresh("P-9001")

    assert entry is not None
    assert entry.value == "v2"
    assert entry.stored_at == START + timedelta(seconds=25)


def test_a_copy_can_be_removed_and_removing_a_missing_one_is_harmless():
    cache, _ = _cache()
    cache.set("P-9001", "v1")

    cache.delete("P-9001")
    cache.delete("P-9001")

    assert cache.get_any("P-9001") is None

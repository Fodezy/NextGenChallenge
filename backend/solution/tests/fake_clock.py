"""A clock tests move by hand, so TTL tests never sleep."""

from datetime import UTC, datetime, timedelta

START = datetime(2026, 10, 3, 10, 0, 0, tzinfo=UTC)


class FakeClock:
    def __init__(self, start: datetime = START) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)

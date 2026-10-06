"""Injectable clocks. Production uses the system clock. Tests pass scripted times."""

from datetime import datetime, timedelta, timezone


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def format_time(value: datetime) -> str:
    return as_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class ScriptedClock:
    """Return queued timestamps, or successive seconds from a start time.

    A queued clock that runs out repeats its last timestamp so a long command
    script still stays deterministic.
    """

    def __init__(
        self,
        times: list[datetime] | None = None,
        start: datetime | None = None,
    ) -> None:
        if times is not None:
            self._times = [as_utc(item) for item in times]
            self._index = 0
            self._start = None
        else:
            self._times = None
            self._start = as_utc(start or datetime(2026, 10, 6, tzinfo=timezone.utc))
            self._index = 0

    def now(self) -> datetime:
        if self._times is not None:
            if not self._times:
                raise RuntimeError("ScriptedClock has no timestamps")
            if self._index >= len(self._times):
                return self._times[-1]
            current = self._times[self._index]
            self._index += 1
            return current
        assert self._start is not None
        current = self._start + timedelta(seconds=self._index)
        self._index += 1
        return current

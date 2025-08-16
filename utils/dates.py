from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime

    def as_iso(self) -> dict[str, str]:
        return {"start": self.start.isoformat(), "end": self.end.isoformat()}


def now_utc_naive() -> datetime:
    return datetime.utcnow().replace(tzinfo=None)


def _midnight_utc(d: datetime) -> datetime:
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day_exclusive(d: datetime) -> datetime:
    if d.time() == time(0, 0, 0, 0):
        return d.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return d + timedelta(microseconds=1)


def current_window(period: str, ref: datetime | None = None) -> tuple[datetime, datetime]:
    base = _midnight_utc(ref or now_utc_naive())
    p = (period or "").lower()

    if p == "weekly":
        start = base - timedelta(days=base.weekday())
        end = start + timedelta(days=7)
        return start, end

    if p == "monthly":
        start = base.replace(day=1)
        next_month = start.replace(
            year=start.year + (start.month == 12),
            month=1 if start.month == 12 else start.month + 1,
        )
        end = next_month
        return start, end

    if p == "yearly":
        start = base.replace(month=1, day=1)
        end = start.replace(year=start.year + 1)
        return start, end

    raise ValueError("period must be one of: weekly, monthly, yearly")


def window_for_period(
    period: str,
    ref: datetime | None = None,
    now: datetime | None = None,
) -> Window:
    if now is not None and ref is None:
        ref = now
    start, end = current_window(period, ref)
    return Window(start=start, end=end)

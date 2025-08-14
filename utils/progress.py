from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func

from ..extensions import db
from ..models import Goal, WorkoutSession
from .dates import now_utc_naive, window_for_period


def _session_datetime_col():
    candidates = [
        "created_at",
        "timestamp",
        "datetime",
        "date",
        "performed_at",
        "started_at",
        "time",
        "session_time",
    ]
    for name in candidates:
        col = getattr(WorkoutSession, name, None)
        if col is not None:
            return col

    msg = (
        "Nie znaleziono kolumny daty w WorkoutSession. "
        "Dodaj jedną z kolumn: "
        "created_at/timestamp/datetime/date/performed_at/started_at/time/session_time "
        "albo dopasuj listę w utils/progress.py:_session_datetime_col()."
    )
    raise AttributeError(msg)


@dataclass(frozen=True)
class Progress:
    value: int
    target: int
    percent: float
    remaining: int
    status: str
    window: dict

    def as_dict(self) -> dict:
        return {
            "value": self.value,
            "target": self.target,
            "percent": self.percent,
            "remaining": self.remaining,
            "status": self.status,
            "window": self.window,
        }


def _status_for_goal(goal: Goal, now) -> str:
    if getattr(goal, "start_date", None) is not None and now < goal.start_date:
        return "future"
    if getattr(goal, "end_date", None) is not None and now > goal.end_date:
        return "overdue"
    return "active"


def _aggregate_value(goal: Goal, win_start, win_end) -> int:
    dt_col = _session_datetime_col()

    filters = [
        WorkoutSession.user_id == goal.user_id,
        dt_col >= win_start,
        dt_col < win_end,
    ]
    if getattr(goal, "exercise_type_id", None):
        filters.append(WorkoutSession.exercise_type_id == goal.exercise_type_id)

    metric = (goal.metric or "").lower()

    if metric == "duration":
        duration_col = getattr(WorkoutSession, "duration", None) or getattr(
            WorkoutSession, "minutes", None
        )
        if duration_col is None:
            raise AttributeError("WorkoutSession musi mieć kolumnę 'duration' lub 'minutes'.")
        dur_sum = func.coalesce(func.sum(duration_col), 0)
        total = db.session.query(dur_sum).filter(*filters).scalar()
    elif metric == "calories":
        cal_sum = func.coalesce(func.sum(WorkoutSession.calories), 0)
        total = db.session.query(cal_sum).filter(*filters).scalar()
    elif metric == "sessions":
        total = db.session.query(func.count(WorkoutSession.id)).filter(*filters).scalar()
    else:
        raise ValueError(f"Unsupported metric '{goal.metric}'. Use: duration|calories|sessions.")

    return int(total or 0)


def compute_goal_progress(goal: Goal, *, now=None) -> Progress:
    now = now or now_utc_naive()
    win = window_for_period(goal.period, now=now)

    status = _status_for_goal(goal, now)
    value = _aggregate_value(goal, win.start, win.end)

    target = int(getattr(goal, "target_value", 0) or 0)
    if target <= 0:
        percent = 100.0
        remaining = 0
    else:
        percent_raw = (value / target) * 100
        percent = round(min(100.0, percent_raw), 2)
        remaining = max(0, target - value)

    if status == "active" and target > 0 and value >= target:
        status = "achieved"

    return Progress(
        value=value,
        target=target,
        percent=percent,
        remaining=remaining,
        status=status,
        window=win.as_iso(),
    )
